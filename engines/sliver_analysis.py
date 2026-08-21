from models.inputs import TaxScenarioInput
from models.outputs import (
    FederalCombinedSliverResult,
    FederalLTCGQDSLiverResult,
    FederalSliverResult,
)
from engines.federal_orchestrator import orchestrate_federal_tax


def analyze_ordinary_income_sliver(
    scenario: TaxScenarioInput,
    increment: float,
) -> FederalSliverResult:
    if increment <= 0:
        raise ValueError("Ordinary-income sliver increment must be greater than zero.")

    baseline_result = orchestrate_federal_tax(scenario)

    if hasattr(scenario, "model_copy"):
        altered_scenario = scenario.model_copy(
            update={"ordinary_income": scenario.ordinary_income + increment}
        )
    else:
        altered_scenario = scenario.copy(
            update={"ordinary_income": scenario.ordinary_income + increment}
        )

    altered_result = orchestrate_federal_tax(altered_scenario)
    federal_tax_delta = altered_result.total_federal_tax - baseline_result.total_federal_tax

    return FederalSliverResult(
        baseline_result=baseline_result,
        altered_result=altered_result,
        ordinary_income_increment=increment,
        federal_tax_delta=federal_tax_delta,
    )


def analyze_ltcg_qd_sliver(
    scenario: TaxScenarioInput,
    increment: float,
) -> FederalLTCGQDSLiverResult:
    if increment <= 0:
        raise ValueError("LTCG/QD sliver increment must be greater than zero.")

    baseline_result = orchestrate_federal_tax(scenario)

    if hasattr(scenario, "model_copy"):
        altered_scenario = scenario.model_copy(
            update={"ltcg_qd_income": scenario.ltcg_qd_income + increment}
        )
    else:
        altered_scenario = scenario.copy(
            update={"ltcg_qd_income": scenario.ltcg_qd_income + increment}
        )

    altered_result = orchestrate_federal_tax(altered_scenario)
    federal_tax_delta = altered_result.total_federal_tax - baseline_result.total_federal_tax

    return FederalLTCGQDSLiverResult(
        baseline_result=baseline_result,
        altered_result=altered_result,
        ltcg_qd_income_increment=increment,
        federal_tax_delta=federal_tax_delta,
    )


def analyze_combined_income_sliver(
    scenario: TaxScenarioInput,
    ordinary_income_increment: float,
    ltcg_qd_income_increment: float,
) -> FederalCombinedSliverResult:
    if ordinary_income_increment <= 0:
        raise ValueError(
            "Combined ordinary-income sliver increment must be greater than zero."
        )
    if ltcg_qd_income_increment <= 0:
        raise ValueError(
            "Combined LTCG/QD sliver increment must be greater than zero."
        )

    baseline_result = orchestrate_federal_tax(scenario)

    if hasattr(scenario, "model_copy"):
        altered_scenario = scenario.model_copy(
            update={
                "ordinary_income": scenario.ordinary_income + ordinary_income_increment,
                "ltcg_qd_income": scenario.ltcg_qd_income + ltcg_qd_income_increment,
            }
        )
    else:
        altered_scenario = scenario.copy(
            update={
                "ordinary_income": scenario.ordinary_income + ordinary_income_increment,
                "ltcg_qd_income": scenario.ltcg_qd_income + ltcg_qd_income_increment,
            }
        )

    altered_result = orchestrate_federal_tax(altered_scenario)
    federal_tax_delta = altered_result.total_federal_tax - baseline_result.total_federal_tax

    return FederalCombinedSliverResult(
        baseline_result=baseline_result,
        altered_result=altered_result,
        ordinary_income_increment=ordinary_income_increment,
        ltcg_qd_income_increment=ltcg_qd_income_increment,
        federal_tax_delta=federal_tax_delta,
    )
