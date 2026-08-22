from models.inputs import DeductionMode, TaxScenarioInput
from rules.federal.year_2026 import get_standard_deduction


def compute_taxable_ordinary_income(ordinary_income: float, deduction_amount: float) -> float:
    """
    Computes taxable ordinary income by applying deductions.
    Floors the result at zero. Phase 1 does not allocate deduction across
    preferential income types.
    """
    taxable = ordinary_income - deduction_amount
    return max(0.0, taxable)


def resolve_deduction_amount(scenario: TaxScenarioInput) -> float:
    """Resolve the applied deduction while preserving supplied non-standard amounts."""
    if scenario.deduction_mode == DeductionMode.STANDARD:
        return get_standard_deduction(scenario.filing_status)
    return scenario.deduction_amount