def compute_taxable_ordinary_income(ordinary_income: float, deduction_amount: float) -> float:
    """
    Computes taxable ordinary income by applying deductions.
    Floors the result at zero. Phase 1 does not allocate deduction across
    preferential income types.
    """
    taxable = ordinary_income - deduction_amount
    return max(0.0, taxable)