"""Run curated federal tax scenarios and write deterministic review artifacts."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from engines.federal_orchestrator import orchestrate_federal_tax
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
