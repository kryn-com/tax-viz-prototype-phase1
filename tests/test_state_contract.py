from dataclasses import FrozenInstanceError

import pytest

from engines.state_policy import STATE_SUPPORT_POLICY, classify_state, require_supported_state
from models.inputs import FilingStatus
from models.state import (
    StateTaxRequest,
    StateTaxResult,
    StateTaxSupport,
    UnsupportedStateError,
)
from rules.state_policy import STATE_TAX_RATES_2026


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
