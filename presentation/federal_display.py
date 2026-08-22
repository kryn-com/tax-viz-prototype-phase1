from models.federal_display import (
    FederalDisplayBracketSlice,
    FederalDisplayModel,
    FederalDisplayRateSlice,
)
from models.outputs import FederalTaxResult


def build_federal_display_model(
    result: FederalTaxResult,
) -> FederalDisplayModel:
    ordinary_bracket_slices = tuple(
        FederalDisplayBracketSlice(
            rate=bracket.rate,
            lower_bound=bracket.lower_bound,
            upper_bound=bracket.upper_bound,
            taxed_amount=bracket.taxed_amount,
            tax_generated=bracket.tax_generated,
        )
        for bracket in result.ordinary_output.bracket_trace
    )
    preferential_rate_slices = (
        FederalDisplayRateSlice(rate=0.0, taxed_amount=result.ltcg_qd_output.taxed_at_0),
        FederalDisplayRateSlice(rate=0.15, taxed_amount=result.ltcg_qd_output.taxed_at_15),
        FederalDisplayRateSlice(rate=0.20, taxed_amount=result.ltcg_qd_output.taxed_at_20),
    )

    return FederalDisplayModel(
        tax_year=result.scenario.tax_year,
        filing_status=result.scenario.filing_status,
        ordinary_income=result.ordinary_output.ordinary_income,
        taxable_social_security=result.ss_output.taxable_social_security,
        tax_free_social_security=result.ss_output.tax_free_social_security,
        taxable_ordinary_income=result.taxable_ordinary_income,
        preferential_income=result.taxable_preferential_income,
        agi=result.agi,
        magi=result.magi,
        ordinary_tax=result.ordinary_tax,
        ltcg_qd_tax=result.ltcg_qd_tax,
        niit_tax=result.niit_tax,
        total_federal_tax=result.total_federal_tax,
        ordinary_bracket_slices=ordinary_bracket_slices,
        preferential_rate_slices=preferential_rate_slices,
    )