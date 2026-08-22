from models.sliver_display import FederalSliverDisplayModel
from presentation.sliver_display import (
    build_federal_combined_sliver_display_model,
    build_federal_ltcg_qd_sliver_display_model,
    build_federal_sliver_display_model,
)
from presentation.sliver_summary import render_federal_sliver_summary
from tests.test_sliver_analysis import create_sliver_scenario
from engines.sliver_analysis import (
    analyze_combined_income_sliver,
    analyze_ltcg_qd_sliver,
    analyze_ordinary_income_sliver,
)


def test_render_federal_sliver_summary_includes_baseline_and_altered_totals():
    result = analyze_ordinary_income_sliver(create_sliver_scenario(), increment=1000.0)
    model = build_federal_sliver_display_model(result)
    summary = render_federal_sliver_summary(model)

    assert "Result type: ordinary_income" in summary
    assert "Baseline federal tax:" in summary
    assert "Altered federal tax:" in summary
    assert "Federal tax delta:" in summary
    assert "Ordinary income increment:" in summary


def test_render_federal_sliver_summary_handles_zero_and_delta_values():
    model = FederalSliverDisplayModel(
        tax_year=2026,
        filing_status=create_sliver_scenario().filing_status,
        result_kind="combined_income",
        baseline_total_federal_tax=0.0,
        altered_total_federal_tax=0.0,
        federal_tax_delta=0.0,
        ordinary_income_increment=0.0,
        ltcg_qd_income_increment=0.0,
    )

    summary = render_federal_sliver_summary(model)

    assert "Baseline federal tax: $0.00" in summary
    assert "Altered federal tax: $0.00" in summary
    assert "Federal tax delta: $0.00" in summary
    assert "Result type: combined_income" in summary


def test_render_federal_sliver_summary_is_deterministic():
    result = analyze_combined_income_sliver(
        create_sliver_scenario(),
        ordinary_income_increment=1000.0,
        ltcg_qd_income_increment=2000.0,
    )
    model = build_federal_combined_sliver_display_model(result)

    assert render_federal_sliver_summary(model) == render_federal_sliver_summary(model)


def test_sliver_display_builders_cover_supported_variants():
    scenario = create_sliver_scenario()

    ordinary_result = analyze_ordinary_income_sliver(scenario, increment=1000.0)
    ltcg_result = analyze_ltcg_qd_sliver(scenario, increment=1000.0)
    combined_result = analyze_combined_income_sliver(
        scenario,
        ordinary_income_increment=1000.0,
        ltcg_qd_income_increment=2000.0,
    )

    ordinary_model = build_federal_sliver_display_model(ordinary_result)
    ltcg_model = build_federal_ltcg_qd_sliver_display_model(ltcg_result)
    combined_model = build_federal_combined_sliver_display_model(combined_result)

    assert ordinary_model.result_kind == "ordinary_income"
    assert ltcg_model.result_kind == "ltcg_qd_income"
    assert combined_model.result_kind == "combined_income"
    assert ordinary_model.ordinary_income_increment == 1000.0
    assert ltcg_model.ltcg_qd_income_increment == 1000.0
    assert combined_model.ordinary_income_increment == 1000.0
    assert combined_model.ltcg_qd_income_increment == 2000.0
