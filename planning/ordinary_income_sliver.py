from models.inputs import TaxScenarioInput
from models.ordinary_income_sliver import (
    NCSupportedResult,
    OrdinaryIncomeSliverCompositionResult,
    OrdinaryIncomeSliverDeltas,
    ProjectedIRMAASupportedResult,
)
from engines.federal_orchestrator import orchestrate_federal_tax
from engines.state_tax import compute_nc_tax
from rules.irmaa_projected_2028 import build_projected_2028_overlay_result


def _copy_with_updates(
    scenario: TaxScenarioInput,
    updates: dict,
) -> TaxScenarioInput:
    if hasattr(scenario, "model_copy"):
        return scenario.model_copy(update=updates)
    return scenario.copy(update=updates)


def _derive_nc_ready_scenario(
    scenario: TaxScenarioInput,
    federal_agi: float,
    federal_taxable_social_security: float,
) -> TaxScenarioInput:
    return _copy_with_updates(
        scenario,
        {
            "federal_agi": federal_agi,
            "federal_taxable_social_security": federal_taxable_social_security,
        },
    )


def _compute_supported_nc_result(
    scenario: TaxScenarioInput,
) -> NCSupportedResult:
    if scenario.state_code.upper() != "NC":
        return NCSupportedResult(
            supported=False,
            result=None,
            message="NC planning tax is only supported when state_code is NC.",
        )

    return NCSupportedResult(
        supported=True,
        result=compute_nc_tax(scenario),
        message=None,
    )


def _compute_supported_projected_irmaa_result(
    scenario: TaxScenarioInput,
    magi: float,
) -> ProjectedIRMAASupportedResult:
    filing_status = scenario.filing_status.value
    if filing_status not in {"single", "married_filing_jointly"}:
        return ProjectedIRMAASupportedResult(
            supported=False,
            result=None,
            message=(
                "Projected 2028 IRMAA planning mode only supports single "
                "and married_filing_jointly."
            ),
        )

    return ProjectedIRMAASupportedResult(
        supported=True,
        result=build_projected_2028_overlay_result(
            filing_status=filing_status,
            magi=magi,
            magi_source="federal_result.magi",
        ),
        message=None,
    )


def compose_additional_ordinary_income_sliver(
    baseline_scenario: TaxScenarioInput,
    additional_ordinary_income: float,
) -> OrdinaryIncomeSliverCompositionResult:
    if additional_ordinary_income <= 0:
        raise ValueError("Additional ordinary income must be greater than zero.")

    baseline_federal = orchestrate_federal_tax(baseline_scenario)
    altered_scenario = _copy_with_updates(
        baseline_scenario,
        {
            "ordinary_income": baseline_scenario.ordinary_income + additional_ordinary_income,
        },
    )
    altered_federal = orchestrate_federal_tax(altered_scenario)

    baseline_nc_ready = _derive_nc_ready_scenario(
        baseline_scenario,
        federal_agi=baseline_federal.agi,
        federal_taxable_social_security=baseline_federal.ss_output.taxable_social_security,
    )
    altered_nc_ready = _derive_nc_ready_scenario(
        altered_scenario,
        federal_agi=altered_federal.agi,
        federal_taxable_social_security=altered_federal.ss_output.taxable_social_security,
    )

    baseline_nc = _compute_supported_nc_result(baseline_nc_ready)
    altered_nc = _compute_supported_nc_result(altered_nc_ready)

    baseline_irmaa = _compute_supported_projected_irmaa_result(
        baseline_scenario,
        baseline_federal.magi,
    )
    altered_irmaa = _compute_supported_projected_irmaa_result(
        altered_scenario,
        altered_federal.magi,
    )

    nc_delta = None
    if baseline_nc.supported and altered_nc.supported:
        nc_delta = (
            altered_nc.result.nc_income_tax_before_credits
            - baseline_nc.result.nc_income_tax_before_credits
        )

    irmaa_delta = None
    if baseline_irmaa.supported and altered_irmaa.supported:
        irmaa_delta = (
            altered_irmaa.result.annual_surcharge
            - baseline_irmaa.result.annual_surcharge
        )

    deltas = OrdinaryIncomeSliverDeltas(
        federal_total_tax_delta=(
            altered_federal.total_federal_tax - baseline_federal.total_federal_tax
        ),
        federal_ordinary_tax_delta=(
            altered_federal.ordinary_tax - baseline_federal.ordinary_tax
        ),
        federal_ltcg_qd_tax_delta=(
            altered_federal.ltcg_qd_tax - baseline_federal.ltcg_qd_tax
        ),
        federal_niit_tax_delta=(altered_federal.niit_tax - baseline_federal.niit_tax),
        nc_income_tax_before_credits_delta=nc_delta,
        niit_component_delta=(
            altered_federal.niit_output.niit_tax - baseline_federal.niit_output.niit_tax
        ),
        projected_irmaa_annual_surcharge_delta=irmaa_delta,
    )

    return OrdinaryIncomeSliverCompositionResult(
        result_kind="ordinary_income_sliver",
        additional_ordinary_income=additional_ordinary_income,
        baseline_federal_result=baseline_federal,
        altered_federal_result=altered_federal,
        baseline_nc_result=baseline_nc,
        altered_nc_result=altered_nc,
        baseline_niit_component=baseline_federal.niit_output,
        altered_niit_component=altered_federal.niit_output,
        baseline_projected_irmaa_2028=baseline_irmaa,
        altered_projected_irmaa_2028=altered_irmaa,
        deltas=deltas,
    )