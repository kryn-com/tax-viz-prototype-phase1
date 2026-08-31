import json
from pathlib import Path
from xml.etree import ElementTree

import pytest

from engines.federal_orchestrator import orchestrate_federal_tax
from models.inputs import TaxScenarioInput
from scripts.scenario_runner import (
    EXPECTED_TOLERANCE,
    build_nc_defaults_from_federal_result,
    build_nc_ready_input_fragment,
    build_official_source_audit_report,
    build_single_row_expected_vs_actual_payload,
    build_single_row_summary_payload,
    classify_audit_difference,
    classify_nc_input_source,
    compose_nc_ready_input_fragment,
    compose_nc_ready_input_fragment_from_federal_result,
    discover_scenario_paths,
    load_scenario_bank_csv,
    load_scenario_fixture,
    render_single_case_summary,
    resolve_nc_override_aware_values,
    run_all_scenarios,
    run_scenario,
    run_scenario_bank_csv_cases,
    run_single_row_combined_two_pass,
    run_single_row_federal_pass_1_and_build_nc_ready_fragment,
    run_single_row_nc_pass_2,
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


def _sample_bank_row() -> dict[str, str]:
    csv_path = Path(__file__).parent / "fixtures" / "phase38a_sample_bank.csv"

    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        import csv

        rows = list(csv.DictReader(csv_file))

    assert len(rows) == 1
    return rows[0]


def test_load_scenario_bank_csv_reads_sample_bank_row_with_blank_optional_cells_preserved():
    csv_path = Path(__file__).parent / "fixtures" / "phase38a_sample_bank.csv"

    rows = load_scenario_bank_csv(csv_path)

    assert len(rows) == 1
    sample_row = rows[0]
    assert sample_row["case_id"] == "single_case_001"
    assert sample_row["federal_agi"] == ""
    assert sample_row["federal_taxable_social_security"] == ""
    assert sample_row["expected_federal_total_tax"] == ""


def test_load_scenario_bank_csv_requires_required_base_fields(tmp_path):
    csv_path = tmp_path / "invalid_required_fields.csv"
    csv_path.write_text(
        "case_id,tax_year,state_code,filing_status,taxpayer_age,ordinary_income,ltcg_qd_income,social_security_income,nontaxable_income,deduction_mode,deduction_amount,nc_deduction_mode\n"
        "single_case_001,2026,,single,45,60000,0,0,0,standard,0,standard\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing required base fields: state_code"):
        load_scenario_bank_csv(csv_path)


def test_load_scenario_bank_csv_requires_execution_ready_fields(tmp_path):
    csv_path = tmp_path / "missing_execution_ready_field.csv"
    csv_path.write_text(
        "case_id,tax_year,state_code,filing_status,taxpayer_age,ordinary_income,ltcg_qd_income,social_security_income,nontaxable_income,deduction_mode,deduction_amount,nc_deduction_mode\n"
        "single_case_001,2026,NC,single,45,60000,0,0,,standard,0,standard\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing required base fields: nontaxable_income"):
        load_scenario_bank_csv(csv_path)


def test_load_scenario_bank_csv_requires_required_base_headers(tmp_path):
    csv_path = tmp_path / "missing_required_header.csv"
    csv_path.write_text(
        "case_id,tax_year,filing_status,ordinary_income,ltcg_qd_income,social_security_income,deduction_mode,nc_deduction_mode\n"
        "single_case_001,2026,single,60000,0,0,standard,standard\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing required base headers: state_code"):
        load_scenario_bank_csv(csv_path)


def test_classify_nc_input_source_derived_when_optional_overrides_are_blank():
    row = _sample_bank_row()

    assert classify_nc_input_source(row) == "derived"


def test_classify_nc_input_source_manual_override_when_any_optional_override_is_populated():
    row = _sample_bank_row()
    row["federal_agi"] = "48000"

    assert classify_nc_input_source(row) == "manual_override"

    row["federal_agi"] = ""
    row["federal_taxable_social_security"] = "18000"
    assert classify_nc_input_source(row) == "manual_override"


def test_resolve_nc_override_aware_values_uses_surrogate_defaults_when_both_overrides_are_blank():
    row = _sample_bank_row()
    surrogate = {
        "federal_agi": "60000",
        "federal_taxable_social_security": "18000",
    }

    resolved = resolve_nc_override_aware_values(row, surrogate)

    assert resolved["federal_agi"] == "60000"
    assert resolved["federal_taxable_social_security"] == "18000"
    assert resolved["nc_input_source"] == "derived"


def test_resolve_nc_override_aware_values_uses_row_value_for_single_populated_override():
    row = _sample_bank_row()
    row["federal_agi"] = "48000"
    surrogate = {
        "federal_agi": "60000",
        "federal_taxable_social_security": "18000",
    }

    resolved = resolve_nc_override_aware_values(row, surrogate)

    assert resolved["federal_agi"] == "48000"
    assert resolved["federal_taxable_social_security"] == "18000"
    assert resolved["nc_input_source"] == "manual_override"


def test_resolve_nc_override_aware_values_uses_row_values_when_both_overrides_are_populated():
    row = _sample_bank_row()
    row["federal_agi"] = "48000"
    row["federal_taxable_social_security"] = "20000"
    surrogate = {
        "federal_agi": "60000",
        "federal_taxable_social_security": "18000",
    }

    resolved = resolve_nc_override_aware_values(row, surrogate)

    assert resolved["federal_agi"] == "48000"
    assert resolved["federal_taxable_social_security"] == "20000"
    assert resolved["nc_input_source"] == "manual_override"


def test_load_scenario_bank_csv_reports_row_2_missing_required_base_field(tmp_path):
    csv_path = tmp_path / "row_2_missing_required_field.csv"
    csv_path.write_text(
        "case_id,tax_year,state_code,filing_status,taxpayer_age,ordinary_income,ltcg_qd_income,social_security_income,nontaxable_income,deduction_mode,deduction_amount,nc_deduction_mode\n"
        "single_case_001,2026,NC,single,45,60000,0,0,0,standard,0,standard\n"
        "single_case_002,2026,,single,45,60000,0,0,0,standard,0,standard\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=r"row 2.*state_code"):
        load_scenario_bank_csv(csv_path)


def test_build_nc_ready_input_fragment_uses_derived_values():
    row = _sample_bank_row()
    resolved = {
        "federal_agi": "60000",
        "federal_taxable_social_security": "18000",
        "nc_input_source": "derived",
    }

    fragment = build_nc_ready_input_fragment(row, resolved)

    assert fragment == {
        "state_code": "NC",
        "filing_status": "single",
        "federal_agi": "60000",
        "federal_taxable_social_security": "18000",
        "nc_deduction_mode": "standard",
        "nc_input_source": "derived",
    }


def test_build_nc_ready_input_fragment_uses_manual_override_values():
    row = _sample_bank_row()
    row["federal_agi"] = "48000"
    row["federal_taxable_social_security"] = "20000"
    resolved = {
        "federal_agi": "48000",
        "federal_taxable_social_security": "20000",
        "nc_input_source": "manual_override",
    }

    fragment = build_nc_ready_input_fragment(row, resolved)

    assert fragment == {
        "state_code": "NC",
        "filing_status": "single",
        "federal_agi": "48000",
        "federal_taxable_social_security": "20000",
        "nc_deduction_mode": "standard",
        "nc_input_source": "manual_override",
    }


def test_build_nc_defaults_from_federal_result_uses_real_federal_result_values():
    scenario = TaxScenarioInput(**SCENARIO)
    federal_result = orchestrate_federal_tax(scenario)

    surrogate = build_nc_defaults_from_federal_result(federal_result)

    assert surrogate == {
        "federal_agi": str(federal_result.agi),
        "federal_taxable_social_security": str(federal_result.ss_output.taxable_social_security),
    }


def test_run_single_row_federal_pass_1_and_build_nc_ready_fragment_derived_from_real_result_when_row_overrides_are_blank():
    row = _sample_bank_row()

    result = run_single_row_federal_pass_1_and_build_nc_ready_fragment(row)

    federal_result = result["federal_result"]
    fragment = result["nc_ready_input_fragment"]

    assert isinstance(federal_result, object)
    assert federal_result.agi == float(fragment["federal_agi"])
    assert federal_result.ss_output.taxable_social_security == float(fragment["federal_taxable_social_security"])
    assert fragment == {
        "state_code": "NC",
        "filing_status": "single",
        "federal_agi": str(federal_result.agi),
        "federal_taxable_social_security": str(federal_result.ss_output.taxable_social_security),
        "nc_deduction_mode": "standard",
        "nc_input_source": "derived",
    }


def test_run_single_row_federal_pass_1_and_build_nc_ready_fragment_prefers_manual_override_values():
    row = _sample_bank_row()
    row["federal_agi"] = "48000"
    row["federal_taxable_social_security"] = "20000"

    result = run_single_row_federal_pass_1_and_build_nc_ready_fragment(row)

    federal_result = result["federal_result"]
    fragment = result["nc_ready_input_fragment"]

    assert isinstance(federal_result, object)
    assert fragment == {
        "state_code": "NC",
        "filing_status": "single",
        "federal_agi": "48000",
        "federal_taxable_social_security": "20000",
        "nc_deduction_mode": "standard",
        "nc_input_source": "manual_override",
    }
    assert federal_result.agi != float(fragment["federal_agi"]) or federal_result.ss_output.taxable_social_security != float(fragment["federal_taxable_social_security"])


def test_compose_nc_ready_input_fragment_from_federal_result_uses_derived_defaults_when_row_overrides_are_blank():
    row = _sample_bank_row()
    federal_result = orchestrate_federal_tax(TaxScenarioInput(**SCENARIO))

    fragment = compose_nc_ready_input_fragment_from_federal_result(row, federal_result)

    assert fragment == {
        "state_code": "NC",
        "filing_status": "single",
        "federal_agi": str(federal_result.agi),
        "federal_taxable_social_security": str(federal_result.ss_output.taxable_social_security),
        "nc_deduction_mode": "standard",
        "nc_input_source": "derived",
    }


def test_compose_nc_ready_input_fragment_from_federal_result_prefers_row_manual_overrides():
    row = _sample_bank_row()
    row["federal_agi"] = "48000"
    row["federal_taxable_social_security"] = "20000"
    federal_result = orchestrate_federal_tax(TaxScenarioInput(**SCENARIO))

    fragment = compose_nc_ready_input_fragment_from_federal_result(row, federal_result)

    assert fragment == {
        "state_code": "NC",
        "filing_status": "single",
        "federal_agi": "48000",
        "federal_taxable_social_security": "20000",
        "nc_deduction_mode": "standard",
        "nc_input_source": "manual_override",
    }


def test_compose_nc_ready_input_fragment_uses_surrogate_defaults_when_overrides_are_blank():
    row = _sample_bank_row()
    federal_pass_values = {
        "federal_agi": "60000",
        "federal_taxable_social_security": "18000",
    }

    fragment = compose_nc_ready_input_fragment(row, federal_pass_values)

    assert fragment == {
        "state_code": "NC",
        "filing_status": "single",
        "federal_agi": "60000",
        "federal_taxable_social_security": "18000",
        "nc_deduction_mode": "standard",
        "nc_input_source": "derived",
    }


def test_compose_nc_ready_input_fragment_uses_manual_override_values_when_present():
    row = _sample_bank_row()
    row["federal_agi"] = "48000"
    row["federal_taxable_social_security"] = "20000"
    federal_pass_values = {
        "federal_agi": "60000",
        "federal_taxable_social_security": "18000",
    }

    fragment = compose_nc_ready_input_fragment(row, federal_pass_values)

    assert fragment == {
        "state_code": "NC",
        "filing_status": "single",
        "federal_agi": "48000",
        "federal_taxable_social_security": "20000",
        "nc_deduction_mode": "standard",
        "nc_input_source": "manual_override",
    }


def test_load_scenario_bank_csv_stops_on_first_failing_row(tmp_path):
    csv_path = tmp_path / "first_failing_row.csv"
    csv_path.write_text(
        "case_id,tax_year,state_code,filing_status,taxpayer_age,ordinary_income,ltcg_qd_income,social_security_income,nontaxable_income,deduction_mode,deduction_amount,nc_deduction_mode\n"
        "single_case_001,2026,NC,single,45,60000,0,0,0,standard,0,standard\n"
        "single_case_002,2026,,single,45,60000,0,0,0,standard,0,standard\n"
        "single_case_003,2026,,single,45,60000,0,0,0,standard,0,standard\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=r"row 2.*state_code"):
        load_scenario_bank_csv(csv_path)


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


def test_phase_38b_blank_optional_expected_result_cells_are_allowed_and_remain_blank():
    sample_row = _sample_bank_row()
    assert sample_row["expected_federal_total_tax"] == ""
    assert sample_row["expected_nc_tax"] == ""
    assert sample_row["expected_projected_irmaa_2028_premium"] == ""


def test_phase_38b_required_base_inputs_remain_populated_while_optional_override_and_expected_cells_can_be_blank():
    sample_row = _sample_bank_row()

    required_fields = (
        "case_id",
        "tax_year",
        "state_code",
        "filing_status",
        "ordinary_income",
        "ltcg_qd_income",
        "social_security_income",
        "deduction_mode",
        "nc_deduction_mode",
    )

    for field in required_fields:
        assert sample_row[field] != ""

    assert sample_row["federal_agi"] == ""
    assert sample_row["federal_taxable_social_security"] == ""
    assert sample_row["expected_federal_total_tax"] == ""
    assert sample_row["expected_nc_tax"] == ""
    assert sample_row["expected_projected_irmaa_2028_premium"] == ""


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


def test_run_single_row_federal_pass_1_and_build_nc_ready_fragment_requires_documented_execution_fields():
    row = _sample_bank_row()
    row.pop("nontaxable_income", None)

    with pytest.raises(ValueError, match="missing required fields: nontaxable_income"):
        run_single_row_federal_pass_1_and_build_nc_ready_fragment(row)


def test_run_single_row_federal_pass_1_and_build_nc_ready_fragment_executes_complete_row():
    row = _sample_bank_row()

    result = run_single_row_federal_pass_1_and_build_nc_ready_fragment(row)

    fragment = result["nc_ready_input_fragment"]
    assert fragment["nc_input_source"] == "derived"
    assert fragment["federal_agi"] == str(result["federal_result"].agi)
    assert fragment["federal_taxable_social_security"] == str(result["federal_result"].ss_output.taxable_social_security)
    assert fragment["state_code"] == "NC"
    assert fragment["filing_status"] == "single"


def test_run_single_row_nc_pass_2_uses_derived_federal_defaults_when_overrides_are_blank():
    row = _sample_bank_row()
    pass_1_result = run_single_row_federal_pass_1_and_build_nc_ready_fragment(row)

    nc_pass_2 = run_single_row_nc_pass_2(row, pass_1_result["nc_ready_input_fragment"])

    assert nc_pass_2["nc_input"].federal_agi == float(pass_1_result["nc_ready_input_fragment"]["federal_agi"])
    assert nc_pass_2["nc_input"].federal_taxable_social_security == float(
        pass_1_result["nc_ready_input_fragment"]["federal_taxable_social_security"]
    )
    assert nc_pass_2["nc_result"].breakdown["starting_federal_agi"] == float(
        pass_1_result["nc_ready_input_fragment"]["federal_agi"]
    )
    assert nc_pass_2["nc_result"].breakdown["less_federal_taxable_social_security"] == float(
        pass_1_result["nc_ready_input_fragment"]["federal_taxable_social_security"]
    )


def test_run_single_row_nc_pass_2_prefers_manual_override_values_when_present():
    row = _sample_bank_row()
    row["federal_agi"] = "48000"
    row["federal_taxable_social_security"] = "20000"
    pass_1_result = run_single_row_federal_pass_1_and_build_nc_ready_fragment(row)

    nc_pass_2 = run_single_row_nc_pass_2(row, pass_1_result["nc_ready_input_fragment"])

    assert nc_pass_2["nc_input"].federal_agi == 48000.0
    assert nc_pass_2["nc_input"].federal_taxable_social_security == 20000.0
    assert nc_pass_2["nc_result"].breakdown["starting_federal_agi"] == 48000.0
    assert nc_pass_2["nc_result"].breakdown["less_federal_taxable_social_security"] == 20000.0


def test_run_single_row_combined_two_pass_uses_derived_nc_input_source_when_overrides_are_blank():
    row = _sample_bank_row()

    bundle = run_single_row_combined_two_pass(row)

    assert bundle["nc_input_source"] == "derived"
    assert bundle["nc_ready_input_fragment"]["nc_input_source"] == "derived"
    assert bundle["nc_input"].federal_agi == float(bundle["nc_ready_input_fragment"]["federal_agi"])
    assert bundle["nc_input"].federal_taxable_social_security == float(
        bundle["nc_ready_input_fragment"]["federal_taxable_social_security"]
    )
    assert bundle["nc_result"].breakdown["starting_federal_agi"] == float(
        bundle["nc_ready_input_fragment"]["federal_agi"]
    )


def test_run_single_row_combined_two_pass_prefers_manual_override_values_when_present():
    row = _sample_bank_row()
    row["federal_agi"] = "48000"
    row["federal_taxable_social_security"] = "20000"

    bundle = run_single_row_combined_two_pass(row)

    assert bundle["nc_input_source"] == "manual_override"
    assert bundle["nc_ready_input_fragment"]["federal_agi"] == "48000"
    assert bundle["nc_ready_input_fragment"]["federal_taxable_social_security"] == "20000"
    assert bundle["nc_input"].federal_agi == 48000.0
    assert bundle["nc_input"].federal_taxable_social_security == 20000.0
    assert bundle["nc_result"].breakdown["starting_federal_agi"] == 48000.0
    assert bundle["nc_result"].breakdown["less_federal_taxable_social_security"] == 20000.0


def test_build_single_row_summary_payload_separates_case_federal_and_nc_sections_when_overrides_are_blank():
    row = _sample_bank_row()
    bundle = run_single_row_combined_two_pass(row)

    payload = build_single_row_summary_payload(bundle)

    assert payload["case_metadata"]["case_id"] == "single_case_001"
    assert payload["case_metadata"]["state_code"] == "NC"
    assert payload["federal"]["agi"] == bundle["federal_result"].agi
    assert payload["nc_planning"]["nc_input"].federal_agi == float(bundle["nc_ready_input_fragment"]["federal_agi"])
    assert payload["nc_input_source"]["source"] == "derived"
    assert payload["nc_input_source"]["fields"]["federal_agi"] == bundle["nc_ready_input_fragment"]["federal_agi"]


def test_build_single_row_summary_payload_separates_case_federal_and_nc_sections_when_manual_override_is_present():
    row = _sample_bank_row()
    row["federal_agi"] = "48000"
    row["federal_taxable_social_security"] = "20000"
    bundle = run_single_row_combined_two_pass(row)

    payload = build_single_row_summary_payload(bundle)

    assert payload["case_metadata"]["case_id"] == "single_case_001"
    assert payload["case_metadata"]["state_code"] == "NC"
    assert payload["federal"]["agi"] == bundle["federal_result"].agi
    assert payload["nc_planning"]["nc_input"].federal_agi == 48000.0
    assert payload["nc_input_source"]["source"] == "manual_override"
    assert payload["nc_input_source"]["fields"]["federal_agi"] == "48000"


def test_build_single_row_expected_vs_actual_payload_omits_blank_expected_values_and_supports_federal_and_nc_fields():
    row = _sample_bank_row()
    row["expected_federal_total_tax"] = "50000"
    row["expected_nc_tax"] = "1000"
    row["expected_ordinary_tax"] = ""
    bundle = run_single_row_combined_two_pass(row)

    payload = build_single_row_expected_vs_actual_payload(row, bundle)

    assert payload["case_id"] == "single_case_001"
    assert payload["state_code"] == "NC"
    assert "expected_federal_total_tax" in payload["comparisons"]
    assert "expected_nc_tax" in payload["comparisons"]
    assert "expected_ordinary_tax" not in payload["comparisons"]
    assert payload["comparisons"]["expected_federal_total_tax"]["matched"] is False
    assert payload["comparisons"]["expected_nc_tax"]["matched"] is False


def test_build_single_row_expected_vs_actual_payload_uses_summary_payload_when_provided():
    row = _sample_bank_row()
    row["expected_federal_total_tax"] = "25000"
    row["expected_nc_tax"] = "5000"
    summary = build_single_row_summary_payload(run_single_row_combined_two_pass(row))

    payload = build_single_row_expected_vs_actual_payload(row, summary)

    assert payload["case_id"] == "single_case_001"
    assert payload["comparisons"]["expected_federal_total_tax"]["actual"] == summary["federal"]["total_federal_tax"]
    assert payload["comparisons"]["expected_nc_tax"]["actual"] == summary["nc_planning"]["nc_result"].nc_income_tax_before_credits


def test_render_single_case_summary_includes_federal_nc_sections_and_nc_input_source_note():
    row = _sample_bank_row()
    bundle = run_single_row_combined_two_pass(row)
    summary = build_single_row_summary_payload(bundle)
    comparison = build_single_row_expected_vs_actual_payload(row, summary)

    rendered = render_single_case_summary(summary, comparison)

    assert "Case summary" in rendered
    assert "Federal summary:" in rendered
    assert "NC planning summary:" in rendered
    assert "NC input source: derived" in rendered
    assert "expected_federal_total_tax" not in rendered


def test_render_single_case_summary_shows_populated_expected_values_and_omits_blank_fields():
    row = _sample_bank_row()
    row["expected_federal_total_tax"] = "25000"
    row["expected_nc_tax"] = "5000"
    row["expected_ordinary_tax"] = ""
    bundle = run_single_row_combined_two_pass(row)
    summary = build_single_row_summary_payload(bundle)
    comparison = build_single_row_expected_vs_actual_payload(row, summary)

    rendered = render_single_case_summary(summary, comparison)

    assert "Expected vs actual:" in rendered
    assert "expected_federal_total_tax" in rendered
    assert "expected_nc_tax" in rendered
    assert "expected_ordinary_tax" not in rendered


def test_run_scenario_bank_csv_cases_returns_one_output_per_valid_row_from_sample_bank():
    csv_path = Path(__file__).parent / "fixtures" / "phase38a_sample_bank.csv"

    outputs = run_scenario_bank_csv_cases(csv_path)

    assert len(outputs) == 1
    assert outputs[0]["case_id"] == "single_case_001"
    assert outputs[0]["summary"]["case_metadata"]["state_code"] == "NC"
    assert "Federal summary:" in outputs[0]["rendered_summary"]


def test_render_single_case_summary_uses_manual_override_source_disclosure_when_present():
    row = _sample_bank_row()
    row["federal_agi"] = "48000"
    row["federal_taxable_social_security"] = "20000"
    bundle = run_single_row_combined_two_pass(row)
    summary = build_single_row_summary_payload(bundle)
    comparison = build_single_row_expected_vs_actual_payload(row, summary)

    rendered = render_single_case_summary(summary, comparison)

    assert "NC input source: manual_override" in rendered
    assert "federal_agi: 48000" in rendered


def test_build_official_source_audit_report_uses_default_sample_bank_fixture():
    report = build_official_source_audit_report()

    assert report["federal"]["reviewed_cases"][0]["case_id"] == "single_case_001"
    assert report["nc"]["reviewed_cases"][0]["case_id"] == "single_case_001"


def test_build_official_source_audit_report_has_separate_federal_and_nc_sections_and_sources():
    row = _sample_bank_row()

    report = build_official_source_audit_report([row])

    assert report["official_sources"]["federal"][0].startswith("IRS")
    assert report["official_sources"]["nc"][0].startswith("NC")
    assert report["federal"]["reviewed_cases"][0]["case_id"] == "single_case_001"
    assert report["nc"]["reviewed_cases"][0]["case_id"] == "single_case_001"
    assert report["federal"]["summary"]["status"] == "no_confirmed_defect_in_current_scope"


def test_classify_audit_difference_handles_match_rounding_and_formula_defect_cases():
    assert classify_audit_difference(100.0, 100.0) == "matches_official_source"
    assert classify_audit_difference(100.02, 100.0) == "rounding_presentation_difference"
    assert classify_audit_difference(200.0, 100.0) == "potential_formula_defect"


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