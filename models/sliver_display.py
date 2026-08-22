from dataclasses import dataclass

from models.inputs import FilingStatus


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
