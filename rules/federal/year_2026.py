from typing import List, Dict, Optional, TypedDict
from models.inputs import FilingStatus

class BracketDef(TypedDict):
    rate: float
    lower: float
    upper: Optional[float]


STANDARD_DEDUCTIONS_2026: Dict[FilingStatus, float] = {
    FilingStatus.SINGLE: 16100.0,
    FilingStatus.MARRIED_FILING_JOINTLY: 32200.0,
    FilingStatus.MARRIED_FILING_SEPARATELY: 16100.0,
    FilingStatus.HEAD_OF_HOUSEHOLD: 24150.0,
}

# Provisional extrapolated brackets for 2026 to satisfy engine testing.
# These represent the structure of US Federal Income Tax brackets.
BRACKETS_2026: Dict[FilingStatus, List[BracketDef]] = {
    FilingStatus.SINGLE: [
       {"rate": 0.10, "lower": 0.0, "upper": 12400.0},
       {"rate": 0.12, "lower": 12400.0, "upper": 50400.0},
       {"rate": 0.22, "lower": 50400.0, "upper": 105700.0},
       {"rate": 0.24, "lower": 105700.0, "upper": 201775.0},
       {"rate": 0.32, "lower": 201775.0, "upper": 256225.0},
       {"rate": 0.35, "lower": 256225.0, "upper": 640600.0},
       {"rate": 0.37, "lower": 640600.0, "upper": None},
    ],
    FilingStatus.MARRIED_FILING_JOINTLY: [
        {"rate": 0.10, "lower": 0.0, "upper": 24800.0},
        {"rate": 0.12, "lower": 24800.0, "upper": 100800.0},
        {"rate": 0.22, "lower": 100800.0, "upper": 211400.0},
        {"rate": 0.24, "lower": 211400.0, "upper": 403550.0},
        {"rate": 0.32, "lower": 403550.0, "upper": 512450.0},
        {"rate": 0.35, "lower": 512450.0, "upper": 768700.0},
        {"rate": 0.37, "lower": 768700.0, "upper": None},
    ],
    FilingStatus.MARRIED_FILING_SEPARATELY: [
        {"rate": 0.10, "lower": 0.0, "upper": 11600.0},
        {"rate": 0.12, "lower": 11600.0, "upper": 47150.0},
        {"rate": 0.22, "lower": 47150.0, "upper": 100525.0},
        {"rate": 0.24, "lower": 100525.0, "upper": 191950.0},
        {"rate": 0.32, "lower": 191950.0, "upper": 243725.0},
        {"rate": 0.35, "lower": 243725.0, "upper": 365600.0},
        {"rate": 0.37, "lower": 365600.0, "upper": None},
    ],
    FilingStatus.HEAD_OF_HOUSEHOLD: [
        {"rate": 0.10, "lower": 0.0, "upper": 17700.0},
        {"rate": 0.12, "lower": 17700.0, "upper": 67450.0},
        {"rate": 0.22, "lower": 67450.0, "upper": 105700.0},
        {"rate": 0.24, "lower": 105700.0, "upper": 201775.0},
        {"rate": 0.32, "lower": 201775.0, "upper": 256200.0},
        {"rate": 0.35, "lower": 256200.0, "upper": 640600.0},
        {"rate": 0.37, "lower": 640600.0, "upper": None},
    ],
}

def get_brackets_for_status(filing_status: FilingStatus) -> List[BracketDef]:
    """Retrieves the bracket definition for a specific filing status."""
    if filing_status not in BRACKETS_2026:
        raise ValueError(f"No 2026 brackets defined for {filing_status}")
    return BRACKETS_2026[filing_status]


def get_standard_deduction(filing_status: FilingStatus) -> float:
    """Return the 2026 standard deduction for a filing status."""
    if filing_status not in STANDARD_DEDUCTIONS_2026:
        raise ValueError(f"No 2026 standard deduction defined for {filing_status}")
    return STANDARD_DEDUCTIONS_2026[filing_status]