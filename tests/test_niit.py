import pytest
from models.inputs import FilingStatus
from engines.niit import compute_niit

def test_below_threshold_returns_zero_tax():
    result = compute_niit(FilingStatus.SINGLE, magi=150000.0, net_investment_income=50000.0)
    assert result.niit_tax == 0.0
    assert result.tax_base == 0.0

def test_tax_base_limited_by_net_investment_income():
    # MAGI over threshold by 100k, NII is only 20k. Base should be 20k.
    result = compute_niit(FilingStatus.SINGLE, magi=300000.0, net_investment_income=20000.0)
    assert result.tax_base == 20000.0
    assert result.niit_tax == pytest.approx(20000.0 * 0.038)

def test_tax_base_limited_by_magi_excess():
    # MAGI over threshold by 10k, NII is 50k. Base should be 10k.
    result = compute_niit(FilingStatus.SINGLE, magi=210000.0, net_investment_income=50000.0)
    assert result.tax_base == 10000.0
    assert result.niit_tax == pytest.approx(10000.0 * 0.038)

def test_mfj_uses_250000_threshold():
    # MAGI is 260k, threshold is 250k. Excess is 10k.
    result = compute_niit(FilingStatus.MARRIED_FILING_JOINTLY, magi=260000.0, net_investment_income=50000.0)
    assert result.threshold_applied == 250000.0
    assert result.magi_over_threshold == 10000.0
    assert result.tax_base == 10000.0

def test_mfs_raises_not_implemented_error():
    with pytest.raises(NotImplementedError, match="Married Filing Separately is not implemented."):
        compute_niit(FilingStatus.MARRIED_FILING_SEPARATELY, magi=200000.0, net_investment_income=10000.0)