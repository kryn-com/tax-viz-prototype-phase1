import pytest
from models.inputs import TaxScenarioInput, FilingStatus
from engines.social_security import compute_taxable_social_security

def create_ss_scenario(
    status: FilingStatus, 
    ordinary: float, 
    ss_income: float, 
    ltcg: float = 0.0, 
    nontaxable: float = 0.0
) -> TaxScenarioInput:
    """Helper method to construct basic test scenarios with relevant income fields."""
    return TaxScenarioInput(
        tax_year=2026,
        state_code="TX",
        filing_status=status,
        ordinary_income=ordinary,
        social_security_income=ss_income,
        ltcg_qd_income=ltcg,
        nontaxable_income=nontaxable,
        deduction_amount=0.0
    )

def test_single_below_threshold():
    # Ordinary: 10,000 + 0.5 * SS (10,000) = Provisional: 15,000
    # Threshold 1 is 25,000. Expected taxable: 0
    scenario = create_ss_scenario(FilingStatus.SINGLE, ordinary=10000.0, ss_income=10000.0)
    result = compute_taxable_social_security(scenario)
    
    assert result.provisional_income == pytest.approx(15000.0)
    assert result.taxable_social_security == pytest.approx(0.0)
    assert result.tax_free_social_security == pytest.approx(10000.0)
    assert result.total_social_security == pytest.approx(10000.0)

def test_single_middle_band():
    # Ordinary: 25,000 + 0.5 * SS (10,000) = Provisional: 30,000
    # Threshold 1 is 25,000. Excess: 5,000.
    # Taxable = min(0.5 * 10,000, 0.5 * 5,000) -> min(5000, 2500) = 2500
    scenario = create_ss_scenario(FilingStatus.SINGLE, ordinary=25000.0, ss_income=10000.0)
    result = compute_taxable_social_security(scenario)
    
    assert result.provisional_income == pytest.approx(30000.0)
    assert result.taxable_social_security == pytest.approx(2500.0)
    assert result.tax_free_social_security == pytest.approx(7500.0)

def test_mfj_upper_band():
    # Ordinary: 40,000 + 0.5 * SS (20,000) = Provisional: 50,000
    # Threshold 2 is 44,000. Excess: 6,000. Base amount: 6,000.
    # Taxable = min(0.85 * 20,000, (0.85 * 6,000) + 6,000) 
    # -> min(17000, 5100 + 6000) = min(17000, 11100) = 11100
    scenario = create_ss_scenario(FilingStatus.MARRIED_FILING_JOINTLY, ordinary=40000.0, ss_income=20000.0)
    result = compute_taxable_social_security(scenario)
    
    assert result.provisional_income == pytest.approx(50000.0)
    assert result.taxable_social_security == pytest.approx(11100.0)

def test_single_upper_band_small_benefits():
    # Benefits are small (5000), so 50% of benefits (2500) is less than the 4500 base amount.
    # Ordinary: 32,500 + 0.5 * SS (5,000) = Provisional: 35,000
    # Threshold 2 is 34,000. Excess: 1,000.
    # Formula: 0.85 * 1000 + min(4500, 0.5 * 5000) = 850 + 2500 = 3350.
    # Max cap: 0.85 * 5000 = 4250. Result should be 3350, not the 4250 that the old bug would have yielded.
    scenario = create_ss_scenario(FilingStatus.SINGLE, ordinary=32500.0, ss_income=5000.0)
    result = compute_taxable_social_security(scenario)
    
    assert result.provisional_income == pytest.approx(35000.0)
    assert result.taxable_social_security == pytest.approx(3350.0)

def test_hoh_uses_single_thresholds():
    # Identical to single_middle_band, should produce same result.
    scenario = create_ss_scenario(FilingStatus.HEAD_OF_HOUSEHOLD, ordinary=25000.0, ss_income=10000.0)
    result = compute_taxable_social_security(scenario)
    
    assert result.provisional_income == pytest.approx(30000.0)
    assert result.taxable_social_security == pytest.approx(2500.0)

def test_mfs_raises_not_implemented():
    # MFS has complicated logic depending on living situation, out of scope.
    scenario = create_ss_scenario(FilingStatus.MARRIED_FILING_SEPARATELY, ordinary=50000.0, ss_income=10000.0)
    
    with pytest.raises(NotImplementedError, match="permanently out of scope"):
        compute_taxable_social_security(scenario)