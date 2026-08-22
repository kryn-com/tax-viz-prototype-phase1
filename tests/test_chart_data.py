from dataclasses import FrozenInstanceError

import pytest

from models.chart_display import FederalChartSegment, FederalChartViewModel
from models.federal_display import (
    FederalDisplayBracketSlice,
    FederalDisplayModel,
    FederalDisplayRateSlice,
)
from presentation.chart_data import build_federal_chart_view_model
from tests.test_federal_display import create_scenario
from engines.federal_orchestrator import orchestrate_federal_tax
from presentation.federal_display import build_federal_display_model


def test_build_federal_chart_view_model_maps_components_and_metadata():
    result = orchestrate_federal_tax(create_scenario())
    display = build_federal_display_model(result)

    chart = build_federal_chart_view_model(display)

    assert chart.tax_year == display.tax_year
    assert chart.filing_status is display.filing_status
    assert chart.total_federal_tax == display.total_federal_tax
    assert [(segment.label, segment.value) for segment in chart.tax_component_segments] == [
        ("Ordinary tax", display.ordinary_tax),
        ("LTCG/QD tax", display.ltcg_qd_tax),
        ("NIIT tax", display.niit_tax),
    ]


def test_build_federal_chart_view_model_preserves_fixed_segment_order():
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
        ordinary_tax=10.0,
        ltcg_qd_tax=20.0,
        niit_tax=30.0,
        total_federal_tax=60.0,
        ordinary_bracket_slices=(
            FederalDisplayBracketSlice(0.12, 100.0, 200.0, 50.0, 6.0),
            FederalDisplayBracketSlice(0.22, 200.0, None, 75.0, 16.5),
        ),
        preferential_rate_slices=(
            FederalDisplayRateSlice(0.0, 100.0),
            FederalDisplayRateSlice(0.15, 200.0),
            FederalDisplayRateSlice(0.20, 300.0),
        ),
    )

    chart = build_federal_chart_view_model(model)

    assert [segment.label for segment in chart.tax_component_segments] == [
        "Ordinary tax",
        "LTCG/QD tax",
        "NIIT tax",
    ]
    assert [(segment.label, segment.value, segment.rate) for segment in chart.ordinary_bracket_segments] == [
        ("Ordinary bracket 1", 6.0, 0.12),
        ("Ordinary bracket 2", 16.5, 0.22),
    ]
    assert [(segment.label, segment.value, segment.rate) for segment in chart.preferential_rate_segments] == [
        ("Preferential rate 0%", 100.0, 0.0),
        ("Preferential rate 15%", 200.0, 0.15),
        ("Preferential rate 20%", 300.0, 0.20),
    ]


def test_build_federal_chart_view_model_preserves_zero_segments():
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
        ordinary_bracket_slices=(FederalDisplayBracketSlice(0.10, 0.0, 100.0, 0.0, 0.0),),
        preferential_rate_slices=(FederalDisplayRateSlice(0.0, 0.0),),
    )

    chart = build_federal_chart_view_model(model)

    assert [segment.value for segment in chart.tax_component_segments] == [0.0, 0.0, 0.0]
    assert chart.ordinary_bracket_segments[0].value == 0.0
    assert chart.preferential_rate_segments[0].value == 0.0


def test_build_federal_chart_view_model_preserves_empty_source_tuples():
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

    chart = build_federal_chart_view_model(model)

    assert chart.ordinary_bracket_segments == ()
    assert chart.preferential_rate_segments == ()


def test_chart_view_model_is_immutable():
    segment = FederalChartSegment(label="Tax", value=1.0)
    chart = FederalChartViewModel(2026, create_scenario().filing_status, 1.0, (segment,), (), ())

    with pytest.raises(FrozenInstanceError):
        segment.value = 2.0
    with pytest.raises(FrozenInstanceError):
        chart.total_federal_tax = 2.0


def test_build_federal_chart_view_model_is_deterministic():
    display = build_federal_display_model(orchestrate_federal_tax(create_scenario()))

    assert build_federal_chart_view_model(display) == build_federal_chart_view_model(display)
