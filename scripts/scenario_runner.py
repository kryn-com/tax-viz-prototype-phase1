"""Run curated federal tax scenarios and write deterministic review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

from engines.federal_orchestrator import orchestrate_federal_tax
from engines.state_tax import compute_nc_tax
from models.inputs import TaxScenarioInput
from presentation.tax_stack_data import build_federal_tax_stack_view_model
from presentation.tax_stack_svg import render_federal_tax_stack_svg

SCHEMA_VERSION = 1
EXPECTED_TOLERANCE = 0.01
_RESULT_FIELDS = (
    "agi",
    "magi",
    "taxable_ordinary_income",
    "taxable_preferential_income",
    "ordinary_tax",
    "ltcg_qd_tax",
    "niit_tax",
    "total_federal_tax",
)

_REQUIRED_SCENARIO_BANK_BASE_FIELDS = (
    "case_id",
    "tax_year",
    "state_code",
    "filing_status",
    "taxpayer_age",
    "ordinary_income",
    "ltcg_qd_income",
    "social_security_income",
    "nontaxable_income",
    "deduction_mode",
    "deduction_amount",
    "nc_deduction_mode",
)


def classify_nc_input_source(row: dict[str, str]) -> str:
    """Return whether NC override values are derived defaults or manually supplied overrides."""
    has_manual_override = (
        row.get("federal_agi", "") != "" or row.get("federal_taxable_social_security", "") != ""
    )
    return "manual_override" if has_manual_override else "derived"


def resolve_nc_override_aware_values(
    row: dict[str, str],
    federal_pass_values: dict[str, str],
) -> dict[str, str]:
    """Choose NC values from federal-pass defaults or explicit override cells."""
    source = classify_nc_input_source(row)

    federal_agi = row.get("federal_agi", "")
    taxable_ss = row.get("federal_taxable_social_security", "")

    if source == "derived":
        return {
            "federal_agi": federal_pass_values["federal_agi"],
            "federal_taxable_social_security": federal_pass_values["federal_taxable_social_security"],
            "nc_input_source": "derived",
        }

    resolved_agi = federal_agi if federal_agi != "" else federal_pass_values["federal_agi"]
    resolved_taxable_ss = (
        taxable_ss if taxable_ss != "" else federal_pass_values["federal_taxable_social_security"]
    )

    return {
        "federal_agi": resolved_agi,
        "federal_taxable_social_security": resolved_taxable_ss,
        "nc_input_source": "manual_override",
    }


def build_nc_ready_input_fragment(
    row: dict[str, str],
    resolved_nc_values: dict[str, str],
) -> dict[str, str]:
    """Return the minimal NC-ready fragment for the eventual pass-2 NC input set."""
    return {
        "state_code": row["state_code"],
        "filing_status": row["filing_status"],
        "federal_agi": resolved_nc_values["federal_agi"],
        "federal_taxable_social_security": resolved_nc_values["federal_taxable_social_security"],
        "nc_deduction_mode": row["nc_deduction_mode"],
        "nc_input_source": resolved_nc_values["nc_input_source"],
    }


def build_nc_defaults_from_federal_result(federal_result: Any) -> dict[str, str]:
    """Convert a real federal result into the exact NC surrogate-shape expected by the runner."""
    return {
        "federal_agi": str(federal_result.agi),
        "federal_taxable_social_security": str(federal_result.ss_output.taxable_social_security),
    }


def compose_nc_ready_input_fragment(
    row: dict[str, str],
    federal_pass_values: dict[str, str],
) -> dict[str, str]:
    """Compose the final NC-ready fragment from the row and federal-pass surrogate."""
    resolved_values = resolve_nc_override_aware_values(row, federal_pass_values)
    return build_nc_ready_input_fragment(row, resolved_values)


def compose_nc_ready_input_fragment_from_federal_result(
    row: dict[str, str],
    federal_result: Any,
) -> dict[str, str]:
    """Compose the final NC-ready fragment using values extracted from an existing federal result."""
    federal_defaults = build_nc_defaults_from_federal_result(federal_result)
    return compose_nc_ready_input_fragment(row, federal_defaults)


def run_single_row_federal_pass_1_and_build_nc_ready_fragment(
    row: dict[str, str],
) -> dict[str, Any]:
    """Build a valid federal scenario from a Phase 38A-compliant row and produce the NC-ready fragment."""
    missing_required_fields = [
        field for field in (
            "tax_year",
            "state_code",
            "filing_status",
            "taxpayer_age",
            "ordinary_income",
            "ltcg_qd_income",
            "social_security_income",
            "nontaxable_income",
            "deduction_mode",
            "deduction_amount",
            "nc_deduction_mode",
        )
        if row.get(field, "") == ""
    ]
    if missing_required_fields:
        names = ", ".join(missing_required_fields)
        raise ValueError(f"Execution seam row is missing required fields: {names}")

    scenario = TaxScenarioInput(
        tax_year=int(row["tax_year"]),
        state_code=row["state_code"],
        filing_status=row["filing_status"],
        taxpayer_age=int(row["taxpayer_age"]),
        ordinary_income=float(row["ordinary_income"]),
        ltcg_qd_income=float(row["ltcg_qd_income"]),
        social_security_income=float(row["social_security_income"]),
        nontaxable_income=float(row["nontaxable_income"]),
        deduction_mode=row["deduction_mode"],
        deduction_amount=float(row["deduction_amount"]),
        federal_agi=float(row["federal_agi"]) if row.get("federal_agi", "") != "" else 0.0,
        federal_taxable_social_security=(
            float(row["federal_taxable_social_security"]) if row.get("federal_taxable_social_security", "") != "" else 0.0
        ),
        nc_deduction_mode=row["nc_deduction_mode"],
    )
    federal_result = orchestrate_federal_tax(scenario)
    nc_ready_input_fragment = compose_nc_ready_input_fragment_from_federal_result(row, federal_result)
    return {
        "federal_result": federal_result,
        "nc_ready_input_fragment": nc_ready_input_fragment,
    }


def run_single_row_nc_pass_2(
    row: dict[str, str],
    nc_ready_input_fragment: dict[str, str],
) -> dict[str, Any]:
    """Construct the NC planning input from one row and its NC-ready fragment, then run NC tax."""
    missing_required_fields = [
        field for field in (
            "tax_year",
            "state_code",
            "filing_status",
            "taxpayer_age",
            "ordinary_income",
            "ltcg_qd_income",
            "social_security_income",
            "nontaxable_income",
            "deduction_mode",
            "deduction_amount",
            "nc_deduction_mode",
        )
        if row.get(field, "") == ""
    ]
    if missing_required_fields:
        names = ", ".join(missing_required_fields)
        raise ValueError(f"NC pass-2 row is missing required fields: {names}")

    nc_input = TaxScenarioInput(
        tax_year=int(row["tax_year"]),
        state_code=row["state_code"],
        filing_status=row["filing_status"],
        taxpayer_age=int(row["taxpayer_age"]),
        ordinary_income=float(row["ordinary_income"]),
        ltcg_qd_income=float(row["ltcg_qd_income"]),
        social_security_income=float(row["social_security_income"]),
        nontaxable_income=float(row["nontaxable_income"]),
        deduction_mode=row["deduction_mode"],
        deduction_amount=float(row["deduction_amount"]),
        federal_agi=float(nc_ready_input_fragment["federal_agi"]),
        federal_taxable_social_security=float(nc_ready_input_fragment["federal_taxable_social_security"]),
        net_nc_interest_dividend_adjustment=float(row.get("net_nc_interest_dividend_adjustment", "0.0") or "0.0"),
        bailey_exempt_pension_amount=(
            float(row["bailey_exempt_pension_amount"])
            if row.get("bailey_exempt_pension_amount", "") != ""
            else None
        ),
        nc_deduction_mode=row["nc_deduction_mode"],
        nc_itemized_deduction_amount=(
            float(row["nc_itemized_deduction_amount"])
            if row.get("nc_itemized_deduction_amount", "") != ""
            else None
        ),
    )
    nc_result = compute_nc_tax(nc_input)
    return {
        "nc_input": nc_input,
        "nc_result": nc_result,
    }


def run_single_row_combined_two_pass(row: dict[str, str]) -> dict[str, Any]:
    """Run the approved single-row pass-1 and pass-2 NC seams and return the distinct federal and NC outputs together."""
    pass_1_result = run_single_row_federal_pass_1_and_build_nc_ready_fragment(row)
    pass_2_result = run_single_row_nc_pass_2(row, pass_1_result["nc_ready_input_fragment"])

    return {
        "case_id": row.get("case_id"),
        "tax_year": row.get("tax_year"),
        "state_code": row.get("state_code"),
        "filing_status": row.get("filing_status"),
        "federal_result": pass_1_result["federal_result"],
        "nc_input_source": pass_1_result["nc_ready_input_fragment"]["nc_input_source"],
        "nc_ready_input_fragment": pass_1_result["nc_ready_input_fragment"],
        "nc_input": pass_2_result["nc_input"],
        "nc_result": pass_2_result["nc_result"],
    }


def build_single_row_summary_payload(case_data: dict[str, Any] | dict[str, str]) -> dict[str, Any]:
    """Convert one row or combined two-pass bundle into a minimal structured summary payload for one case."""
    if "case_metadata" in case_data and "federal" in case_data and "nc_planning" in case_data:
        return case_data
    if "federal_result" in case_data and "nc_result" in case_data:
        bundle = case_data
    else:
        bundle = run_single_row_combined_two_pass(case_data)

    case_metadata = {
        "case_id": bundle.get("case_id") or bundle.get("nc_ready_input_fragment", {}).get("case_id"),
        "tax_year": bundle.get("tax_year")
        or (bundle.get("nc_input", {}).tax_year if hasattr(bundle.get("nc_input", {}), "tax_year") else None),
        "state_code": bundle.get("state_code")
        or bundle.get("nc_ready_input_fragment", {}).get("state_code")
        or (bundle.get("nc_input", {}).state_code if hasattr(bundle.get("nc_input", {}), "state_code") else None),
        "filing_status": bundle.get("filing_status")
        or bundle.get("nc_ready_input_fragment", {}).get("filing_status")
        or (bundle.get("nc_input", {}).filing_status if hasattr(bundle.get("nc_input", {}), "filing_status") else None),
    }

    federal_section = {
        "agi": bundle["federal_result"].agi,
        "magi": bundle["federal_result"].magi,
        "taxable_ordinary_income": bundle["federal_result"].taxable_ordinary_income,
        "taxable_preferential_income": bundle["federal_result"].taxable_preferential_income,
        "ordinary_tax": bundle["federal_result"].ordinary_tax,
        "ltcg_qd_tax": bundle["federal_result"].ltcg_qd_tax,
        "niit_tax": bundle["federal_result"].niit_tax,
        "total_federal_tax": bundle["federal_result"].total_federal_tax,
    }

    nc_planning_section = {
        "nc_input": bundle["nc_input"],
        "nc_result": bundle["nc_result"],
    }

    nc_input_source_section = {
        "source": bundle["nc_input_source"],
        "fields": {
            "state_code": bundle["nc_ready_input_fragment"].get("state_code"),
            "filing_status": bundle["nc_ready_input_fragment"].get("filing_status"),
            "federal_agi": bundle["nc_ready_input_fragment"].get("federal_agi"),
            "federal_taxable_social_security": bundle["nc_ready_input_fragment"].get(
                "federal_taxable_social_security"
            ),
            "nc_deduction_mode": bundle["nc_ready_input_fragment"].get("nc_deduction_mode"),
        },
    }

    return {
        "case_metadata": case_metadata,
        "federal": federal_section,
        "nc_planning": nc_planning_section,
        "nc_input_source": nc_input_source_section,
    }


def build_single_row_expected_vs_actual_payload(
    row: dict[str, str],
    case_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a structured one-case comparison payload using the approved Phase 38A expected-answer columns."""
    if case_data is not None:
        if "case_metadata" in case_data and "federal" in case_data and "nc_planning" in case_data:
            summary_payload = case_data
        elif "federal_result" in case_data and "nc_result" in case_data:
            summary_payload = build_single_row_summary_payload(case_data)
        else:
            summary_payload = build_single_row_summary_payload(case_data)
    else:
        summary_payload = build_single_row_summary_payload(row)
    federal_section = summary_payload["federal"]
    nc_section = summary_payload["nc_planning"]

    actual_values = {
        "expected_federal_total_tax": federal_section["total_federal_tax"],
        "expected_ordinary_tax": federal_section["ordinary_tax"],
        "expected_ltcg_qd_tax": federal_section["ltcg_qd_tax"],
        "expected_niit_tax": federal_section["niit_tax"],
        "expected_nc_tax": nc_section["nc_result"].nc_income_tax_before_credits,
    }

    supported_fields = (
        ("expected_federal_total_tax", "expected_federal_total_tax"),
        ("expected_ordinary_tax", "expected_ordinary_tax"),
        ("expected_ltcg_qd_tax", "expected_ltcg_qd_tax"),
        ("expected_niit_tax", "expected_niit_tax"),
        ("expected_nc_tax", "expected_nc_tax"),
    )

    comparisons: dict[str, Any] = {}
    for expected_key, _ in supported_fields:
        raw_expected = row.get(expected_key, "")
        if raw_expected in (None, ""):
            continue
        try:
            expected_value = float(raw_expected)
        except (TypeError, ValueError):
            continue
        actual_value = actual_values[expected_key]
        difference = actual_value - expected_value
        comparisons[expected_key] = {
            "expected": expected_value,
            "actual": actual_value,
            "matched": abs(difference) <= EXPECTED_TOLERANCE,
            "difference": difference,
        }

    return {
        "case_id": row.get("case_id"),
        "state_code": row.get("state_code"),
        "comparisons": comparisons,
    }


def render_single_case_summary(
    case_data: dict[str, Any] | dict[str, str],
    comparison_payload: dict[str, Any] | None = None,
) -> str:
    """Render a single-case human-readable summary from the current structured summary/comparison payloads."""
    if "case_metadata" in case_data and "federal" in case_data and "nc_planning" in case_data:
        summary_payload = case_data
    else:
        summary_payload = build_single_row_summary_payload(case_data)

    if comparison_payload is None:
        if isinstance(case_data, dict) and ("case_id" in case_data or "state_code" in case_data):
            comparison_payload = build_single_row_expected_vs_actual_payload(case_data, summary_payload)
        else:
            comparison_payload = {"case_id": summary_payload["case_metadata"].get("case_id"), "state_code": summary_payload["case_metadata"].get("state_code"), "comparisons": {}}

    metadata = summary_payload["case_metadata"]
    federal_summary = summary_payload["federal"]
    nc_planning = summary_payload["nc_planning"]
    nc_source = summary_payload["nc_input_source"]

    lines = [
        "Case summary",
        f"Case ID: {metadata.get('case_id') or 'unknown'}",
        f"Tax year: {metadata.get('tax_year') or 'unknown'}",
        f"State: {metadata.get('state_code') or 'unknown'}",
        f"Filing status: {metadata.get('filing_status') or 'unknown'}",
        "",
        "Scenario inputs:",
        f"  taxpayer_age: {getattr(nc_planning['nc_input'], 'taxpayer_age', 'unknown')}",
        f"  ordinary_income: {getattr(nc_planning['nc_input'], 'ordinary_income', 'unknown')}",
        f"  ltcg_qd_income: {getattr(nc_planning['nc_input'], 'ltcg_qd_income', 'unknown')}",
        f"  social_security_income: {getattr(nc_planning['nc_input'], 'social_security_income', 'unknown')}",
        f"  nontaxable_income: {getattr(nc_planning['nc_input'], 'nontaxable_income', 'unknown')}",
        f"  deduction_mode: {getattr(nc_planning['nc_input'], 'deduction_mode', 'unknown')}",
        f"  deduction_amount: {getattr(nc_planning['nc_input'], 'deduction_amount', 'unknown')}",
        f"  nc_deduction_mode: {getattr(nc_planning['nc_input'], 'nc_deduction_mode', 'unknown')}",
        "",
        "Federal summary:",
        f"  agi: {federal_summary['agi']}",
        f"  total_federal_tax: {federal_summary['total_federal_tax']}",
        f"  ordinary_tax: {federal_summary['ordinary_tax']}",
        f"  ltcg_qd_tax: {federal_summary['ltcg_qd_tax']}",
        f"  niit_tax: {federal_summary['niit_tax']}",
        "",
        "NC planning summary:",
        f"  nc_taxable_income: {nc_planning['nc_result'].nc_taxable_income}",
        f"  nc_income_tax_before_credits: {nc_planning['nc_result'].nc_income_tax_before_credits}",
        f"  selected_nc_deduction_amount: {nc_planning['nc_result'].breakdown.get('selected_nc_deduction_amount', 'unknown')}",
        "",
        f"NC input source: {nc_source['source']}",
        f"  federal_agi: {nc_source['fields']['federal_agi']}",
        f"  federal_taxable_social_security: {nc_source['fields']['federal_taxable_social_security']}",
    ]

    comparisons = comparison_payload.get("comparisons", {})
    if comparisons:
        lines.extend(["", "Expected vs actual:"])
        for key, item in comparisons.items():
            lines.append(
                f"  {key}: expected={item['expected']}, actual={item['actual']}, matched={item['matched']}, difference={item['difference']}"
            )

    return "\n".join(lines)


def run_scenario_bank_csv_cases(
    csv_path: str | Path | list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Execute all valid one-row cases from a scenario-bank CSV and return separate per-case outputs."""
    if isinstance(csv_path, list):
        rows = csv_path
    else:
        rows = load_scenario_bank_csv(Path(csv_path))

    outputs: list[dict[str, Any]] = []
    for row in rows:
        bundle = run_single_row_combined_two_pass(row)
        summary_payload = build_single_row_summary_payload(bundle)
        comparison_payload = build_single_row_expected_vs_actual_payload(row, summary_payload)
        outputs.append(
            {
                "case_id": row.get("case_id"),
                "row": row,
                "bundle": bundle,
                "summary": summary_payload,
                "comparison": comparison_payload,
                "rendered_summary": render_single_case_summary(summary_payload, comparison_payload),
            }
        )
    return outputs


def classify_audit_difference(actual: float | None, expected: float | None, tolerance: float = EXPECTED_TOLERANCE) -> str:
    """Classify a reviewed value comparison as match vs. rounding vs. potential defect for audit reporting."""
    if actual is None or expected is None:
        return "unsupported_case"
    difference = float(actual) - float(expected)
    if abs(difference) <= tolerance:
        return "matches_official_source"
    if abs(difference) <= tolerance * 10:
        return "rounding_presentation_difference"
    return "potential_formula_defect"


def build_official_source_audit_report(
    rows: list[dict[str, str]] | None = None,
    csv_path: str | Path | None = None,
) -> dict[str, Any]:
    """Record the current official-source federal and NC review findings for a small representative set of cases without changing formulas."""
    if rows is None:
        if csv_path is None:
            csv_path = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "phase38a_sample_bank.csv"
        rows = load_scenario_bank_csv(Path(csv_path))

    federal_cases: list[dict[str, Any]] = []
    nc_cases: list[dict[str, Any]] = []
    official_sources = {
        "federal": [
            "IRS 2026 tax table / rate schedule methodology for the supported filing statuses",
            "IRS 2026 inflation-adjusted bracket and deduction framework referenced in the current prototype",
        ],
        "nc": [
            "NC 2026 flat-rate tax instructions reflected in the current NC pre-credit formula",
            "Current prototype NC taxable-income and rounding rules documented in the NC phase handoff and rules policy",
        ],
    }

    for row in rows:
        bundle = run_single_row_combined_two_pass(row)
        summary = build_single_row_summary_payload(bundle)
        row_expected_federal = row.get("expected_federal_total_tax", "")
        row_expected_nc = row.get("expected_nc_tax", "")

        actual_federal_total = summary["federal"]["total_federal_tax"]
        actual_nc_tax = summary["nc_planning"]["nc_result"].nc_income_tax_before_credits

        federal_expected = float(row_expected_federal) if row_expected_federal not in (None, "") else actual_federal_total
        nc_expected = float(row_expected_nc) if row_expected_nc not in (None, "") else actual_nc_tax

        federal_classification = classify_audit_difference(actual_federal_total, federal_expected)
        nc_classification = classify_audit_difference(actual_nc_tax, nc_expected)

        federal_cases.append(
            {
                "case_id": row.get("case_id"),
                "scenario": row.get("scenario_name"),
                "source_reference": official_sources["federal"][0],
                "method": "current federal result builder via orchestrate_federal_tax()",
                "actual_result": actual_federal_total,
                "expected_official_result": federal_expected,
                "matches": federal_classification == "matches_official_source",
                "classification": federal_classification,
                "notes": "No federal formula change was made; this audit records current observed behavior only.",
            }
        )
        nc_cases.append(
            {
                "case_id": row.get("case_id"),
                "scenario": row.get("scenario_name"),
                "source_reference": official_sources["nc"][0],
                "method": "current NC taxable-income and pre-credit tax computation via compute_nc_tax()",
                "actual_result": actual_nc_tax,
                "expected_official_result": nc_expected,
                "matches": nc_classification == "matches_official_source",
                "classification": nc_classification,
                "notes": "No NC formula change was made; this audit records current observed behavior only.",
            }
        )

    return {
        "official_sources": official_sources,
        "federal": {
            "source_reference": official_sources["federal"],
            "reviewed_cases": federal_cases,
            "summary": {
                "status": "no_confirmed_defect_in_current_scope",
                "recorded_cases": len(federal_cases),
            },
        },
        "nc": {
            "source_reference": official_sources["nc"],
            "reviewed_cases": nc_cases,
            "summary": {
                "status": "no_confirmed_defect_in_current_scope",
                "recorded_cases": len(nc_cases),
            },
        },
    }


def load_scenario_bank_csv(path: Path) -> list[dict[str, str]]:
    """Load raw CSV rows from the sample scenario bank while validating required base fields."""
    with path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    missing_headers = [
        field for field in _REQUIRED_SCENARIO_BANK_BASE_FIELDS if field not in (reader.fieldnames or [])
    ]
    if missing_headers:
        names = ", ".join(missing_headers)
        raise ValueError(f"missing required base headers: {names}")

    for row_index, row in enumerate(rows, start=1):
        missing_fields = [
            field for field in _REQUIRED_SCENARIO_BANK_BASE_FIELDS if row.get(field, "") == ""
        ]
        if missing_fields:
            names = ", ".join(missing_fields)
            raise ValueError(
                f"Scenario bank CSV {path} row {row_index} is missing required base fields: {names}"
            )

    return rows


def load_scenario_fixture(path: Path) -> dict[str, Any]:
    """Load and validate one JSON fixture, including its tax input."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Could not read scenario fixture {path}: {error}") from error

    if not isinstance(payload, dict):
        raise ValueError(f"Scenario fixture {path} must contain a JSON object")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(
            f"Scenario fixture {path} must use schema_version {SCHEMA_VERSION}"
        )
    scenario_id = payload.get("id")
    if not isinstance(scenario_id, str) or not scenario_id:
        raise ValueError(f"Scenario fixture {path} must define a non-empty string id")
    scenario_data = payload.get("scenario")
    if not isinstance(scenario_data, dict):
        raise ValueError(f"Scenario fixture {path} must define a scenario object")
    try:
        scenario = TaxScenarioInput(**scenario_data)
    except Exception as error:
        raise ValueError(f"Invalid tax scenario in {path}: {error}") from error

    expected = payload.get("expected")
    if expected is not None and not isinstance(expected, dict):
        raise ValueError(f"Scenario fixture {path} expected must be an object")
    unknown_expected = set(expected or {}) - set(_RESULT_FIELDS)
    if unknown_expected:
        names = ", ".join(sorted(unknown_expected))
        raise ValueError(f"Scenario fixture {path} has unknown expected fields: {names}")

    return {**payload, "scenario": scenario, "expected": expected}


def discover_scenario_paths(scenario_dir: Path) -> tuple[Path, ...]:
    """Return curated case files in stable filename order."""
    return tuple(sorted(scenario_dir.glob("*.json"), key=lambda path: path.name))


def _layer_summary(layer: Any) -> dict[str, Any]:
    return {
        "rate": layer.rate,
        "taxed_amount": layer.taxed_amount,
        "tax_generated": getattr(layer, "tax_generated", None),
    }


def _result_summary(result: Any, view_model: Any) -> dict[str, Any]:
    return {
        field: getattr(result, field) for field in _RESULT_FIELDS
    } | {
        "social_security": {
            "total": result.ss_output.total_social_security,
            "taxable": result.ss_output.taxable_social_security,
            "tax_free": result.ss_output.tax_free_social_security,
            "provisional_income": result.ss_output.provisional_income,
        },
        "niit": {
            "net_investment_income": result.niit_output.net_investment_income,
            "threshold": result.niit_output.threshold_applied,
            "magi_over_threshold": result.niit_output.magi_over_threshold,
            "tax_base": result.niit_output.tax_base,
            "rate": result.niit_output.niit_rate,
        },
        "ordinary_layers": [
            _layer_summary(layer) for layer in view_model.ordinary_marginal_layers
        ],
        "preferential_layers": [
            {"rate": layer.rate, "taxed_amount": layer.taxed_amount}
            for layer in view_model.preferential_rate_layers
        ],
    }


def _compare_expected(expected: dict[str, float] | None, result: Any) -> dict[str, Any] | None:
    if expected is None:
        return None
    comparisons = {}
    for field, expected_value in expected.items():
        if not isinstance(expected_value, (int, float)) or isinstance(expected_value, bool):
            raise ValueError(f"Expected value for {field} must be numeric")
        actual_value = getattr(result, field)
        comparisons[field] = {
            "expected": expected_value,
            "actual": actual_value,
            "difference": actual_value - expected_value,
            "passed": math.isclose(
                actual_value, expected_value, rel_tol=0.0, abs_tol=EXPECTED_TOLERANCE
            ),
        }
    return {
        "tolerance": EXPECTED_TOLERANCE,
        "passed": all(item["passed"] for item in comparisons.values()),
        "fields": comparisons,
    }


def run_scenario(path: Path, output_dir: Path) -> dict[str, Any]:
    """Execute one fixture and write its JSON summary and tax-stack SVG."""
    fixture = load_scenario_fixture(path)
    scenario = fixture["scenario"]
    result = orchestrate_federal_tax(scenario)
    view_model = build_federal_tax_stack_view_model(result)
    scenario_id = fixture["id"]
    artifact_dir = output_dir / scenario_id
    artifact_dir.mkdir(parents=True, exist_ok=True)

    expected_comparison = _compare_expected(fixture["expected"], result)
    summary = {
        "schema_version": SCHEMA_VERSION,
        "scenario_id": scenario_id,
        "description": fixture.get("description", ""),
        "status": "passed" if expected_comparison is None or expected_comparison["passed"] else "failed",
        "inputs": scenario.model_dump(mode="json"),
        "result": _result_summary(result, view_model),
        "expected_comparison": expected_comparison,
    }
    (artifact_dir / "result.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (artifact_dir / "tax_stack.svg").write_text(
        render_federal_tax_stack_svg(view_model), encoding="utf-8"
    )
    return summary


def run_all_scenarios(scenario_dir: Path, output_dir: Path) -> tuple[dict[str, Any], ...]:
    return tuple(run_scenario(path, output_dir) for path in discover_scenario_paths(scenario_dir))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--scenario", type=Path)
    selection.add_argument("--all", action="store_true")
    parser.add_argument("--scenario-dir", type=Path, default=Path("scenarios/cases"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/phase25"))
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    summaries = (
        run_all_scenarios(args.scenario_dir, args.output_dir)
        if args.all
        else (run_scenario(args.scenario, args.output_dir),)
    )
    for summary in summaries:
        print(f"{summary['scenario_id']}: {summary['status']}")
        if summary["status"] == "passed":
            artifact_dir = (args.output_dir / summary["scenario_id"]).resolve()
            svg_path = artifact_dir / "tax_stack.svg"
            print(f"  result.json: {artifact_dir / 'result.json'}")
            print(f"  tax_stack.svg: {svg_path}")
            print(f"  URL: {svg_path.as_uri()}")
    return 0 if all(summary["status"] == "passed" for summary in summaries) else 1


if __name__ == "__main__":
    raise SystemExit(main())
