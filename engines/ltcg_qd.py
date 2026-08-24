from models.inputs import TaxScenarioInput, FilingStatus
from models.outputs import LTCG_QD_Output
from engines.deductions import compute_taxable_ordinary_income, resolve_deduction_amount

def compute_preferential_tax(scenario: TaxScenarioInput) -> LTCG_QD_Output:
    """
    Computes the tax on long-term capital gains and qualified dividends.
    Uses standard stacking rules: ordinary income fills bottom brackets,
    and preferential income is layered on top, passing through 0%, 15%, and 20% thresholds.
    """
    if scenario.filing_status == FilingStatus.MARRIED_FILING_SEPARATELY:
        raise NotImplementedError("Married Filing Separately is permanently out of scope for this project.")

    # Corrected 2026 provisional LTCG thresholds
    if scenario.filing_status == FilingStatus.SINGLE:
        threshold_15 = 49450.0
        threshold_20 = 545500.0
    elif scenario.filing_status == FilingStatus.MARRIED_FILING_JOINTLY:
        threshold_15 = 98900.0
        threshold_20 = 613700.0
    elif scenario.filing_status == FilingStatus.HEAD_OF_HOUSEHOLD:
        threshold_15 = 66200.0
        threshold_20 = 579600.0
    else:
        raise ValueError(f"Unsupported status for LTCG: {scenario.filing_status}")

    pref_income = scenario.ltcg_qd_income
    
    # Handle trivial case early
    if pref_income == 0.0:
        return LTCG_QD_Output(
            total_preferential_income=0.0,
            taxed_at_0=0.0,
            taxed_at_15=0.0,
            taxed_at_20=0.0,
            total_preferential_tax=0.0
        )

    # Calculate the base ordinary income pushing preferential income up the brackets.
    applied_deduction = resolve_deduction_amount(scenario)

    base_income = compute_taxable_ordinary_income(
        ordinary_income=scenario.ordinary_income,
        deduction_amount=applied_deduction
    )

    # 1. Fill the 0% Bracket
    capacity_0 = max(0.0, threshold_15 - base_income)
    taxed_at_0 = min(pref_income, capacity_0)

    # 2. Fill the 15% Bracket
    rem_pref_after_0 = pref_income - taxed_at_0
    capacity_15 = max(0.0, threshold_20 - max(base_income, threshold_15))
    taxed_at_15 = min(rem_pref_after_0, capacity_15)

    # 3. Fill the 20% Bracket (unlimited capacity)
    taxed_at_20 = rem_pref_after_0 - taxed_at_15

    # Compute final tax
    total_tax = (taxed_at_15 * 0.15) + (taxed_at_20 * 0.20)

    return LTCG_QD_Output(
        total_preferential_income=pref_income,
        taxed_at_0=taxed_at_0,
        taxed_at_15=taxed_at_15,
        taxed_at_20=taxed_at_20,
        total_preferential_tax=total_tax
    )