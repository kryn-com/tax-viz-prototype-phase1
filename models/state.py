from dataclasses import dataclass
from enum import Enum
from typing import Optional

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
