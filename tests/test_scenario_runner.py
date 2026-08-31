import json
from pathlib import Path
from xml.etree import ElementTree

import pytest

from scripts.scenario_runner import (
    EXPECTED_TOLERANCE,
    discover_scenario_paths,
    load_scenario_fixture,
    run_all_scenarios,
    run_scenario,
)
from scripts import scenario_runner


SCENARIO = {
    "tax_year": 2026,
    "state_code": "NC",
    "filing_status": "single",
    "taxpayer_age": 45,
    "ordinary_income": 60000.0,
    "ltcg_qd_income": 20000.0,
    "social_security_income": 30000.0,
    "nontaxable_income": 0.0,
    "deduction_mode": "standard",
    "deduction_amount": 0.0,
}

PHASE_38A_REQUIRED_BASE_INPUT_COLUMNS = frozenset({
    "case_id",
    "scenario_name",
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
    "net_nc_interest_dividend_adjustment",
    "nc_deduction_mode",
})

PHASE_38A_OPTIONAL_BASE_OR_OVERRIDE_COLUMNS = frozenset({
    "spouse_age",
    "bailey_exempt_pension_amount",
    "nc_itemized_deduction_amount",
    "federal_agi",
    "federal_taxable_social_security",
})

PHASE_38A_OPTIONAL_EXPECTED_ANSWER_COLUMNS = frozenset({
    "expected_federal_total_tax",
    "expected_ordinary_tax",
    "expected_ltcg_qd_tax",
    "expected_niit_tax",
    "expected_nc_tax",
    "expected_projected_irmaa_2028_premium",
    "expected_projected_irmaa_2028_surcharge",
    "expected_status",
    "expected_notes",
})

PHASE_38A_OPTIONAL_METADATA_STATUS_COLUMNS = frozenset({
    "status",
    "owner",
    "reviewer",
    "source",
    "tags",
    "last_run_date",
    "validation_status",
    "notes",
    "issue_id",
})


def test_phase_38a_csv_sample_bank_header_and_row_contract():
    csv_path = Path(__file__).parent / "fixtures" / "phase38a_sample_bank.csv"
    approved_order = (
        "case_id",
        "scenario_name",
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
        "net_nc_interest_dividend_adjustment",
        "nc_deduction_mode",
        "spouse_age",
        "bailey_exempt_pension_amount",
        "nc_itemized_deduction_amount",
        "federal_agi",
        "federal_taxable_social_security",
        "expected_federal_total_tax",
        "expected_ordinary_tax",
        "expected_ltcg_qd_tax",
        "expected_niit_tax",
        "expected_nc_tax",
        "expected_projected_irmaa_2028_premium",
        "expected_projected_irmaa_2028_surcharge",
        "expected_status",
        "expected_notes",
        "status",
        "owner",
        "reviewer",
        "source",
        "tags",
        "last_run_date",
        "validation_status",
        "notes",
        "issue_id",
    )

    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        import csv

        rows = list(csv.reader(csv_file))

    assert len(rows) == 2
    assert rows[0] == list(approved_order)
    assert len(rows[1]) == len(rows[0])


def write_fixture(directory: Path, name: str, **overrides) -> Path:
    payload = {
        "schema_version": 1,
        "id": name,
        "description": "Test fixture",
        "scenario": {**SCENARIO, **overrides.pop("scenario", {})},
        **overrides,
    }
    path = directory / f"{name}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_phase_38a_contract_definition_freezes_approved_column_groups():
    required = PHASE_38A_REQUIRED_BASE_INPUT_COLUMNS
    optional_override = PHASE_38A_OPTIONAL_BASE_OR_OVERRIDE_COLUMNS
    expected = PHASE_38A_OPTIONAL_EXPECTED_ANSWER_COLUMNS
    metadata = PHASE_38A_OPTIONAL_METADATA_STATUS_COLUMNS

    assert required.isdisjoint(optional_override)
    assert required.isdisjoint(expected)
    assert required.isdisjoint(metadata)
    assert optional_override.isdisjoint(expected)
    assert optional_override.isdisjoint(metadata)
    assert expected.isdisjoint(metadata)

    column_union = required | optional_override | expected | metadata
    assert len(column_union) == 37
    assert "federal_agi" in optional_override
    assert "federal_taxable_social_security" in optional_override
    assert "federal_agi" not in required
    assert "federal_taxable_social_security" not in required


def test_phase_38a_deferred_validation_boundary_is_documentation_only():
    required = PHASE_38A_REQUIRED_BASE_INPUT_COLUMNS
    optional_override = PHASE_38A_OPTIONAL_BASE_OR_OVERRIDE_COLUMNS
    expected = PHASE_38A_OPTIONAL_EXPECTED_ANSWER_COLUMNS
    metadata = PHASE_38A_OPTIONAL_METADATA_STATUS_COLUMNS
    deferred_behaviors = {
        "blank_string_normalization",
        "spreadsheet_row_parsing",
        "two_pass_derivation_behavior",
    }
    runtime_fixture_schema_keys = {
        "schema_version",
        "id",
        "description",
        "scenario",
        "expected",
    }

    assert required.isdisjoint(expected)
    assert required.isdisjoint(metadata)
    assert optional_override.isdisjoint(expected)
    assert optional_override.isdisjoint(metadata)
    assert deferred_behaviors.isdisjoint(required)
    assert deferred_behaviors.isdisjoint(optional_override)
    assert deferred_behaviors.isdisjoint(expected)
    assert deferred_behaviors.isdisjoint(metadata)
    assert deferred_behaviors.isdisjoint(runtime_fixture_schema_keys)


def test_phase_38a_audit_evidence_metadata_contract_test():
    required = PHASE_38A_REQUIRED_BASE_INPUT_COLUMNS
    optional_override = PHASE_38A_OPTIONAL_BASE_OR_OVERRIDE_COLUMNS
    expected = PHASE_38A_OPTIONAL_EXPECTED_ANSWER_COLUMNS
    metadata = PHASE_38A_OPTIONAL_METADATA_STATUS_COLUMNS
    audit_evidence_fields = frozenset({
        "source",
        "reviewer",
        "last_run_date",
        "validation_status",
        "notes",
        "issue_id",
    })

    assert audit_evidence_fields == frozenset({
        "source",
        "reviewer",
        "last_run_date",
        "validation_status",
        "notes",
        "issue_id",
    })
    assert audit_evidence_fields <= metadata
    assert audit_evidence_fields.isdisjoint(required)
    assert audit_evidence_fields.isdisjoint(optional_override)
    assert audit_evidence_fields.isdisjoint(expected)


def test_load_scenario_fixture_validates_native_tax_input():
    path = write_fixture(Path(__file__).parent, "unused")
    try:
        fixture = load_scenario_fixture(path)
    finally:
        path.unlink()

    assert fixture["id"] == "unused"
    assert fixture["scenario"].filing_status.value == "single"
    assert fixture["scenario"].ordinary_income == 60000.0


def test_load_scenario_fixture_rejects_invalid_tax_input(tmp_path):
    path = write_fixture(tmp_path, "invalid", scenario={"tax_year": 2025})

    with pytest.raises(ValueError, match="Invalid tax scenario"):
        load_scenario_fixture(path)


def test_load_scenario_fixture_accepts_valid_taxpayer_age(tmp_path):
    path = write_fixture(tmp_path, "valid-age", scenario={"taxpayer_age": 45})

    fixture = load_scenario_fixture(path)

    assert fixture["scenario"].taxpayer_age == 45


def test_load_scenario_fixture_rejects_mfj_without_spouse_age(tmp_path):
    path = write_fixture(
        tmp_path,
        "mfj-no-spouse-age",
        scenario={
            "filing_status": "married_filing_jointly",
            "taxpayer_age": 45,
            "spouse_age": None,
        },
    )

    with pytest.raises(ValueError, match="Invalid tax scenario"):
        load_scenario_fixture(path)


def test_load_scenario_fixture_rejects_invalid_taxpayer_age(tmp_path):
    path = write_fixture(tmp_path, "invalid-age", scenario={"taxpayer_age": 121})

    with pytest.raises(ValueError, match="Invalid tax scenario"):
        load_scenario_fixture(path)


def test_discover_scenario_paths_is_sorted_and_directory_scoped(tmp_path):
    write_fixture(tmp_path, "z-case")
    write_fixture(tmp_path, "a-case")
    (tmp_path / "defects.json").write_text("{}", encoding="utf-8")

    assert [path.name for path in discover_scenario_paths(tmp_path)] == [
        "a-case.json",
        "defects.json",
        "z-case.json",
    ]


def test_run_scenario_writes_deterministic_json_and_svg_artifacts(tmp_path):
    fixture_path = write_fixture(tmp_path, "artifact-case")
    first_output = tmp_path / "first"
    second_output = tmp_path / "second"

    first = run_scenario(fixture_path, first_output)
    run_scenario(fixture_path, second_output)

    first_dir = first_output / "artifact-case"
    second_dir = second_output / "artifact-case"
    assert first["status"] == "passed"
    assert (first_dir / "result.json").exists()
    assert (first_dir / "tax_stack.svg").exists()
    assert json.loads((first_dir / "result.json").read_text(encoding="utf-8"))["scenario_id"] == "artifact-case"
    assert ElementTree.fromstring((first_dir / "tax_stack.svg").read_text(encoding="utf-8")).tag.endswith("svg")
    assert (first_dir / "result.json").read_bytes() == (second_dir / "result.json").read_bytes()
    assert (first_dir / "tax_stack.svg").read_bytes() == (second_dir / "tax_stack.svg").read_bytes()


def test_run_scenario_compares_optional_expected_values_with_tolerance(tmp_path):
    path = write_fixture(
        tmp_path,
        "expected-case",
        expected={"total_federal_tax": 12980.0 + EXPECTED_TOLERANCE / 2},
    )

    summary = run_scenario(path, tmp_path / "artifacts")

    assert summary["status"] == "passed"
    assert summary["expected_comparison"]["passed"] is True
    assert summary["expected_comparison"]["tolerance"] == EXPECTED_TOLERANCE


def test_run_scenario_reports_expected_value_mismatch(tmp_path):
    path = write_fixture(
        tmp_path,
        "mismatch-case",
        expected={"total_federal_tax": 0.0},
    )

    summary = run_scenario(path, tmp_path / "artifacts")

    assert summary["status"] == "failed"
    assert summary["expected_comparison"]["fields"]["total_federal_tax"]["passed"] is False


def test_main_prints_absolute_artifact_paths_and_svg_url(tmp_path, capsys, monkeypatch):
    fixture_path = write_fixture(tmp_path, "link-case")
    output_dir = tmp_path / "artifacts"
    monkeypatch.setattr(
        "sys.argv",
        [
            "scenario_runner",
            "--scenario",
            str(fixture_path),
            "--output-dir",
            str(output_dir),
        ],
    )

    assert scenario_runner.main() == 0

    output = capsys.readouterr().out
    svg_path = (output_dir / "link-case" / "tax_stack.svg").resolve()
    assert str(svg_path) in output
    assert svg_path.as_uri() in output

def test_run_all_repository_scenarios_pass(tmp_path):
    scenario_dir = Path("scenarios/cases")
    summaries = run_all_scenarios(scenario_dir, tmp_path / "artifacts")

    scenario_ids = [summary["scenario_id"] for summary in summaries]

    assert scenario_ids == [
        "high-income-niit",
        "hoh-060k-014k-ltcg-030k-ss-standard",
        "hoh-1000k-190k-ltcg-explicit-40k",
        "hoh-188k-001k-ltcg-010k-ss-standard",
        "hoh-395k-224500-ltcg-050k-ss-standard",
        "hoh-ordinary-only",
        "mf-joint-ordinary-only",
        "mfj-040k-005k-ltcg-standard",
        "mfj-055k-055k-ltcg-explicit-30k",
        "mfj-075k-009k-ltcg-023k-ss-standard",
        "mfj-099k-044k-ltcg-030k-ss-explicit-74k",
        "mfj-1285k-158k-ltcg-standard",
        "mfj-128k-012k-ltcg-standard",
        "mfj-129k-046k-ss-standard",
        "mfj-201k-055k-ltcg-075k-ss-standard",
        "mfj-385k-068k-ltcg-021k-ss-explicit-39k",
        "single-020k-003k-ltcg-standard",
        "single-050k-011k-ltcg-015k-ss-standard",
        "single-080k-020k-ltcg-030k-ss-explicit-20k",
        "single-110k-040k-ss-explicit-40k",
        "single-190k-080k-ltcg-020k-ss-explicit-30k",
        "single-280k-030k-ltcg-standard",
        "single-800k-200k-ltcg-015k-ss-explicit-80k",
        "single-baseline",
        "zero-income",
    ]
    assert all(summary["status"] == "passed" for summary in summaries)