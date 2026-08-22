import re
from xml.etree import ElementTree

from engines.federal_orchestrator import orchestrate_federal_tax
from models.inputs import DeductionMode, FilingStatus, TaxScenarioInput
from models.tax_stack_display import (
    FederalTaxStackNIIT,
    FederalTaxStackSocialSecurity,
    FederalTaxStackViewModel,
)
from presentation.tax_stack_data import build_federal_tax_stack_view_model
from presentation.tax_stack_svg import render_federal_tax_stack_svg


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


def create_model(**overrides):
    model = build_federal_tax_stack_view_model(orchestrate_federal_tax(create_scenario()))
    values = model.__dict__
    values.update(overrides)
    return FederalTaxStackViewModel(**values)


def test_render_tax_stack_svg_is_standalone_and_structurally_valid():
    root = ElementTree.fromstring(render_federal_tax_stack_svg(create_model()))

    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert root.attrib == {"width": "1000", "height": "820", "viewBox": "0 0 1000 820"}
    assert root.find("{http://www.w3.org/2000/svg}title") is not None


def test_render_tax_stack_svg_includes_headers_and_sections_in_order():
    svg = render_federal_tax_stack_svg(create_model())

    labels = [
        "Federal Tax Stack",
        "Federal-only scope",
        "Scenario inputs (audit target)",
        "Deduction / 0% shielding",
        "Ordinary-income marginal layers",
        "LTCG/QD rate layers",
        "Social Security explanation",
        "NIIT notice / overlay",
        "Federal totals",
    ]
    assert [svg.index(label) for label in labels] == sorted(svg.index(label) for label in labels)


def test_render_tax_stack_svg_preserves_layer_order_and_formats_values():
    svg = render_federal_tax_stack_svg(create_model())

    assert svg.index("Ordinary layer 1") < svg.index("Ordinary layer 2")
    ordinary_layer_positions = [
        int(position)
        for position in re.findall(
            r'<g id="ordinary-layer">\s*<rect class="ordinary" x="48" y="(\d+)"',
            svg,
        )
    ]
    assert ordinary_layer_positions == sorted(ordinary_layer_positions, reverse=True)
    assert "10%" in svg
    assert "0.00%" not in svg
    assert "$20,000.00" in svg


def test_render_tax_stack_svg_omits_non_applicable_preferential_rates():
    svg = render_federal_tax_stack_svg(create_model())

    assert "LTCG/QD layer 1" in svg
    assert "LTCG/QD layer 2" not in svg
    assert "LTCG/QD layer 3" not in svg
    assert "15% | $20,000.00" in svg


def test_render_tax_stack_svg_includes_social_security_and_niit_content():
    svg = render_federal_tax_stack_svg(create_model())

    assert "Taxable Social Security" in svg
    assert "Tax-free Social Security" in svg
    assert "Provisional income" in svg
    assert "Net investment income" in svg
    assert "MAGI over threshold" in svg
    assert "NIIT rate" in svg
    assert "Overlay; not an income-stack layer." in svg


def test_render_tax_stack_svg_represents_zero_values_and_empty_layers():
    zero_model = create_model(
        deduction_shielding_amount=0.0,
        ordinary_marginal_layers=(),
        preferential_rate_layers=(),
    )
    svg = render_federal_tax_stack_svg(zero_model)

    assert "0% shielding" in svg
    assert "Conceptual shielding zone; allocation not specified" in svg
    assert "$0.00 deduction applied" not in svg
    assert svg.count("No layers") == 2


def test_render_tax_stack_svg_escapes_dynamic_text_and_is_deterministic():
    model = create_model(filing_status="<single&filing>")
    first = render_federal_tax_stack_svg(model)

    assert "&lt;single&amp;filing&gt;" in first
    assert "<single&filing>" not in first
    assert first == render_federal_tax_stack_svg(model)


def test_render_tax_stack_svg_does_not_mutate_view_model():
    model = create_model()
    before = model

    render_federal_tax_stack_svg(model)

    assert model == before