import pytest
from models.inputs import TaxScenarioInput, FilingStatus
from engines.federal_ordinary import compute_federal_ordinary_tax

def create_base_scenario(income: float, deduction: float, status: FilingStatus = FilingStatus.SINGLE) -> TaxScenarioInput:
    return TaxScenarioInput(
        tax_year=2026,
        state_code="TX",
        filing_status=status,
        ordinary_income=income,
        deduction_amount=deduction
    )

def test_zero_taxable_income():
    scenario = create_base_scenario(income=40000, deduction=50000)
    result = compute_federal_ordinary_tax(scenario)
    
    assert result.taxable_ordinary_income == 0.0
    assert result.total_tax == 0.0
    # Confirm the trace still returns bounds but zeroed values
    for slice in result.bracket_trace:
        assert slice.taxed_amount == 0.0
        assert slice.tax_generated == 0.0

def test_positive_taxable_income_one_bracket():
    scenario = create_base_scenario(income=15000, deduction=5000)
    result = compute_federal_ordinary_tax(scenario)
    
    assert result.taxable_ordinary_income == 10000.0
    # Single bracket 10%: 10000 * 0.10 = 1000
    assert result.total_tax == 1000.0
    assert result.bracket_trace[0].taxed_amount == 10000.0
    assert result.bracket_trace[0].tax_generated == 1000.0
    assert result.bracket_trace[1].taxed_amount == 0.0

def test_taxable_income_spanning_multiple_brackets():
    # taxable = 60000 (Single)
    # Brackets: 10% up to 11600 (1160 tax)
    #           12% 11600 to 47150 (35550 * 0.12 = 4266 tax)
    #           22% 47150 to 100525 (12850 * 0.22 = 2827 tax)
    # Total = 1160 + 4266 + 2827 = 8253
    scenario = create_base_scenario(income=70000, deduction=10000)
    result = compute_federal_ordinary_tax(scenario)
    
    assert result.taxable_ordinary_income == 60000.0
    assert pytest.approx(result.total_tax, 0.01) == 8253.0
    
    assert result.bracket_trace[0].taxed_amount == 11600.0
    assert result.bracket_trace[1].taxed_amount == 35550.0
    assert result.bracket_trace[2].taxed_amount == 12850.0
    assert result.bracket_trace[3].taxed_amount == 0.0

def test_exact_threshold_boundary():
    # Exactly on the line of the first bracket (11600)
    scenario = create_base_scenario(income=11600, deduction=0)
    result = compute_federal_ordinary_tax(scenario)
    
    assert result.taxable_ordinary_income == 11600.0
    assert result.total_tax == 1160.0
    assert result.bracket_trace[0].taxed_amount == 11600.0
    assert result.bracket_trace[1].taxed_amount == 0.0

def test_deterministic_repeated_runs():
    scenario = create_base_scenario(income=200000, deduction=15000, status=FilingStatus.MARRIED_FILING_JOINTLY)
    
    run_1 = compute_federal_ordinary_tax(scenario)
    run_2 = compute_federal_ordinary_tax(scenario)
    
    assert run_1.total_tax == run_2.total_tax
    assert run_1.taxable_ordinary_income == run_2.taxable_ordinary_income
    assert run_1.bracket_trace == run_2.bracket_trace