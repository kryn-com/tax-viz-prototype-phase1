import pytest
from models.inputs import TaxScenarioInput, FilingStatus
from engines.ltcg_qd import compute_preferential_tax

def create_ltcg_scenario(
    status: FilingStatus, 
    ordinary: float, 
    ltcg: float, 
    deduction: float = 0.0
) -> TaxScenarioInput:
    """Helper method to construct LTCG test scenarios."""
    return TaxScenarioInput(
        tax_year=2026,
        state_code="TX",
        filing_status=status,
        ordinary_income=ordinary,
        ltcg_qd_income=ltcg,
        deduction_amount=deduction
    )

def test_zero_preferential_income():
    scenario = create_ltcg_scenario(FilingStatus.SINGLE, ordinary=50000.0, ltcg=0.0)
    result = compute_preferential_tax(scenario)
    
    assert result.total_preferential_income == 0.0
    assert result.total_preferential_tax == 0.0
    assert result.taxed_at_0 == 0.0

def test_preferential_fully_in_zero_band():
    # Single threshold_15 is 49,450. 
    # Base income 20,000 + 10,000 LTCG = 30,000 total. All 10k fits in 0%.
    scenario = create_ltcg_scenario(FilingStatus.SINGLE, ordinary=20000.0, ltcg=10000.0)
    result = compute_preferential_tax(scenario)
    
    assert result.taxed_at_0 == pytest.approx(10000.0)
    assert result.taxed_at_15 == 0.0
    assert result.total_preferential_tax == 0.0

def test_preferential_split_zero_and_15():
    # Single threshold_15 is 49,450.
    # Base income 40,000. LTCG 20,000.
    # 0% band fits: 49,450 - 40,000 = 9,450.
    # 15% band gets the rest: 20,000 - 9,450 = 10,550.
    scenario = create_ltcg_scenario(FilingStatus.SINGLE, ordinary=40000.0, ltcg=20000.0)
    result = compute_preferential_tax(scenario)
    
    assert result.taxed_at_0 == pytest.approx(9450.0)
    assert result.taxed_at_15 == pytest.approx(10550.0)
    assert result.taxed_at_20 == 0.0
    assert result.total_preferential_tax == pytest.approx(10550.0 * 0.15)

def test_preferential_reaching_20_band():
    # MFJ threshold_15 is 98,900. threshold_20 is 613,700.
    # Base income 500,000. LTCG 200,000.
    # Base income skips the 0% band completely.
    # 15% band capacity: 613,700 - 500,000 = 113,700.
    # 20% band gets the rest: 200,000 - 113,700 = 86,300.
    scenario = create_ltcg_scenario(FilingStatus.MARRIED_FILING_JOINTLY, ordinary=500000.0, ltcg=200000.0)
    result = compute_preferential_tax(scenario)
    
    assert result.taxed_at_0 == 0.0
    assert result.taxed_at_15 == pytest.approx(113700.0)
    assert result.taxed_at_20 == pytest.approx(86300.0)
    
    expected_tax = (113700.0 * 0.15) + (86300.0 * 0.20)
    assert result.total_preferential_tax == pytest.approx(expected_tax)

def test_hoh_behavior():
    # HOH threshold_15 is 66,200.
    # Base income 50,000. LTCG 20,000.
    # 0% capacity: 66,200 - 50,000 = 16,200.
    # 15% gets remainder: 3,800.
    scenario = create_ltcg_scenario(FilingStatus.HEAD_OF_HOUSEHOLD, ordinary=50000.0, ltcg=20000.0)
    result = compute_preferential_tax(scenario)
    
    assert result.taxed_at_0 == pytest.approx(16200.0)
    assert result.taxed_at_15 == pytest.approx(3800.0)
    assert result.total_preferential_tax == pytest.approx(3800.0 * 0.15)

def test_mfs_raises_not_implemented():
    scenario = create_ltcg_scenario(FilingStatus.MARRIED_FILING_SEPARATELY, ordinary=50000.0, ltcg=10000.0)
    
    with pytest.raises(NotImplementedError, match="permanently out of scope"):
        compute_preferential_tax(scenario)

def test_deduction_reduces_ordinary_base():
    # SINGLE, ord=50k, ded=10k -> taxable ord=40k
    # T15 = 49450. 0% capacity = 9450.
    # LTCG = 10000.
    # taxed_at_0 = 9450
    # taxed_at_15 = 550
    # taxed_at_20 = 0
    # total_tax = 550 * 0.15 = 82.50
    scenario = create_ltcg_scenario(
        status=FilingStatus.SINGLE, 
        ordinary=50000.0, 
        ltcg=10000.0, 
        deduction=10000.0
    )
    result = compute_preferential_tax(scenario)
    
    assert result.taxed_at_0 == pytest.approx(9450.0)
    assert result.taxed_at_15 == pytest.approx(550.0)
    assert result.taxed_at_20 == 0.0
    assert result.total_preferential_tax == pytest.approx(82.50)