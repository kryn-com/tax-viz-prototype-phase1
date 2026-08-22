from dataclasses import dataclass
from typing import Tuple

from models.federal_display import (
    FederalDisplayBracketSlice,
    FederalDisplayRateSlice,
)
from models.inputs import DeductionMode, FilingStatus


@dataclass(frozen=True)
class FederalTaxStackSocialSecurity:
    total_social_security: float
    taxable_social_security: float
    tax_free_social_security: float
    provisional_income: float


@dataclass(frozen=True)
class FederalTaxStackNIIT:
    net_investment_income: float
    magi: float
    threshold_applied: float
    magi_over_threshold: float
    tax_base: float
    niit_rate: float
    niit_tax: float


@dataclass(frozen=True)
class FederalTaxStackViewModel:
    tax_year: int
    filing_status: FilingStatus
    ordinary_income: float
    taxable_ordinary_income: float
    preferential_income: float
    nontaxable_income: float
    deduction_mode: DeductionMode
    deduction_shielding_amount: float
    ordinary_marginal_layers: Tuple[FederalDisplayBracketSlice, ...]
    preferential_rate_layers: Tuple[FederalDisplayRateSlice, ...]
    social_security: FederalTaxStackSocialSecurity
    niit: FederalTaxStackNIIT
    agi: float
    magi: float
    ordinary_tax: float
    ltcg_qd_tax: float
    total_federal_tax: float
