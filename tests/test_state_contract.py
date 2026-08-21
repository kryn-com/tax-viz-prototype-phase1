from dataclasses import FrozenInstanceError

import pytest

from engines.state_policy import classify_state, require_supported_state
from models.inputs import FilingStatus
from models.state import (
    StateTaxRequest,
    StateTaxResult,
    StateTaxSupport,
    UnsupportedStateError,
)


def test_classifies_explicit_flat_tax_state():
    assert classify_state("PA") is StateTaxSupport.FLAT_TAX
    assert require_supported_state("pa") is StateTaxSupport.FLAT_TAX


def test_classifies_explicit_no_income_tax_states():
    assert classify_state("FL") is StateTaxSupport.NO_INCOME_TAX
    assert classify_state("TX") is StateTaxSupport.NO_INCOME_TAX


def test_unlisted_state_is_unsupported():
    assert classify_state("NC") is StateTaxSupport.UNSUPPORTED
    assert classify_state("ZZ") is StateTaxSupport.UNSUPPORTED


def test_unsupported_state_raises_clear_error():
    with pytest.raises(UnsupportedStateError, match="NC"):
        require_supported_state("NC")


def test_state_request_and_result_are_typed_without_tax_calculation():
    request = StateTaxRequest(
        tax_year=2026,
        state_code="PA",
        filing_status=FilingStatus.SINGLE,
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
        )
        request.state_code = "TX"
