from engines.state_policy import require_supported_state
from models.inputs import NCDeductionMode, TaxScenarioInput
from models.state import NCStateTaxResult, StateTaxRequest, StateTaxResult, StateTaxSupport
from rules.state_policy import NC_2026_RULES, STATE_TAX_RATES_2026


def compute_state_tax(request: StateTaxRequest) -> StateTaxResult:
    support = require_supported_state(request.state_code)

    if support is StateTaxSupport.FLAT_TAX:
        state_tax_amount = (
            request.state_taxable_income
            * STATE_TAX_RATES_2026[request.state_code.upper()]
        )
    else:
        state_tax_amount = 0.0

    return StateTaxResult(
        request=request,
        support=support,
        state_tax_amount=state_tax_amount,
    )


def compute_nc_tax(scenario: TaxScenarioInput) -> NCStateTaxResult:
    if scenario.state_code.upper() != "NC":
        raise ValueError("compute_nc_tax is only defined for North Carolina state_code='NC'.")

    if scenario.nc_deduction_mode is NCDeductionMode.ITEMIZED:
        selected_deduction_amount = scenario.nc_itemized_deduction_amount
    else:
        selected_deduction_amount = NC_2026_RULES["standard_deduction_by_filing_status"][
            scenario.filing_status.value
        ]

    bailey_amount = scenario.bailey_exempt_pension_amount or 0.0
    nc_taxable_income = (
        scenario.federal_agi
        - scenario.federal_taxable_social_security
        + scenario.net_nc_interest_dividend_adjustment
        - bailey_amount
        - selected_deduction_amount
    )
    nc_taxable_income = max(0.0, nc_taxable_income)

    nc_income_tax_before_credits = round(nc_taxable_income * NC_2026_RULES["flat_rate"], 2)

    breakdown = {
        "starting_federal_agi": scenario.federal_agi,
        "less_federal_taxable_social_security": scenario.federal_taxable_social_security,
        "plus_net_nc_interest_dividend_adjustment": scenario.net_nc_interest_dividend_adjustment,
        "less_bailey_exempt_pension_amount": bailey_amount,
        "less_selected_nc_deduction_amount": selected_deduction_amount,
        "final_nc_taxable_income": nc_taxable_income,
        "nc_flat_rate": NC_2026_RULES["flat_rate"],
        "computed_nc_tax_before_credits": nc_income_tax_before_credits,
        "selected_nc_deduction_amount": selected_deduction_amount,
    }

    return NCStateTaxResult(
        tax_year=scenario.tax_year,
        state_code=scenario.state_code,
        filing_status=scenario.filing_status,
        nc_taxable_income=round(nc_taxable_income, 2),
        nc_income_tax_before_credits=nc_income_tax_before_credits,
        breakdown=breakdown,
    )