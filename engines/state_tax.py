from engines.state_policy import require_supported_state
from models.state import StateTaxRequest, StateTaxResult, StateTaxSupport
from rules.state_policy import STATE_TAX_RATES_2026


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