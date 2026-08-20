from models.outputs import BracketSlice, FederalOrdinaryOutput
from models.inputs import TaxScenarioInput
from rules.federal.year_2026 import get_brackets_for_status
from engines.deductions import compute_taxable_ordinary_income

def compute_federal_ordinary_tax(scenario: TaxScenarioInput) -> FederalOrdinaryOutput:
    """
    Computes the federal ordinary income tax given a valid scenario.
    Generates a detailed bracket-by-bracket trace.
    """
    
    # 1. Deductions application
    taxable_income = compute_taxable_ordinary_income(
        ordinary_income=scenario.ordinary_income,
        deduction_amount=scenario.deduction_amount
    )
    
    # 2. Fetch appropriate bracket rules
    brackets = get_brackets_for_status(scenario.filing_status)
    
    total_tax = 0.0
    trace = []
    
    # 3. Traverse brackets and calculate tax slices
    for bracket in brackets:
        lower = bracket["lower"]
        upper = bracket["upper"]
        rate = bracket["rate"]
        
        # If the taxable income hasn't reached this bracket, we log an empty slice and continue
        # Logging empty slices gives full context in the trace output for visualization later.
        if taxable_income <= lower:
            trace.append(BracketSlice(
                rate=rate,
                lower_bound=lower,
                upper_bound=upper,
                taxed_amount=0.0,
                tax_generated=0.0
            ))
            continue
            
        # Calculate how much income falls into this specific slice
        if upper is None:
            # Uncapped top bracket
            taxed_amount = taxable_income - lower
        else:
            # Bound bracket
            taxed_amount = min(taxable_income, upper) - lower
            
        tax_generated = taxed_amount * rate
        total_tax += tax_generated
        
        trace.append(BracketSlice(
            rate=rate,
            lower_bound=lower,
            upper_bound=upper,
            taxed_amount=taxed_amount,
            tax_generated=tax_generated
        ))
        
    return FederalOrdinaryOutput(
        ordinary_income=scenario.ordinary_income,
        deduction_applied=scenario.deduction_amount,
        taxable_ordinary_income=taxable_income,
        total_tax=total_tax,
        bracket_trace=trace
    )