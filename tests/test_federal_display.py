from engines.federal_orchestrator import orchestrate_federal_tax
from models.inputs import DeductionMode, FilingStatus, TaxScenarioInput
from presentation.federal_display import build_federal_display_model


def create_scenario(**overrides):
    values = {
        "tax_year": 2026,
        "state_code": "NC",
        "filing_status": FilingStatus.SINGLE,
        "ordinary_income": 60000.0,
        "ltcg_qd_income": 20000.0,
        "social_security_income": 30000.0,
        "nontaxable_income": 0.0,
        "deduction_mode": DeductionMode.STANDARD,
    }
    values.update(overrides)
    return TaxScenarioInput(**values)


def test_build_federal_display_model_maps_core_federal_totals():
    result = orchestrate_federal_tax(create_scenario())

    display = build_federal_display_model(result)

    assert display.tax_year == result.scenario.tax_year
    assert display.filing_status is result.scenario.filing_status
    assert display.ordinary_income == result.ordinary_output.ordinary_income
    assert display.taxable_social_security == result.ss_output.taxable_social_security
    assert display.tax_free_social_security == result.ss_output.tax_free_social_security
    assert display.taxable_ordinary_income == result.taxable_ordinary_income
    assert display.preferential_income == result.taxable_preferential_income
    assert display.agi == result.agi
    assert display.magi == result.magi
    assert display.ordinary_tax == result.ordinary_tax
    assert display.ltcg_qd_tax == result.ltcg_qd_tax
    assert display.niit_tax == result.niit_tax
    assert display.total_federal_tax == result.total_federal_tax


def test_build_federal_display_model_preserves_ordinary_bracket_slices():
    result = orchestrate_federal_tax(create_scenario())

    display = build_federal_display_model(result)

    assert len(display.ordinary_bracket_slices) == len(result.ordinary_output.bracket_trace)
    for display_slice, result_slice in zip(
        display.ordinary_bracket_slices,
        result.ordinary_output.bracket_trace,
    ):
        assert display_slice.rate == result_slice.rate
        assert display_slice.lower_bound == result_slice.lower_bound
        assert display_slice.upper_bound == result_slice.upper_bound
        assert display_slice.taxed_amount == result_slice.taxed_amount
        assert display_slice.tax_generated == result_slice.tax_generated


def test_build_federal_display_model_maps_preferential_rate_slices():
    result = orchestrate_federal_tax(create_scenario())

    display = build_federal_display_model(result)

    assert [(item.rate, item.taxed_amount) for item in display.preferential_rate_slices] == [
        (0.0, result.ltcg_qd_output.taxed_at_0),
        (0.15, result.ltcg_qd_output.taxed_at_15),
        (0.20, result.ltcg_qd_output.taxed_at_20),
    ]


def test_build_federal_display_model_is_deterministic():
    result = orchestrate_federal_tax(create_scenario())

    first = build_federal_display_model(result)
    second = build_federal_display_model(result)

    assert first == second


def test_build_federal_display_model_handles_zero_income():
    result = orchestrate_federal_tax(
        create_scenario(
            ordinary_income=0.0,
            ltcg_qd_income=0.0,
            social_security_income=0.0,
        )
    )

    display = build_federal_display_model(result)

    assert display.ordinary_income == 0.0
    assert display.taxable_social_security == 0.0
    assert display.tax_free_social_security == 0.0
    assert display.taxable_ordinary_income == 0.0
    assert display.preferential_income == 0.0
    assert display.agi == 0.0
    assert display.magi == 0.0
    assert display.ordinary_tax == 0.0
    assert display.ltcg_qd_tax == 0.0
    assert display.niit_tax == 0.0
    assert display.total_federal_tax == 0.0
    assert len(display.ordinary_bracket_slices) == len(result.ordinary_output.bracket_trace)
    assert all(item.taxed_amount == 0.0 for item in display.ordinary_bracket_slices)
    assert all(item.tax_generated == 0.0 for item in display.ordinary_bracket_slices)
    assert [item.taxed_amount for item in display.preferential_rate_slices] == [0.0, 0.0, 0.0]