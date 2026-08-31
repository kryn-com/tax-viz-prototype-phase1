from dataclasses import FrozenInstanceError

import pytest

from models.irmaa import IRMAAOverlayResult
from models.inputs import FilingStatus, TaxScenarioInput
from models.nc_planning import NCPlanningResult
from models.outputs import (
    FederalOrdinaryOutput,
    FederalTaxResult,
    LTCG_QD_Output,
    NIITOutput,
    SocialSecurityOutput,
)
from models.planning_scenario import PlanningScenarioResult
from rules.irmaa_projected_2028 import build_projected_2028_overlay_result


def _make_scenario() -> TaxScenarioInput:
    return TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        taxpayer_age=45,
        federal_agi=100000.0,
        federal_taxable_social_security=5000.0,
        net_nc_interest_dividend_adjustment=0.0,
        bailey_exempt_pension_amount=None,
        nc_deduction_mode="standard",
    )


def _make_minimal_federal_result(scenario: TaxScenarioInput) -> FederalTaxResult:
    return FederalTaxResult(
        scenario=scenario,
        agi=100000.0,
        magi=100000.0,
        taxable_ordinary_income=50000.0,
        taxable_preferential_income=0.0,
        ss_output=SocialSecurityOutput(
            total_social_security=0.0,
            taxable_social_security=0.0,
            tax_free_social_security=0.0,
            provisional_income=0.0,
        ),
        ordinary_output=FederalOrdinaryOutput(
            ordinary_income=50000.0,
            deduction_applied=0.0,
            taxable_ordinary_income=50000.0,
            total_tax=0.0,
            bracket_trace=[],
        ),
        ltcg_qd_output=LTCG_QD_Output(
            total_preferential_income=0.0,
            taxed_at_0=0.0,
            taxed_at_15=0.0,
            taxed_at_20=0.0,
            total_preferential_tax=0.0,
        ),
        niit_output=NIITOutput(
            net_investment_income=0.0,
            magi=100000.0,
            threshold_applied=0.0,
            magi_over_threshold=0.0,
            tax_base=0.0,
            niit_rate=0.0,
            niit_tax=0.0,
        ),
        ordinary_tax=0.0,
        ltcg_qd_tax=0.0,
        niit_tax=0.0,
        total_federal_tax=0.0,
    )


def _make_nc_planning_result(federal_result: FederalTaxResult):
    return NCPlanningResult(
        federal_result=federal_result,
        nc_state_result=None,
    )


def test_planning_scenario_result_is_immutable():
    scenario = _make_scenario()
    federal_result = _make_minimal_federal_result(scenario)
    nc_planning_result = _make_nc_planning_result(federal_result)
    projected_irmaa_2028 = build_projected_2028_overlay_result("single", 100000.0)
    result = PlanningScenarioResult(
        scenario=scenario,
        federal_result=federal_result,
        nc_planning_result=nc_planning_result,
        projected_irmaa_2028=projected_irmaa_2028,
    )

    with pytest.raises(FrozenInstanceError):
        result.scenario = scenario


def test_planning_scenario_result_preserves_exact_object_identity():
    scenario = _make_scenario()
    federal_result = _make_minimal_federal_result(scenario)
    nc_planning_result = _make_nc_planning_result(federal_result)
    projected_irmaa_2028 = build_projected_2028_overlay_result("single", 100000.0)

    result = PlanningScenarioResult(
        scenario=scenario,
        federal_result=federal_result,
        nc_planning_result=nc_planning_result,
        projected_irmaa_2028=projected_irmaa_2028,
    )

    assert result.scenario is scenario
    assert result.federal_result is federal_result
    assert result.nc_planning_result is nc_planning_result
    assert result.projected_irmaa_2028 is projected_irmaa_2028


def test_planning_scenario_result_has_no_combined_or_duplicate_top_level_fields():
    scenario = _make_scenario()
    federal_result = _make_minimal_federal_result(scenario)
    nc_planning_result = _make_nc_planning_result(federal_result)
    projected_irmaa_2028 = build_projected_2028_overlay_result("single", 100000.0)

    result = PlanningScenarioResult(
        scenario=scenario,
        federal_result=federal_result,
        nc_planning_result=nc_planning_result,
        projected_irmaa_2028=projected_irmaa_2028,
    )

    assert set(result.__dict__) == {"scenario", "federal_result", "nc_planning_result", "projected_irmaa_2028"}
    assert not hasattr(result, "combined_total")
    assert not hasattr(result, "total_tax")
    assert not hasattr(result, "niit_output")
