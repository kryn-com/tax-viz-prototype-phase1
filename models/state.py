from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from models.inputs import FilingStatus


class StateTaxSupport(str, Enum):
    FLAT_TAX = "flat_tax"
    NO_INCOME_TAX = "no_income_tax"
    UNSUPPORTED = "unsupported"


class UnsupportedStateError(ValueError):
    pass


@dataclass(frozen=True)
class StateTaxRequest:
    tax_year: int
    state_code: str
    filing_status: FilingStatus
    state_taxable_income: float

    def __post_init__(self):
        if self.state_taxable_income < 0:
            raise ValueError("State taxable income cannot be negative.")


@dataclass(frozen=True)
class StateTaxResult:
    request: StateTaxRequest
    support: StateTaxSupport
    state_tax_amount: Optional[float] = None


@dataclass(frozen=True)
class NCStateTaxBreakdown:
    starting_federal_agi: float
    less_federal_taxable_social_security: float
    plus_net_nc_interest_dividend_adjustment: float
    less_bailey_exempt_pension_amount: float
    less_selected_nc_deduction_amount: float
    final_nc_taxable_income: float
    nc_flat_rate: float
    computed_nc_tax_before_credits: float


@dataclass(frozen=True)
class NCStateTaxResult:
    tax_year: int
    state_code: str
    filing_status: FilingStatus
    nc_taxable_income: float
    nc_income_tax_before_credits: float
    breakdown: Dict[str, Any]
