from xml.etree import ElementTree

from models.chart_display import FederalChartSegment, FederalChartViewModel
from presentation.federal_chart_svg import render_federal_chart_svg
from tests.test_federal_display import create_scenario


def create_chart(**overrides):
    values = {
        "tax_year": 2026,
        "filing_status": create_scenario().filing_status,
        "total_federal_tax": 600.0,
        "tax_component_segments": (
            FederalChartSegment("Ordinary tax", 300.0),
            FederalChartSegment("LTCG/QD tax", 200.0),
            FederalChartSegment("NIIT tax", 100.0),
        ),
        "ordinary_bracket_segments": (
            FederalChartSegment("Ordinary bracket 1", 100.0, 0.10),
            FederalChartSegment("Ordinary bracket 2", 200.0, 0.22),
        ),
        "preferential_rate_segments": (
            FederalChartSegment("Preferential rate 0%", 50.0, 0.0),
            FederalChartSegment("Preferential rate 15%", 150.0, 0.15),
        ),
    }
    values.update(overrides)
    return FederalChartViewModel(**values)


def test_render_federal_chart_svg_is_standalone_and_structurally_valid():
    svg = render_federal_chart_svg(create_chart())

    root = ElementTree.fromstring(svg)

    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert root.attrib["width"] == "800"
    assert root.attrib["height"] == "600"
    assert root.find("{http://www.w3.org/2000/svg}title") is not None


def test_render_federal_chart_svg_preserves_section_and_segment_order():
    svg = render_federal_chart_svg(create_chart())

    section_positions = [
        svg.index("Federal tax components"),
        svg.index("Ordinary tax by bracket"),
        svg.index("Preferential income by rate"),
    ]
    segment_positions = [
        svg.index("Ordinary tax"),
        svg.index("LTCG/QD tax"),
        svg.index("NIIT tax"),
        svg.index("Ordinary bracket 1"),
        svg.index("Ordinary bracket 2"),
        svg.index("Preferential rate 0%"),
        svg.index("Preferential rate 15%"),
    ]

    assert section_positions == sorted(section_positions)
    assert segment_positions == sorted(segment_positions)


def test_render_federal_chart_svg_is_deterministic():
    chart = create_chart()

    assert render_federal_chart_svg(chart) == render_federal_chart_svg(chart)


def test_render_federal_chart_svg_preserves_zero_valued_segments():
    chart = create_chart(
        tax_component_segments=(FederalChartSegment("Zero tax", 0.0),),
        ordinary_bracket_segments=(FederalChartSegment("Zero bracket", 0.0, 0.10),),
        preferential_rate_segments=(FederalChartSegment("Zero rate", 0.0, 0.0),),
    )

    svg = render_federal_chart_svg(chart)

    assert "Zero tax" in svg
    assert "Zero bracket" in svg
    assert "Zero rate" in svg
    assert svg.count("$0.00") == 3


def test_render_federal_chart_svg_handles_empty_collections():
    svg = render_federal_chart_svg(
        create_chart(
            tax_component_segments=(),
            ordinary_bracket_segments=(),
            preferential_rate_segments=(),
        )
    )

    assert svg.count("No segments") == 3


def test_render_federal_chart_svg_does_not_mutate_view_model():
    chart = create_chart()
    before = chart

    render_federal_chart_svg(chart)

    assert chart == before