import pytest

from engines.state_tax import compute_state_tax
from models.inputs import FilingStatus
from models.state import StateTaxRequest, StateTaxSupport, UnsupportedStateError


def create_state_request(
    state_code: str,
    state_taxable_income: float,
    filing_status: FilingStatus = FilingStatus.SINGLE,
) -> StateTaxRequest:
    return StateTaxRequest(
        tax_year=2026,
        state_code=state_code,
        filing_status=filing_status,
        state_taxable_income=state_taxable_income,
    )


@pytest.mark.parametrize(
    ("state_code", "rate"),
    [
        ("PA", 0.0307),
        ("NC", 0.0399),
        ("IL", 0.0495),
        ("IN", 0.029),
    ],
)
def test_flat_tax_known_base_calculation(state_code, rate):
    result = compute_state_tax(create_state_request(state_code, 100000.0))

    assert result.support is StateTaxSupport.FLAT_TAX
    assert result.state_tax_amount == pytest.approx(100000.0 * rate)


def test_pa_zero_base():
    result = compute_state_tax(create_state_request("PA", 0.0))

    assert result.state_tax_amount == 0.0


@pytest.mark.parametrize("state_code", ["FL", "TX", "WA", "NV", "SD", "WY"])
def test_no_income_tax_states_return_explicit_zero(state_code):
    result = compute_state_tax(create_state_request(state_code, 100000.0))

    assert result.support is StateTaxSupport.NO_INCOME_TAX
    assert result.state_tax_amount == 0.0


@pytest.mark.parametrize("state_code", ["MI", "ZZ"])
def test_unsupported_states_raise(state_code):
    with pytest.raises(UnsupportedStateError, match=state_code):
        compute_state_tax(create_state_request(state_code, 100000.0))


def test_negative_state_taxable_income_is_rejected():
    with pytest.raises(ValueError, match="State taxable income cannot be negative"):
        create_state_request("PA", -1.0)


def test_result_preserves_request_and_filing_status():
    request = create_state_request(
        "PA",
        50000.0,
        filing_status=FilingStatus.MARRIED_FILING_JOINTLY,
    )

    result = compute_state_tax(request)

    assert result.request is request
    assert result.request.filing_status is FilingStatus.MARRIED_FILING_JOINTLY


def test_repeated_calculations_are_deterministic():
    request = create_state_request("PA", 75000.0)

    first = compute_state_tax(request)
    second = compute_state_tax(request)

    assert first == second