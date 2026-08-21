from models.state import StateTaxSupport, UnsupportedStateError


STATE_SUPPORT_POLICY = {
    "PA": StateTaxSupport.FLAT_TAX,
    "FL": StateTaxSupport.NO_INCOME_TAX,
    "TX": StateTaxSupport.NO_INCOME_TAX,
}


def classify_state(state_code: str) -> StateTaxSupport:
    normalized_state_code = state_code.upper()
    return STATE_SUPPORT_POLICY.get(
        normalized_state_code,
        StateTaxSupport.UNSUPPORTED,
    )


def require_supported_state(state_code: str) -> StateTaxSupport:
    support = classify_state(state_code)
    if support is StateTaxSupport.UNSUPPORTED:
        raise UnsupportedStateError(
            f"State tax policy is unsupported for state code: {state_code.upper()}"
        )
    return support
