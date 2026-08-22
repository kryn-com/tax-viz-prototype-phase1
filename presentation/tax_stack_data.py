from models.outputs import FederalTaxResult
from models.tax_stack_display import (
    FederalTaxStackNIIT,
    FederalTaxStackSocialSecurity,
    FederalTaxStackViewModel,
)
from presentation.federal_display import build_federal_display_model


def build_federal_tax_stack_view_model(
    result: FederalTaxResult,
) -> FederalTaxStackViewModel:
    display_model = build_federal_display_model(result)
    ordinary_marginal_layers = tuple(
        sorted(
            (
                layer
                for layer in display_model.ordinary_bracket_slices
                if layer.taxed_amount != 0.0 or layer.tax_generated != 0.0
            ),
            key=lambda layer: layer.rate,
        )
    )
    preferential_rate_layers = tuple(
        sorted(
            (
                layer
                for layer in display_model.preferential_rate_slices
                if layer.taxed_amount != 0.0
            ),
            key=lambda layer: layer.rate,
        )
    )

    return FederalTaxStackViewModel(
        tax_year=display_model.tax_year,
        filing_status=display_model.filing_status,
        ordinary_income=display_model.ordinary_income,
        taxable_ordinary_income=display_model.taxable_ordinary_income,
        preferential_income=display_model.preferential_income,
        nontaxable_income=result.scenario.nontaxable_income,
        deduction_mode=result.scenario.deduction_mode,
        deduction_shielding_amount=result.ordinary_output.deduction_applied,
        ordinary_marginal_layers=ordinary_marginal_layers,
        preferential_rate_layers=preferential_rate_layers,
        social_security=FederalTaxStackSocialSecurity(
            total_social_security=result.ss_output.total_social_security,
            taxable_social_security=result.ss_output.taxable_social_security,
            tax_free_social_security=result.ss_output.tax_free_social_security,
            provisional_income=result.ss_output.provisional_income,
        ),
        niit=FederalTaxStackNIIT(
            net_investment_income=result.niit_output.net_investment_income,
            magi=result.niit_output.magi,
            threshold_applied=result.niit_output.threshold_applied,
            magi_over_threshold=result.niit_output.magi_over_threshold,
            tax_base=result.niit_output.tax_base,
            niit_rate=result.niit_output.niit_rate,
            niit_tax=result.niit_output.niit_tax,
        ),
        agi=display_model.agi,
        magi=display_model.magi,
        ordinary_tax=display_model.ordinary_tax,
        ltcg_qd_tax=display_model.ltcg_qd_tax,
        total_federal_tax=display_model.total_federal_tax,
    )
