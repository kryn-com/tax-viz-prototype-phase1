import pytest
from models.inputs import TaxScenarioInput, FilingStatus
from engines.social_security import compute_taxable_social_security

def test_social_security_placeholder_raises_error():
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="TX",
        filing_status=FilingStatus.SINGLE,
        social_security_income=15000.0,
        ordinary_income=50000.0
    )
    
    with pytest.raises(NotImplementedError) as exc_info:
        compute_taxable_social_security(scenario)
        
    assert "Social Security taxability calculation is not yet implemented." in str(exc_info.value)