from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from models.outputs import BracketSlice, FederalOrdinaryOutput
from models.inputs import FilingStatus
from models.inputs import TaxScenarioInput
from rules.federal.year_2026 import get_brackets_for_status
from engines.deductions import compute_taxable_ordinary_income, resolve_deduction_amount

PROVISIONAL_PRINTED_TAX_TABLE_METHOD_LABEL = (
    "provisional_2026_printed_tax_table_reproduction_pending_official_irs_publication"
)


@dataclass(frozen=True)
class ProvisionalPrintedTaxTableReproductionResult:
    taxable_income: float
    interval_lower_bound: float
    interval_upper_bound_exclusive: float | None
    midpoint_used: float
    reproduced_ordinary_tax: float
    method_label: str
    fallback_to_exact: bool


def _compute_ordinary_tax_from_taxable_income(
    filing_status: FilingStatus,
    taxable_income: float,
) -> tuple[float, list[BracketSlice]]:
    brackets = get_brackets_for_status(filing_status)
    total_tax = 0.0
    trace: list[BracketSlice] = []

    for bracket in brackets:
        lower = bracket["lower"]
        upper = bracket["upper"]
        rate = bracket["rate"]

        if taxable_income <= lower:
            trace.append(
                BracketSlice(
                    rate=rate,
                    lower_bound=lower,
                    upper_bound=upper,
                    taxed_amount=0.0,
                    tax_generated=0.0,
                )
            )
            continue

        if upper is None:
            taxed_amount = taxable_income - lower
        else:
            taxed_amount = min(taxable_income, upper) - lower

        tax_generated = taxed_amount * rate
        total_tax += tax_generated

        trace.append(
            BracketSlice(
                rate=rate,
                lower_bound=lower,
                upper_bound=upper,
                taxed_amount=taxed_amount,
                tax_generated=tax_generated,
            )
        )

    return total_tax, trace


def _resolve_provisional_printed_tax_table_interval(taxable_income: float) -> tuple[float, float, float]:
    if taxable_income < 5.0:
        return 0.0, 5.0, 0.0
    if taxable_income < 15.0:
        return 5.0, 15.0, 10.0
    if taxable_income < 25.0:
        return 15.0, 25.0, 20.0
    if taxable_income < 3000.0:
        lower = 25.0 + (int((taxable_income - 25.0) // 25.0) * 25.0)
        upper = lower + 25.0
        return lower, upper, lower + 12.5

    lower = 3000.0 + (int((taxable_income - 3000.0) // 50.0) * 50.0)
    upper = lower + 50.0
    return lower, upper, lower + 25.0


def _round_whole_dollar_half_up(amount: float) -> float:
    return float(Decimal(str(amount)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def reproduce_provisional_printed_tax_table_ordinary_tax(
    filing_status: FilingStatus,
    taxable_income: float,
) -> ProvisionalPrintedTaxTableReproductionResult:
    """Reproduce the project provisional 2026 printed-tax-table method for validation only."""
    if taxable_income < 0.0:
        raise ValueError("taxable_income cannot be negative")

    if taxable_income >= 100000.0:
        exact_tax, _ = _compute_ordinary_tax_from_taxable_income(
            filing_status=filing_status,
            taxable_income=taxable_income,
        )
        return ProvisionalPrintedTaxTableReproductionResult(
            taxable_income=taxable_income,
            interval_lower_bound=100000.0,
            interval_upper_bound_exclusive=None,
            midpoint_used=taxable_income,
            reproduced_ordinary_tax=exact_tax,
            method_label=PROVISIONAL_PRINTED_TAX_TABLE_METHOD_LABEL,
            fallback_to_exact=True,
        )

    lower, upper, midpoint = _resolve_provisional_printed_tax_table_interval(taxable_income)
    midpoint_tax, _ = _compute_ordinary_tax_from_taxable_income(
        filing_status=filing_status,
        taxable_income=midpoint,
    )
    rounded_midpoint_tax = _round_whole_dollar_half_up(midpoint_tax)

    return ProvisionalPrintedTaxTableReproductionResult(
        taxable_income=taxable_income,
        interval_lower_bound=lower,
        interval_upper_bound_exclusive=upper,
        midpoint_used=midpoint,
        reproduced_ordinary_tax=rounded_midpoint_tax,
        method_label=PROVISIONAL_PRINTED_TAX_TABLE_METHOD_LABEL,
        fallback_to_exact=False,
    )

def compute_federal_ordinary_tax(scenario: TaxScenarioInput) -> FederalOrdinaryOutput:
    """
    Computes the federal ordinary income tax given a valid scenario.
    Generates a detailed bracket-by-bracket trace.
    """
    
    # 1. Deductions application
    deduction_amount = resolve_deduction_amount(scenario)
    taxable_income = compute_taxable_ordinary_income(
        ordinary_income=scenario.ordinary_income,
        deduction_amount=deduction_amount
    )
    
    # 2. Fetch appropriate bracket rules and compute tax trace
    total_tax, trace = _compute_ordinary_tax_from_taxable_income(
        filing_status=scenario.filing_status,
        taxable_income=taxable_income,
    )
        
    return FederalOrdinaryOutput(
        ordinary_income=scenario.ordinary_income,
        deduction_applied=deduction_amount,
        taxable_ordinary_income=taxable_income,
        total_tax=total_tax,
        bracket_trace=trace
    )