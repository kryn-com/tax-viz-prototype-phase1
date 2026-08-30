from dataclasses import dataclass
from typing import Optional


_SUPPORTED_IRMAA_FILING_STATUSES = {"single", "married_filing_jointly"}


def validate_magi(magi: Optional[float]) -> float:
    if magi is None:
        raise ValueError("MAGI is required for IRMAA evaluation.")
    if magi < 0:
        raise ValueError("MAGI cannot be negative.")
    return float(magi)


def validate_filing_status(filing_status: str) -> str:
    if filing_status not in _SUPPORTED_IRMAA_FILING_STATUSES:
        raise ValueError("IRMAA only supports single and married_filing_jointly in this phase.")
    return filing_status


@dataclass(frozen=True)
class IRMAAThresholdRow:
    filing_status: str
    threshold_magi: float
    part_b_monthly_surcharge: float
    part_d_monthly_surcharge: float
    tier_name: str


@dataclass(frozen=True)
class IRMAAOverlayResult:
    filing_status: str
    magi_used: float
    magi_source: str
    threshold_applied: float
    part_b_monthly_surcharge: float
    part_d_monthly_surcharge: float
    total_monthly_surcharge: float
    annual_surcharge: float
    income_year: int
    premium_year: int
    is_estimate: bool
    is_official: bool
    estimate_basis: str
    source_note: str
    rule_version: str
    notes: str
