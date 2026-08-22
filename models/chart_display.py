from dataclasses import dataclass
from typing import Optional, Tuple

from models.inputs import FilingStatus


@dataclass(frozen=True)
class FederalChartSegment:
    label: str
    value: float
    rate: Optional[float] = None


@dataclass(frozen=True)
class FederalChartViewModel:
    tax_year: int
    filing_status: FilingStatus
    total_federal_tax: float
    tax_component_segments: Tuple[FederalChartSegment, ...]
    ordinary_bracket_segments: Tuple[FederalChartSegment, ...]
    preferential_rate_segments: Tuple[FederalChartSegment, ...]
