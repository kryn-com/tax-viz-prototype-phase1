from xml.etree import ElementTree

from examples.federal_svg_demo import (
    create_representative_federal_scenario,
    main,
    render_representative_federal_svg,
)
from engines.federal_orchestrator import orchestrate_federal_tax
from presentation.chart_data import build_federal_chart_view_model
from presentation.federal_display import build_federal_display_model


def test_representative_scenario_is_fresh_and_deterministic():
    first = create_representative_federal_scenario()
    second = create_representative_federal_scenario()

    assert first == second
    assert first is not second


def test_representative_scenario_completes_existing_federal_pipeline():
    scenario = create_representative_federal_scenario()
    result = orchestrate_federal_tax(scenario)
    display_model = build_federal_display_model(result)
    chart_view_model = build_federal_chart_view_model(display_model)

    assert result.total_federal_tax > 0.0
    assert chart_view_model.total_federal_tax == result.total_federal_tax
    assert chart_view_model.tax_component_segments
    assert chart_view_model.ordinary_bracket_segments
    assert chart_view_model.preferential_rate_segments


def test_representative_svg_is_valid_and_contains_expected_labels():
    svg = render_representative_federal_svg()
    root = ElementTree.fromstring(svg)

    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert "Federal Tax Overview (2026)" in svg
    assert "Total federal tax:" in svg
    assert "Federal tax components" in svg
    assert "Ordinary tax by bracket" in svg
    assert "Preferential income by rate" in svg
    assert "Ordinary tax" in svg
    assert "LTCG/QD tax" in svg
    assert "NIIT tax" in svg


def test_representative_svg_is_deterministic():
    assert render_representative_federal_svg() == render_representative_federal_svg()


def test_repeated_rendering_does_not_mutate_scenario_assumptions(monkeypatch):
    scenario = create_representative_federal_scenario()
    before = scenario.model_dump()
    monkeypatch.setattr(
        "examples.federal_svg_demo.create_representative_federal_scenario",
        lambda: scenario,
    )

    render_representative_federal_svg()
    render_representative_federal_svg()

    assert scenario.model_dump() == before


def test_main_writes_exact_rendered_svg(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    expected_svg = render_representative_federal_svg()

    main()

    assert (tmp_path / "federal_tax_chart.svg").read_text(encoding="utf-8") == expected_svg
