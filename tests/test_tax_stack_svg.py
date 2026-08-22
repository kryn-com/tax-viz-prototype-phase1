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
        "Scenario",
        "Income summary",
        "Federal tax summary",
        "Deduction relief zone",
        "Ordinary-income marginal layers",
        "LTCG/QD rate layers",
        "Social Security explanation",
        "NIIT notice / overlay",
        "Federal totals",
    ]
    assert [svg.index(label) for label in labels] == sorted(svg.index(label) for label in labels)


def test_render_tax_stack_svg_keeps_stack_sections_below_income_summary():
    svg = render_federal_tax_stack_svg(create_model())

    summary_note_y = 294
    ordinary_section_y = int(
        re.search(
            r'<text class="section-title" x="48" y="(\d+)">Ordinary-income marginal layers',
            svg,
        ).group(1)
    )
    preferential_section_y = int(
        re.search(
            r'<text class="section-title" x="48" y="(\d+)">LTCG/QD rate layers',
            svg,
        ).group(1)
    )

    assert ordinary_section_y > summary_note_y
    assert preferential_section_y > summary_note_y


def test_render_tax_stack_svg_separates_top_left_summary_blocks():
    svg = render_federal_tax_stack_svg(create_model())

    assert 'id="top-left-tax-summary"' in svg
    assert 'x="48" y="132">Income summary' in svg
    assert 'x="48" y="152">Source' in svg
    assert 'x="300" y="152">Amount' in svg
    assert 'x="48" y="336">Federal tax summary' in svg
    assert 'x="48" y="300">Taxable Social Security is included in ordinary income; tax-free is not.' in svg
    assert "Taxable Social Security is included in ordinary income above;" not in svg
    assert "tax-free Social Security is included only in displayed total income." not in svg


def test_render_tax_stack_svg_preserves_layer_order_and_formats_values():
    svg = render_federal_tax_stack_svg(create_model())

    assert svg.index("10% tax bracket") < svg.index("12% tax bracket")
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
    assert "$20,000" in svg
    assert "$20,000.00" not in svg
    assert "Marginal rate" in svg
    assert "Effective rate" in svg
    assert "of total displayed income" in svg


def test_render_tax_stack_svg_omits_non_applicable_preferential_rates():
    svg = render_federal_tax_stack_svg(create_model())

    assert "15% LTCG/QD tax bracket" in svg
    assert "0% LTCG/QD tax bracket" not in svg
    assert "20% LTCG/QD tax bracket" not in svg
    assert "$20,000" in svg
    assert "15% | $20,000" not in svg
    assert "Tax $3,000" in svg


def test_render_tax_stack_svg_includes_social_security_and_niit_content():
    svg = render_federal_tax_stack_svg(create_model())

    assert "Taxable Social Security" in svg
    assert "Tax-free Social Security" in svg
    assert "Provisional income" in svg
    assert "NIIT does not apply in this scenario." in svg
    assert "Separate overlay; not an income-stack layer." in svg


def test_render_tax_stack_svg_shows_niit_details_when_niit_applies():
    model = build_federal_tax_stack_view_model(
        orchestrate_federal_tax(
            create_scenario(ordinary_income=1_000_000.0, ltcg_qd_income=500_000.0)
        )
    )
    svg = render_federal_tax_stack_svg(model)

    assert "Net investment income" in svg
    assert "MAGI over threshold" in svg
    assert "NIIT rate" in svg
    assert "NIIT tax" in svg
    assert "Separate overlay; not an income-stack layer." in svg


def test_render_tax_stack_svg_represents_zero_values_and_empty_layers():
    zero_model = create_model(
        deduction_shielding_amount=0.0,
        ordinary_marginal_layers=(),
        preferential_rate_layers=(),
    )
    svg = render_federal_tax_stack_svg(zero_model)

    assert "Deduction relief" in svg
    assert "0% shielding" not in svg
    assert "Conceptual zone; deduction is not allocated to a specific layer" in svg
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