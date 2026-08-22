from copy import deepcopy
from dataclasses import FrozenInstanceError

import pytest

from engines.federal_orchestrator import orchestrate_federal_tax
from models.inputs import DeductionMode, FilingStatus, TaxScenarioInput
from presentation.tax_stack_data import build_federal_tax_stack_view_model


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


def test_build_federal_tax_stack_view_model_maps_complete_result():
    result = orchestrate_federal_tax(create_scenario())

    model = build_federal_tax_stack_view_model(result)

    assert model.tax_year == result.scenario.tax_year
    assert model.filing_status is result.scenario.filing_status
    assert model.ordinary_income == result.ordinary_output.ordinary_income
    assert model.taxable_ordinary_income == result.taxable_ordinary_income
    assert model.preferential_income == result.taxable_preferential_income
    assert model.deduction_shielding_amount == result.ordinary_output.deduction_applied
    assert model.agi == result.agi
    assert model.magi == result.magi
    assert model.ordinary_tax == result.ordinary_tax
    assert model.ltcg_qd_tax == result.ltcg_qd_tax
    assert model.total_federal_tax == result.total_federal_tax


def test_build_federal_tax_stack_view_model_maps_deduction_shielding():
    result = orchestrate_federal_tax(
        create_scenario(
            deduction_mode=DeductionMode.EXPLICIT,
            deduction_amount=12345.0,
        )
    )

    model = build_federal_tax_stack_view_model(result)

    assert model.deduction_shielding_amount == 12345.0
    assert model.deduction_shielding_amount == result.ordinary_output.deduction_applied


def test_build_federal_tax_stack_view_model_preserves_ordinary_layer_order_and_values():
    result = orchestrate_federal_tax(create_scenario())

    model = build_federal_tax_stack_view_model(result)

    assert [layer.rate for layer in model.ordinary_marginal_layers] == [
        item.rate for item in result.ordinary_output.bracket_trace
    ]
    assert [layer.taxed_amount for layer in model.ordinary_marginal_layers] == [
        item.taxed_amount for item in result.ordinary_output.bracket_trace
    ]
    assert [layer.tax_generated for layer in model.ordinary_marginal_layers] == [
        item.tax_generated for item in result.ordinary_output.bracket_trace
    ]


def test_build_federal_tax_stack_view_model_preserves_preferential_layer_order():
    result = orchestrate_federal_tax(create_scenario())

    model = build_federal_tax_stack_view_model(result)

    assert [(layer.rate, layer.taxed_amount) for layer in model.preferential_rate_layers] == [
        (0.0, result.ltcg_qd_output.taxed_at_0),
        (0.15, result.ltcg_qd_output.taxed_at_15),
        (0.20, result.ltcg_qd_output.taxed_at_20),
    ]


def test_build_federal_tax_stack_view_model_maps_social_security_explanation():
    result = orchestrate_federal_tax(create_scenario())

    model = build_federal_tax_stack_view_model(result)

    assert model.social_security.total_social_security == result.ss_output.total_social_security
    assert model.social_security.taxable_social_security == result.ss_output.taxable_social_security
    assert model.social_security.tax_free_social_security == result.ss_output.tax_free_social_security
    assert model.social_security.provisional_income == result.ss_output.provisional_income


def test_build_federal_tax_stack_view_model_maps_niit_notice_fields():
    result = orchestrate_federal_tax(create_scenario())

    model = build_federal_tax_stack_view_model(result)

    assert model.niit.net_investment_income == result.niit_output.net_investment_income
    assert model.niit.magi == result.niit_output.magi
    assert model.niit.threshold_applied == result.niit_output.threshold_applied
    assert model.niit.magi_over_threshold == result.niit_output.magi_over_threshold
    assert model.niit.tax_base == result.niit_output.tax_base
    assert model.niit.niit_rate == result.niit_output.niit_rate
    assert model.niit.niit_tax == result.niit_output.niit_tax


def test_build_federal_tax_stack_view_model_preserves_zero_layers_and_values():
    result = orchestrate_federal_tax(
        create_scenario(
            ordinary_income=0.0,
            ltcg_qd_income=0.0,
            social_security_income=0.0,
            deduction_mode=DeductionMode.EXPLICIT,
            deduction_amount=0.0,
        )
    )

    model = build_federal_tax_stack_view_model(result)

    assert model.ordinary_marginal_layers
    assert all(layer.taxed_amount == 0.0 for layer in model.ordinary_marginal_layers)
    assert all(layer.tax_generated == 0.0 for layer in model.ordinary_marginal_layers)
    assert [(layer.rate, layer.taxed_amount) for layer in model.preferential_rate_layers] == [
        (0.0, 0.0),
        (0.15, 0.0),
        (0.20, 0.0),
    ]
    assert model.social_security.taxable_social_security == 0.0
    assert model.niit.niit_tax == 0.0


def test_build_federal_tax_stack_view_model_is_deterministic():
    result = orchestrate_federal_tax(create_scenario())

    assert build_federal_tax_stack_view_model(result) == build_federal_tax_stack_view_model(result)


def test_tax_stack_dataclasses_are_immutable():
    result = orchestrate_federal_tax(create_scenario())
    model = build_federal_tax_stack_view_model(result)

    with pytest.raises(FrozenInstanceError):
        model.deduction_shielding_amount = 1.0
    with pytest.raises(FrozenInstanceError):
        model.social_security.taxable_social_security = 1.0
    with pytest.raises(FrozenInstanceError):
        model.niit.niit_tax = 1.0


def test_build_federal_tax_stack_view_model_does_not_mutate_source_result():
    result = orchestrate_federal_tax(create_scenario())
    before = deepcopy(result)

    build_federal_tax_stack_view_model(result)

    assert result == before
