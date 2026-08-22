from dataclasses import dataclass
from typing import Optional, Tuple

from models.inputs import FilingStatus


@dataclass(frozen=True)
class FederalDisplayBracketSlice:
    rate: float
    lower_bound: float
    upper_bound: Optional[float]
    taxed_amount: float
    tax_generated: float


@dataclass(frozen=True)
class FederalDisplayRateSlice:
    rate: float
    taxed_amount: float


@dataclass(frozen=True)
class FederalDisplayModel:
    tax_year: int
    filing_status: FilingStatus
    ordinary_income: float
    taxable_social_security: float
    tax_free_social_security: float
    taxable_ordinary_income: float
    preferential_income: float
    agi: float
    magi: float
    ordinary_tax: float
    ltcg_qd_tax: float
    niit_tax: float
    total_federal_tax: float
    ordinary_bracket_slices: Tuple[FederalDisplayBracketSlice, ...]
    preferential_rate_slices: Tuple[FederalDisplayRateSlice, ...]