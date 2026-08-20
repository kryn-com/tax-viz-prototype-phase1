from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class BracketSlice:
    rate: float
    lower_bound: float
    upper_bound: Optional[float]
    taxed_amount: float
    tax_generated: float

@dataclass
class FederalOrdinaryOutput:
    ordinary_income: float
    deduction_applied: float
    taxable_ordinary_income: float
    total_tax: float
    bracket_trace: List[BracketSlice] = field(default_factory=list)

@dataclass
class SocialSecurityOutput:
    total_social_security: float
    taxable_social_security: float
    tax_free_social_security: float
    provisional_income: float

@dataclass
class LTCG_QD_Output:
    total_preferential_income: float
    taxed_at_0: float
    taxed_at_15: float
    taxed_at_20: float
    total_preferential_tax: float