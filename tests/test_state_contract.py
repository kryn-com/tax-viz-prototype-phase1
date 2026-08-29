from dataclasses import FrozenInstanceError

import pytest
from pydantic import ValidationError

from engines.state_policy import STATE_SUPPORT_POLICY, classify_state, require_supported_state
from engines.state_tax import compute_nc_tax
from models.inputs import FilingStatus, NCDeductionMode, TaxScenarioInput
from models.state import (
    StateTaxRequest,
    StateTaxResult,
    StateTaxSupport,
    UnsupportedStateError,
)
from rules.state_policy import NC_2026_RULES, STATE_TAX_RATES_2026


def test_classifies_explicit_flat_tax_state():
    assert classify_state("PA") is StateTaxSupport.FLAT_TAX
    assert classify_state("NC") is StateTaxSupport.FLAT_TAX
    assert classify_state("IL") is StateTaxSupport.FLAT_TAX
    assert classify_state("IN") is StateTaxSupport.FLAT_TAX
    assert require_supported_state("pa") is StateTaxSupport.FLAT_TAX


def test_flat_tax_policy_has_numeric_rate_for_every_supported_flat_tax_state():
    flat_tax_states = {
        state_code
        for state_code, support in STATE_SUPPORT_POLICY.items()
        if support is StateTaxSupport.FLAT_TAX
    }

    assert flat_tax_states <= STATE_TAX_RATES_2026.keys()


def test_classifies_explicit_no_income_tax_states():
    assert classify_state("FL") is StateTaxSupport.NO_INCOME_TAX
    assert classify_state("TX") is StateTaxSupport.NO_INCOME_TAX
    assert classify_state("WA") is StateTaxSupport.NO_INCOME_TAX
    assert classify_state("NV") is StateTaxSupport.NO_INCOME_TAX
    assert classify_state("SD") is StateTaxSupport.NO_INCOME_TAX
    assert classify_state("WY") is StateTaxSupport.NO_INCOME_TAX


def test_unlisted_state_is_unsupported():
    assert classify_state("MI") is StateTaxSupport.UNSUPPORTED
    assert classify_state("ZZ") is StateTaxSupport.UNSUPPORTED


def test_unsupported_state_raises_clear_error():
    with pytest.raises(UnsupportedStateError, match="MI"):
        require_supported_state("MI")


def test_state_request_and_result_are_typed_without_tax_calculation():
    request = StateTaxRequest(
        tax_year=2026,
        state_code="PA",
        filing_status=FilingStatus.SINGLE,
        state_taxable_income=0.0,
    )
    result = StateTaxResult(
        request=request,
        support=StateTaxSupport.FLAT_TAX,
    )

    assert result.request is request
    assert result.support is StateTaxSupport.FLAT_TAX
    assert result.state_tax_amount is None


def test_state_contract_is_side_effect_free():
    with pytest.raises(FrozenInstanceError):
        request = StateTaxRequest(
            tax_year=2026,
            state_code="PA",
            filing_status=FilingStatus.SINGLE,
            state_taxable_income=0.0,
        )
        request.state_code = "TX"


def test_nc_input_contract_requires_only_approved_fields():
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        taxpayer_age=45,
        federal_agi=120000.0,
        federal_taxable_social_security=5000.0,
        net_nc_interest_dividend_adjustment=-250.0,
        bailey_exempt_pension_amount=None,
        nc_deduction_mode=NCDeductionMode.STANDARD,
        nc_itemized_deduction_amount=None,
    )

    assert scenario.federal_agi == 120000.0
    assert scenario.federal_taxable_social_security == 5000.0
    assert scenario.net_nc_interest_dividend_adjustment == -250.0
    assert scenario.bailey_exempt_pension_amount is None
    assert scenario.nc_deduction_mode is NCDeductionMode.STANDARD
    assert scenario.nc_itemized_deduction_amount is None
    assert "nc_credit_amount" not in TaxScenarioInput.model_fields
    assert "nc_income_tax_before_credits" not in TaxScenarioInput.model_fields


def test_nc_net_interest_dividend_adjustment_allows_signed_values():
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.MARRIED_FILING_JOINTLY,
        taxpayer_age=45,
        spouse_age=42,
        federal_agi=90000.0,
        net_nc_interest_dividend_adjustment=-1200.0,
        nc_deduction_mode=NCDeductionMode.STANDARD,
    )

    assert scenario.net_nc_interest_dividend_adjustment == -1200.0

    scenario_two = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        taxpayer_age=45,
        federal_agi=90000.0,
        net_nc_interest_dividend_adjustment=1200.0,
        nc_deduction_mode=NCDeductionMode.STANDARD,
    )

    assert scenario_two.net_nc_interest_dividend_adjustment == 1200.0


def test_nc_bailey_amount_optional_when_not_applicable():
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        taxpayer_age=60,
        federal_agi=82000.0,
        bailey_exempt_pension_amount=None,
        nc_deduction_mode=NCDeductionMode.STANDARD,
    )
    assert scenario.bailey_exempt_pension_amount is None

    scenario_two = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        taxpayer_age=60,
        federal_agi=82000.0,
        bailey_exempt_pension_amount=4500.0,
        nc_deduction_mode=NCDeductionMode.STANDARD,
    )
    assert scenario_two.bailey_exempt_pension_amount == 4500.0

    with pytest.raises(ValidationError, match="bailey_exempt_pension_amount"):
        TaxScenarioInput(
            tax_year=2026,
            state_code="NC",
            filing_status=FilingStatus.SINGLE,
            taxpayer_age=60,
            federal_agi=82000.0,
            bailey_exempt_pension_amount=-100.0,
            nc_deduction_mode=NCDeductionMode.STANDARD,
        )


def test_nc_deduction_mode_validation_boundaries():
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        taxpayer_age=55,
        federal_agi=100000.0,
        nc_deduction_mode=NCDeductionMode.STANDARD,
    )
    assert scenario.nc_deduction_mode is NCDeductionMode.STANDARD

    itemized = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        taxpayer_age=55,
        federal_agi=100000.0,
        nc_deduction_mode=NCDeductionMode.ITEMIZED,
        nc_itemized_deduction_amount=15000.0,
    )
    assert itemized.nc_itemized_deduction_amount == 15000.0

    with pytest.raises(ValidationError, match="nc_itemized_deduction_amount"):
        TaxScenarioInput(
            tax_year=2026,
            state_code="NC",
            filing_status=FilingStatus.SINGLE,
            taxpayer_age=55,
            federal_agi=100000.0,
            nc_deduction_mode=NCDeductionMode.STANDARD,
            nc_itemized_deduction_amount=15000.0,
        )

    with pytest.raises(ValidationError, match="nc_itemized_deduction_amount"):
        TaxScenarioInput(
            tax_year=2026,
            state_code="NC",
            filing_status=FilingStatus.SINGLE,
            taxpayer_age=55,
            federal_agi=100000.0,
            nc_deduction_mode=NCDeductionMode.ITEMIZED,
            nc_itemized_deduction_amount=None,
        )


def test_nc_rules_are_scaffold_only_with_no_credit_or_engine_fields():
    assert NC_2026_RULES["state_code"] == "NC"
    assert NC_2026_RULES["tax_year"] == 2026
    assert NC_2026_RULES["credits"] == []
    assert "nc_taxable_income" not in TaxScenarioInput.model_fields
    assert "nc_income_tax_before_credits" not in TaxScenarioInput.model_fields
    assert "nc_credit_amount" not in TaxScenarioInput.model_fields


def test_compute_nc_tax_base_case_and_flat_rate():
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        taxpayer_age=45,
        federal_agi=100000.0,
        federal_taxable_social_security=5000.0,
        net_nc_interest_dividend_adjustment=0.0,
        bailey_exempt_pension_amount=None,
        nc_deduction_mode=NCDeductionMode.STANDARD,
    )

    result = compute_nc_tax(scenario)

    expected_standard_deduction = NC_2026_RULES["standard_deduction_by_filing_status"][scenario.filing_status.value]
    expected_taxable_income = 100000.0 - 5000.0 - expected_standard_deduction
    expected_tax = round(expected_taxable_income * 0.0399, 2)

    assert result.nc_taxable_income == expected_taxable_income
    assert result.nc_income_tax_before_credits == expected_tax
    assert result.breakdown["less_federal_taxable_social_security"] == 5000.0
    assert result.breakdown["selected_nc_deduction_amount"] == expected_standard_deduction


def test_compute_nc_tax_handles_taxable_ss_and_signed_adjustments():
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        taxpayer_age=48,
        federal_agi=90000.0,
        federal_taxable_social_security=12000.0,
        net_nc_interest_dividend_adjustment=1500.0,
        bailey_exempt_pension_amount=None,
        nc_deduction_mode=NCDeductionMode.STANDARD,
    )

    result = compute_nc_tax(scenario)
    taxable = 90000.0 - 12000.0 + 1500.0 - NC_2026_RULES["standard_deduction_by_filing_status"][scenario.filing_status.value]
    assert result.nc_taxable_income == taxable
    assert result.breakdown["plus_net_nc_interest_dividend_adjustment"] == 1500.0

    scenario_negative = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        taxpayer_age=49,
        federal_agi=90000.0,
        federal_taxable_social_security=12000.0,
        net_nc_interest_dividend_adjustment=-1500.0,
        bailey_exempt_pension_amount=None,
        nc_deduction_mode=NCDeductionMode.STANDARD,
    )

    negative_result = compute_nc_tax(scenario_negative)
    assert negative_result.breakdown["plus_net_nc_interest_dividend_adjustment"] == -1500.0


def test_compute_nc_tax_handles_bailey_and_deduction_modes():
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        taxpayer_age=60,
        federal_agi=85000.0,
        federal_taxable_social_security=3000.0,
        net_nc_interest_dividend_adjustment=0.0,
        bailey_exempt_pension_amount=2500.0,
        nc_deduction_mode=NCDeductionMode.STANDARD,
    )

    result = compute_nc_tax(scenario)
    expected_standard_deduction = NC_2026_RULES["standard_deduction_by_filing_status"][scenario.filing_status.value]
    expected_taxable = 85000.0 - 3000.0 - 2500.0 - expected_standard_deduction
    assert result.nc_taxable_income == expected_taxable
    assert result.breakdown["less_bailey_exempt_pension_amount"] == 2500.0
    assert result.breakdown["selected_nc_deduction_amount"] == expected_standard_deduction

    itemized = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        taxpayer_age=61,
        federal_agi=85000.0,
        federal_taxable_social_security=3000.0,
        net_nc_interest_dividend_adjustment=0.0,
        bailey_exempt_pension_amount=None,
        nc_deduction_mode=NCDeductionMode.ITEMIZED,
        nc_itemized_deduction_amount=18000.0,
    )

    itemized_result = compute_nc_tax(itemized)
    itemized_expected = 85000.0 - 3000.0 - 18000.0
    assert itemized_result.nc_taxable_income == itemized_expected
    assert itemized_result.breakdown["selected_nc_deduction_amount"] == 18000.0


def test_compute_nc_tax_zero_floors_and_no_credit_fields():
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        taxpayer_age=40,
        federal_agi=8000.0,
        federal_taxable_social_security=2000.0,
        net_nc_interest_dividend_adjustment=0.0,
        bailey_exempt_pension_amount=None,
        nc_deduction_mode=NCDeductionMode.STANDARD,
    )

    result = compute_nc_tax(scenario)
    assert result.nc_taxable_income == 0.0
    assert result.nc_income_tax_before_credits == 0.0
    assert "nc_credit_amount" not in result.__dict__


def test_standard_deduction_varies_by_filing_status():
    single = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        taxpayer_age=45,
        federal_agi=200000.0,
        federal_taxable_social_security=0.0,
        nc_deduction_mode=NCDeductionMode.STANDARD,
    )
    head = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.HEAD_OF_HOUSEHOLD,
        taxpayer_age=45,
        federal_agi=200000.0,
        federal_taxable_social_security=0.0,
        nc_deduction_mode=NCDeductionMode.STANDARD,
    )
    mfj = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.MARRIED_FILING_JOINTLY,
        taxpayer_age=45,
        spouse_age=42,
        federal_agi=200000.0,
        federal_taxable_social_security=0.0,
        nc_deduction_mode=NCDeductionMode.STANDARD,
    )

    assert compute_nc_tax(single).breakdown["selected_nc_deduction_amount"] == 12750.0
    assert compute_nc_tax(head).breakdown["selected_nc_deduction_amount"] == 19125.0
    assert compute_nc_tax(mfj).breakdown["selected_nc_deduction_amount"] == 25500.0


def test_compute_nc_tax_approximate_2025_tie_out_tolerance():
    scenario = TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        taxpayer_age=52,
        federal_agi=82000.0,
        federal_taxable_social_security=10000.0,
        net_nc_interest_dividend_adjustment=-750.0,
        bailey_exempt_pension_amount=0.0,
        nc_deduction_mode=NCDeductionMode.STANDARD,
    )

    result = compute_nc_tax(scenario)
    reference_pre_credit_tax = 2310.0

    assert abs(result.nc_income_tax_before_credits - reference_pre_credit_tax) <= 500.0
    assert result.nc_income_tax_before_credits >= 0.0
