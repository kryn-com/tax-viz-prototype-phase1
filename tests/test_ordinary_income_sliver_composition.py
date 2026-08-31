import pytest

from engines.federal_orchestrator import orchestrate_federal_tax
from models.inputs import FilingStatus, TaxScenarioInput
from planning.ordinary_income_sliver import compose_additional_ordinary_income_sliver


def _make_scenario(
    *,
    filing_status: FilingStatus = FilingStatus.SINGLE,
    state_code: str = "NC",
    ordinary_income: float = 120000.0,
    ltcg_qd_income: float = 25000.0,
    social_security_income: float = 24000.0,
) -> TaxScenarioInput:
    return TaxScenarioInput(
        tax_year=2026,
        state_code=state_code,
        filing_status=filing_status,
        taxpayer_age=45,
        spouse_age=45 if filing_status is FilingStatus.MARRIED_FILING_JOINTLY else None,
        ordinary_income=ordinary_income,
        ltcg_qd_income=ltcg_qd_income,
        social_security_income=social_security_income,
        nontaxable_income=0.0,
        deduction_mode="standard",
        deduction_amount=0.0,
        nc_deduction_mode="standard",
    )


def test_compose_additional_ordinary_income_sliver_returns_baseline_and_altered_federal_results():
    scenario = _make_scenario()

    result = compose_additional_ordinary_income_sliver(
        scenario,
        additional_ordinary_income=1000.0,
    )

    assert result.result_kind == "ordinary_income_sliver"
    assert result.additional_ordinary_income == 1000.0
    assert result.baseline_federal_result.scenario is scenario
    assert result.altered_federal_result.scenario is not scenario
    assert result.altered_federal_result.scenario.ordinary_income == 121000.0
    assert result.deltas.federal_total_tax_delta == pytest.approx(
        result.altered_federal_result.total_federal_tax
        - result.baseline_federal_result.total_federal_tax
    )


def test_compose_additional_ordinary_income_sliver_recomputes_full_applicable_pipeline():
    scenario = _make_scenario(ordinary_income=10000.0, social_security_income=40000.0)

    result = compose_additional_ordinary_income_sliver(
        scenario,
        additional_ordinary_income=100000.0,
    )

    assert result.altered_federal_result.ss_output.taxable_social_security > (
        result.baseline_federal_result.ss_output.taxable_social_security
    )
    assert result.deltas.federal_ordinary_tax_delta > 0.0
    assert result.baseline_federal_result.ordinary_output is not None
    assert result.altered_federal_result.ordinary_output is not None


def test_compose_additional_ordinary_income_sliver_preserves_separate_outputs_and_deltas():
    scenario = _make_scenario(ordinary_income=150000.0, ltcg_qd_income=90000.0)

    result = compose_additional_ordinary_income_sliver(
        scenario,
        additional_ordinary_income=30000.0,
    )

    assert result.baseline_niit_component == result.baseline_federal_result.niit_output
    assert result.altered_niit_component == result.altered_federal_result.niit_output
    assert result.baseline_nc_result.supported is True
    assert result.altered_nc_result.supported is True
    assert result.baseline_nc_result.result is not None
    assert result.altered_nc_result.result is not None
    assert result.baseline_projected_irmaa_2028.supported is True
    assert result.altered_projected_irmaa_2028.supported is True
    assert result.baseline_projected_irmaa_2028.result is not None
    assert result.altered_projected_irmaa_2028.result is not None
    assert result.deltas.nc_income_tax_before_credits_delta == pytest.approx(
        result.altered_nc_result.result.nc_income_tax_before_credits
        - result.baseline_nc_result.result.nc_income_tax_before_credits
    )
    assert result.deltas.projected_irmaa_annual_surcharge_delta == pytest.approx(
        result.altered_projected_irmaa_2028.result.annual_surcharge
        - result.baseline_projected_irmaa_2028.result.annual_surcharge
    )


def test_compose_additional_ordinary_income_sliver_unsupported_boundaries_are_explicit():
    scenario = _make_scenario(
        filing_status=FilingStatus.HEAD_OF_HOUSEHOLD,
        state_code="PA",
        ordinary_income=210000.0,
    )

    result = compose_additional_ordinary_income_sliver(
        scenario,
        additional_ordinary_income=1000.0,
    )

    assert result.baseline_nc_result.supported is False
    assert result.altered_nc_result.supported is False
    assert result.baseline_nc_result.result is None
    assert result.altered_nc_result.result is None
    assert "state_code is NC" in result.baseline_nc_result.message
    assert result.baseline_projected_irmaa_2028.supported is False
    assert result.altered_projected_irmaa_2028.supported is False
    assert result.baseline_projected_irmaa_2028.result is None
    assert result.altered_projected_irmaa_2028.result is None
    assert "single and married_filing_jointly" in result.baseline_projected_irmaa_2028.message
    assert result.deltas.nc_income_tax_before_credits_delta is None
    assert result.deltas.projected_irmaa_annual_surcharge_delta is None


def test_compose_additional_ordinary_income_sliver_matches_direct_federal_recompute():
    scenario = _make_scenario(ordinary_income=85000.0, social_security_income=30000.0)

    composed = compose_additional_ordinary_income_sliver(
        scenario,
        additional_ordinary_income=5000.0,
    )

    if hasattr(scenario, "model_copy"):
        altered_scenario = scenario.model_copy(update={"ordinary_income": 90000.0})
    else:
        altered_scenario = scenario.copy(update={"ordinary_income": 90000.0})

    direct_baseline = orchestrate_federal_tax(scenario)
    direct_altered = orchestrate_federal_tax(altered_scenario)

    assert composed.baseline_federal_result.total_federal_tax == pytest.approx(
        direct_baseline.total_federal_tax
    )
    assert composed.altered_federal_result.total_federal_tax == pytest.approx(
        direct_altered.total_federal_tax
    )


@pytest.mark.parametrize("increment", [0.0, -1.0])
def test_compose_additional_ordinary_income_sliver_requires_positive_increment(increment):
    with pytest.raises(ValueError, match="greater than zero"):
        compose_additional_ordinary_income_sliver(_make_scenario(), increment)