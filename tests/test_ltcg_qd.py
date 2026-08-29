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
        taxpayer_age=45,
        ordinary_income=ordinary,
        ltcg_qd_income=ltcg,
        deduction_amount=deduction,
        spouse_age=45 if status is FilingStatus.MARRIED_FILING_JOINTLY else None,
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
    scenario = create_ltcg_scenario(FilingStatus.SINGLE, ordinary=40000.0, ltcg=20000.0)
    result = compute_preferential_tax(scenario)

    assert result.taxed_at_0 == pytest.approx(20000.0)
    assert result.taxed_at_15 == pytest.approx(0.0)
    assert result.taxed_at_20 == 0.0
    assert result.total_preferential_tax == pytest.approx(0.0)

def test_preferential_reaching_20_band():
    scenario = create_ltcg_scenario(
        FilingStatus.MARRIED_FILING_JOINTLY,
        ordinary=500000.0,
        ltcg=200000.0,
    )
    result = compute_preferential_tax(scenario)

    assert result.taxed_at_0 == 0.0
    assert result.taxed_at_15 == pytest.approx(145900.0)
    assert result.taxed_at_20 == pytest.approx(54100.0)

    expected_tax = (145900.0 * 0.15) + (54100.0 * 0.20)
    assert result.total_preferential_tax == pytest.approx(expected_tax)

def test_hoh_behavior():
    # HOH threshold_15 is 66,200.
    # Ordinary income is 50,000; the HOH standard deduction is 24,150.
    # Taxable ordinary base = 25,850.
    # 0% capacity = 66,200 - 25,850 = 40,350.
    # LTCG is 20,000, so all of it is taxed at 0%.
    scenario = create_ltcg_scenario(
        FilingStatus.HEAD_OF_HOUSEHOLD,
        ordinary=50000.0,
        ltcg=20000.0,
    )
    result = compute_preferential_tax(scenario)

    assert result.taxed_at_0 == pytest.approx(20000.0)
    assert result.taxed_at_15 == pytest.approx(0.0)
    assert result.taxed_at_20 == pytest.approx(0.0)
    assert result.total_preferential_tax == pytest.approx(0.0)

def test_mfs_raises_not_implemented():
    scenario = create_ltcg_scenario(FilingStatus.MARRIED_FILING_SEPARATELY, ordinary=50000.0, ltcg=10000.0)
    
    with pytest.raises(NotImplementedError, match="permanently out of scope"):
        compute_preferential_tax(scenario)

def test_deduction_floor_reduces_ordinary_base_for_preferential_stacking():
    # SINGLE, ord=50k, explicit ded=10k -> applied ded floors to 16.1k
    # taxable ord = 33.9k
    # T15 = 49.45k, so 0% capacity = 15.55k
    # LTCG = 10k, all taxed at 0%
    scenario = create_ltcg_scenario(
        status=FilingStatus.SINGLE,
        ordinary=50000.0,
        ltcg=10000.0,
        deduction=10000.0,
    )
    result = compute_preferential_tax(scenario)

    assert result.taxed_at_0 == pytest.approx(10000.0)
    assert result.taxed_at_15 == pytest.approx(0.0)
    assert result.taxed_at_20 == 0.0
    assert result.total_preferential_tax == pytest.approx(0.0)