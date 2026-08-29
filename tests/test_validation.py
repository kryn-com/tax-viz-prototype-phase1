import pytest
from pydantic import ValidationError
from models.inputs import TaxScenarioInput, FilingStatus


def test_unsupported_tax_year():
    with pytest.raises(ValidationError) as exc_info:
        TaxScenarioInput(
            tax_year=2025,
            state_code="CA",
            filing_status=FilingStatus.SINGLE,
            ordinary_income=50000,
            taxpayer_age=35,
        )
    assert "Unsupported tax year: 2025" in str(exc_info.value)


def test_invalid_filing_status():
    with pytest.raises(ValidationError) as exc_info:
        TaxScenarioInput(
            tax_year=2026,
            state_code="CA",
            filing_status="divorced",  # Invalid enum
            ordinary_income=50000,
            taxpayer_age=35,
        )
    assert "Input should be 'single', 'married_filing_jointly'" in str(exc_info.value)


def test_valid_taxpayer_age_is_accepted():
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NY",
        filing_status=FilingStatus.SINGLE,
        ordinary_income=50000,
        taxpayer_age=45,
    )

    assert scenario.taxpayer_age == 45


def test_invalid_taxpayer_age_below_range_rejected():
    with pytest.raises(ValidationError) as exc_info:
        TaxScenarioInput(
            tax_year=2026,
            state_code="NY",
            filing_status=FilingStatus.SINGLE,
            ordinary_income=50000,
            taxpayer_age=-1,
        )
    assert "greater than or equal to 0" in str(exc_info.value)


def test_invalid_taxpayer_age_above_range_rejected():
    with pytest.raises(ValidationError) as exc_info:
        TaxScenarioInput(
            tax_year=2026,
            state_code="NY",
            filing_status=FilingStatus.SINGLE,
            ordinary_income=50000,
            taxpayer_age=121,
        )
    assert "less than or equal to 120" in str(exc_info.value)


def test_spouse_age_is_required_for_married_filing_jointly():
    with pytest.raises(ValidationError) as exc_info:
        TaxScenarioInput(
            tax_year=2026,
            state_code="NY",
            filing_status=FilingStatus.MARRIED_FILING_JOINTLY,
            ordinary_income=50000,
            taxpayer_age=45,
        )
    assert "spouse_age is required when filing_status is married_filing_jointly" in str(exc_info.value)


def test_spouse_age_is_optional_for_non_mfj_statuses():
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NY",
        filing_status=FilingStatus.HEAD_OF_HOUSEHOLD,
        ordinary_income=50000,
        taxpayer_age=45,
    )

    assert scenario.spouse_age is None


def test_invalid_supplied_spouse_age_outside_range_rejected():
    with pytest.raises(ValidationError) as exc_info:
        TaxScenarioInput(
            tax_year=2026,
            state_code="NY",
            filing_status=FilingStatus.MARRIED_FILING_JOINTLY,
            ordinary_income=50000,
            taxpayer_age=45,
            spouse_age=121,
        )
    assert "less than or equal to 120" in str(exc_info.value)


def test_negative_deduction_rejection():
    with pytest.raises(ValidationError) as exc_info:
        TaxScenarioInput(
            tax_year=2026,
            state_code="NY",
            filing_status=FilingStatus.SINGLE,
            deduction_amount=-1000.0,
            ordinary_income=50000,
            taxpayer_age=35,
        )
    assert "greater than or equal to 0" in str(exc_info.value)


def test_negative_ordinary_income_rejection():
    with pytest.raises(ValidationError) as exc_info:
        TaxScenarioInput(
            tax_year=2026,
            state_code="NY",
            filing_status=FilingStatus.SINGLE,
            ordinary_income=-500.0,
            taxpayer_age=35,
        )
    assert "Input should be greater than or equal to 0" in str(exc_info.value)
