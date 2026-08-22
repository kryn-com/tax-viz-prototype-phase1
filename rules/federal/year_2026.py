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
        {"rate": 0.10, "lower": 0.0, "upper": 11600.0},
        {"rate": 0.12, "lower": 11600.0, "upper": 47150.0},
        {"rate": 0.22, "lower": 47150.0, "upper": 100525.0},
        {"rate": 0.24, "lower": 100525.0, "upper": 191950.0},
        {"rate": 0.32, "lower": 191950.0, "upper": 243725.0},
        {"rate": 0.35, "lower": 243725.0, "upper": 609350.0},
        {"rate": 0.37, "lower": 609350.0, "upper": None},
    ],
    FilingStatus.MARRIED_FILING_JOINTLY: [
        {"rate": 0.10, "lower": 0.0, "upper": 23200.0},
        {"rate": 0.12, "lower": 23200.0, "upper": 94300.0},
        {"rate": 0.22, "lower": 94300.0, "upper": 201050.0},
        {"rate": 0.24, "lower": 201050.0, "upper": 383900.0},
        {"rate": 0.32, "lower": 383900.0, "upper": 487450.0},
        {"rate": 0.35, "lower": 487450.0, "upper": 731200.0},
        {"rate": 0.37, "lower": 731200.0, "upper": None},
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
        {"rate": 0.10, "lower": 0.0, "upper": 16550.0},
        {"rate": 0.12, "lower": 16550.0, "upper": 63100.0},
        {"rate": 0.22, "lower": 63100.0, "upper": 100500.0},
        {"rate": 0.24, "lower": 100500.0, "upper": 191950.0},
        {"rate": 0.32, "lower": 191950.0, "upper": 243700.0},
        {"rate": 0.35, "lower": 243700.0, "upper": 609300.0},
        {"rate": 0.37, "lower": 609300.0, "upper": None},
    ]
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