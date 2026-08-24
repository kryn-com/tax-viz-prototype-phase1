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
    """Resolve the applied deduction, enforcing the standard-deduction floor."""
    standard_deduction = get_standard_deduction(scenario.filing_status)

    if scenario.deduction_mode == DeductionMode.STANDARD:
        return standard_deduction

    return max(scenario.deduction_amount, standard_deduction)