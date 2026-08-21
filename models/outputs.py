from dataclasses import dataclass, field
from typing import List, Optional
from models.inputs import TaxScenarioInput

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


@dataclass
class NIITOutput:
    net_investment_income: float
    magi: float
    threshold_applied: float
    magi_over_threshold: float
    tax_base: float
    niit_rate: float
    niit_tax: float

@dataclass
class FederalTaxResult:
    """
    Unified result object aggregating the original scenario, derived income bases,
    and all preserved component outputs from the federal tax pipeline.
    """
    scenario: TaxScenarioInput

    agi: float
    magi: float
    taxable_ordinary_income: float
    taxable_preferential_income: float

    ss_output: SocialSecurityOutput
    ordinary_output: FederalOrdinaryOutput
    ltcg_qd_output: LTCG_QD_Output
    niit_output: NIITOutput

    ordinary_tax: float
    ltcg_qd_tax: float
    niit_tax: float
    total_federal_tax: float

@dataclass
class FederalSliverResult:
    baseline_result: FederalTaxResult
    altered_result: FederalTaxResult
    ordinary_income_increment: float
    federal_tax_delta: float

@dataclass
class FederalLTCGQDSLiverResult:
    baseline_result: FederalTaxResult
    altered_result: FederalTaxResult
    ltcg_qd_income_increment: float
    federal_tax_delta: float

@dataclass
class FederalCombinedSliverResult:
    baseline_result: FederalTaxResult
    altered_result: FederalTaxResult
    ordinary_income_increment: float
    ltcg_qd_income_increment: float
    federal_tax_delta: float