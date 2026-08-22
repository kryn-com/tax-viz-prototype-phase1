from dataclasses import dataclass
from typing import Optional

from models.inputs import FilingStatus


@dataclass(frozen=True)
class FederalSliverTaxBreakdown:
    ordinary_tax: float
    ltcg_qd_tax: float
    niit_tax: float
    total_federal_tax: float


@dataclass(frozen=True)
class FederalSliverDisplayModel:
    tax_year: int
    filing_status: FilingStatus
    result_kind: str
    baseline_total_federal_tax: float
    altered_total_federal_tax: float
    federal_tax_delta: float
    ordinary_income_increment: float = 0.0
    ltcg_qd_income_increment: float = 0.0
    baseline_breakdown: Optional[FederalSliverTaxBreakdown] = None
    altered_breakdown: Optional[FederalSliverTaxBreakdown] = None
