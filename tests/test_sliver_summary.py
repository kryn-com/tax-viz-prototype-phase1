from models.sliver_display import (
    FederalSliverDisplayModel,
    FederalSliverTaxBreakdown,
)
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
    assert "Federal tax components:" in summary
    assert "baseline ordinary tax:" in summary
    assert "altered NIIT tax:" in summary


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
        baseline_breakdown=FederalSliverTaxBreakdown(
            ordinary_tax=0.0,
            ltcg_qd_tax=0.0,
            niit_tax=0.0,
            total_federal_tax=0.0,
        ),
        altered_breakdown=FederalSliverTaxBreakdown(
            ordinary_tax=0.0,
            ltcg_qd_tax=0.0,
            niit_tax=0.0,
            total_federal_tax=0.0,
        ),
    )

    summary = render_federal_sliver_summary(model)

    assert "Baseline federal tax: $0.00" in summary
    assert "Altered federal tax: $0.00" in summary
    assert "Federal tax delta: $0.00" in summary
    assert "Result type: combined_income" in summary
    assert "baseline ordinary tax: $0.00" in summary
    assert "altered LTCG/QD tax: $0.00" in summary
    assert "NIIT tax delta: $0.00" in summary


def test_sliver_display_builders_map_component_breakdowns_and_deltas():
    result = analyze_combined_income_sliver(
        create_sliver_scenario(),
        ordinary_income_increment=1000.0,
        ltcg_qd_income_increment=2000.0,
    )
    model = build_federal_combined_sliver_display_model(result)

    assert model.baseline_breakdown is not None
    assert model.altered_breakdown is not None
    assert model.baseline_breakdown.ordinary_tax == result.baseline_result.ordinary_tax
    assert model.baseline_breakdown.ltcg_qd_tax == result.baseline_result.ltcg_qd_tax
    assert model.baseline_breakdown.niit_tax == result.baseline_result.niit_tax
    assert model.baseline_breakdown.total_federal_tax == result.baseline_result.total_federal_tax
    assert model.altered_breakdown.ordinary_tax == result.altered_result.ordinary_tax
    assert model.altered_breakdown.ltcg_qd_tax == result.altered_result.ltcg_qd_tax
    assert model.altered_breakdown.niit_tax == result.altered_result.niit_tax
    assert model.altered_breakdown.total_federal_tax == result.altered_result.total_federal_tax
    assert model.altered_breakdown.ordinary_tax - model.baseline_breakdown.ordinary_tax == (
        result.altered_result.ordinary_tax - result.baseline_result.ordinary_tax
    )


def test_ordinary_sliver_display_builder_maps_all_components():
    result = analyze_ordinary_income_sliver(create_sliver_scenario(), increment=1000.0)
    model = build_federal_sliver_display_model(result)

    assert model.baseline_breakdown == FederalSliverTaxBreakdown(
        ordinary_tax=result.baseline_result.ordinary_tax,
        ltcg_qd_tax=result.baseline_result.ltcg_qd_tax,
        niit_tax=result.baseline_result.niit_tax,
        total_federal_tax=result.baseline_result.total_federal_tax,
    )
    assert model.altered_breakdown == FederalSliverTaxBreakdown(
        ordinary_tax=result.altered_result.ordinary_tax,
        ltcg_qd_tax=result.altered_result.ltcg_qd_tax,
        niit_tax=result.altered_result.niit_tax,
        total_federal_tax=result.altered_result.total_federal_tax,
    )


def test_ltcg_qd_sliver_display_builder_maps_all_components():
    result = analyze_ltcg_qd_sliver(create_sliver_scenario(), increment=1000.0)
    model = build_federal_ltcg_qd_sliver_display_model(result)

    assert model.baseline_breakdown == FederalSliverTaxBreakdown(
        ordinary_tax=result.baseline_result.ordinary_tax,
        ltcg_qd_tax=result.baseline_result.ltcg_qd_tax,
        niit_tax=result.baseline_result.niit_tax,
        total_federal_tax=result.baseline_result.total_federal_tax,
    )
    assert model.altered_breakdown == FederalSliverTaxBreakdown(
        ordinary_tax=result.altered_result.ordinary_tax,
        ltcg_qd_tax=result.altered_result.ltcg_qd_tax,
        niit_tax=result.altered_result.niit_tax,
        total_federal_tax=result.altered_result.total_federal_tax,
    )


def test_render_federal_sliver_summary_includes_component_deltas():
    result = analyze_combined_income_sliver(
        create_sliver_scenario(),
        ordinary_income_increment=1000.0,
        ltcg_qd_income_increment=2000.0,
    )
    summary = render_federal_sliver_summary(
        build_federal_combined_sliver_display_model(result)
    )

    assert "ordinary tax delta: $" in summary
    assert "LTCG/QD tax delta: $" in summary
    assert "NIIT tax delta: $" in summary


def test_render_federal_sliver_summary_formats_negative_component_deltas():
    model = FederalSliverDisplayModel(
        tax_year=2026,
        filing_status=create_sliver_scenario().filing_status,
        result_kind="combined_income",
        baseline_total_federal_tax=100.0,
        altered_total_federal_tax=70.0,
        federal_tax_delta=-30.0,
        baseline_breakdown=FederalSliverTaxBreakdown(
            ordinary_tax=100.0,
            ltcg_qd_tax=80.0,
            niit_tax=60.0,
            total_federal_tax=240.0,
        ),
        altered_breakdown=FederalSliverTaxBreakdown(
            ordinary_tax=90.0,
            ltcg_qd_tax=50.0,
            niit_tax=20.0,
            total_federal_tax=160.0,
        ),
    )

    summary = render_federal_sliver_summary(model)

    assert "ordinary tax delta: $-10.00" in summary
    assert "LTCG/QD tax delta: $-30.00" in summary
    assert "NIIT tax delta: $-40.00" in summary


def test_legacy_positional_sliver_display_model_renders_without_components():
    model = FederalSliverDisplayModel(
        2026,
        create_sliver_scenario().filing_status,
        "ordinary_income",
        100.0,
        120.0,
        20.0,
        1000.0,
        0.0,
    )

    summary = render_federal_sliver_summary(model)

    assert "Result type: ordinary_income" in summary
    assert "Federal tax delta: $20.00" in summary
    assert "Federal tax components:" not in summary


def test_legacy_keyword_sliver_display_model_renders_without_components():
    model = FederalSliverDisplayModel(
        tax_year=2026,
        filing_status=create_sliver_scenario().filing_status,
        result_kind="ltcg_qd_income",
        baseline_total_federal_tax=100.0,
        altered_total_federal_tax=130.0,
        federal_tax_delta=30.0,
        ltcg_qd_income_increment=1000.0,
    )

    summary = render_federal_sliver_summary(model)

    assert "Result type: ltcg_qd_income" in summary
    assert "Federal tax delta: $30.00" in summary
    assert "Federal tax components:" not in summary


def test_baseline_only_sliver_breakdown_is_omitted_from_summary():
    model = FederalSliverDisplayModel(
        tax_year=2026,
        filing_status=create_sliver_scenario().filing_status,
        result_kind="ordinary_income",
        baseline_total_federal_tax=100.0,
        altered_total_federal_tax=120.0,
        federal_tax_delta=20.0,
        baseline_breakdown=FederalSliverTaxBreakdown(100.0, 0.0, 0.0, 100.0),
    )

    assert "Federal tax components:" not in render_federal_sliver_summary(model)


def test_altered_only_sliver_breakdown_is_omitted_from_summary():
    model = FederalSliverDisplayModel(
        tax_year=2026,
        filing_status=create_sliver_scenario().filing_status,
        result_kind="ordinary_income",
        baseline_total_federal_tax=100.0,
        altered_total_federal_tax=120.0,
        federal_tax_delta=20.0,
        altered_breakdown=FederalSliverTaxBreakdown(120.0, 0.0, 0.0, 120.0),
    )

    assert "Federal tax components:" not in render_federal_sliver_summary(model)


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
