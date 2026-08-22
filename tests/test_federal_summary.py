from models.federal_display import FederalDisplayModel
from presentation.federal_display import build_federal_display_model
from presentation.federal_summary import render_federal_summary

from tests.test_federal_display import create_scenario
from engines.federal_orchestrator import orchestrate_federal_tax


def test_render_federal_summary_has_expected_populated_blocks():
    result = orchestrate_federal_tax(create_scenario())
    summary = render_federal_summary(build_federal_display_model(result))

    assert "Taxable ordinary income: $" in summary
    assert "Ordinary tax: $" in summary
    assert "Taxable Social Security: $" in summary
    assert "LTCG/qualified dividend income: $" in summary
    assert "Preferential tax: $" in summary
    assert "NIIT tax: $" in summary
    assert "Total federal tax: $" in summary
    assert "Ordinary bracket slices:\n- rate=" in summary
    assert "Preferential rate slices:\n- rate=" in summary
    assert "- none" not in summary


def test_render_federal_summary_handles_zero_values_and_empty_slices():
    model = FederalDisplayModel(
        tax_year=2026,
        filing_status=create_scenario().filing_status,
        ordinary_income=0.0,
        taxable_social_security=0.0,
        tax_free_social_security=0.0,
        taxable_ordinary_income=0.0,
        preferential_income=0.0,
        agi=0.0,
        magi=0.0,
        ordinary_tax=0.0,
        ltcg_qd_tax=0.0,
        niit_tax=0.0,
        total_federal_tax=0.0,
        ordinary_bracket_slices=(),
        preferential_rate_slices=(),
    )

    summary = render_federal_summary(model)

    assert "Taxable ordinary income: $0.00" in summary
    assert "Total federal tax: $0.00" in summary
    assert "Ordinary bracket slices:\n- none" in summary
    assert "Preferential rate slices:\n- none" in summary


def test_render_federal_summary_is_deterministic():
    result = orchestrate_federal_tax(create_scenario())
    model = build_federal_display_model(result)

    assert render_federal_summary(model) == render_federal_summary(model)
