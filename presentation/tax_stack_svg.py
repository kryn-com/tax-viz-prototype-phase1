from html import escape

from models.tax_stack_display import FederalTaxStackViewModel


_WIDTH = 1000
_HEIGHT = 820
_LEFT = 48
_STACK_X = 48
_STACK_WIDTH = 540
_PANEL_X = 630
_PANEL_WIDTH = 320
_ROW_HEIGHT = 42
_STACK_BOTTOM = 740


def _format_currency(value: float) -> str:
    return f"${value:,.0f}"


def _format_rate(value: float) -> str:
    percentage = value * 100
    if percentage.is_integer():
        return f"{percentage:.0f}%"
    return f"{percentage:.2f}%"


def _text(class_name: str, x: int, y: int, value: str, anchor: str | None = None) -> str:
    anchor_attr = f' text-anchor="{anchor}"' if anchor else ""
    return f'    <text class="{class_name}" x="{x}" y="{y}"{anchor_attr}>{escape(value)}</text>'


def _render_layer(
    group_id: str,
    label: str,
    rate: float,
    amount: float,
    tax: float | None,
    y: int,
    color_class: str,
) -> list[str]:
    lines = [f'  <g id="{group_id}-layer">']
    lines.append(
        f'    <rect class="{color_class}" x="{_STACK_X}" y="{y}" '
        f'width="{_STACK_WIDTH}" height="{_ROW_HEIGHT - 4}" />'
    )
    lines.append(_text("layer-label", _STACK_X + 12, y + 17, label))
    lines.append(
        _text(
            "layer-value",
            _STACK_X + 12,
            y + 34,
            _format_currency(amount),
        )
    )
    if tax is not None:
        lines.append(
            _text(
                "layer-tax",
                _STACK_X + _STACK_WIDTH - 128,
                y + 25,
                f"Tax {_format_currency(tax)}",
            )
        )
    lines.append("  </g>")
    return lines


def _render_empty(group_id: str, title: str, y: int) -> list[str]:
    return [
        f'  <g id="{group_id}">',
        _text("section-title", _STACK_X, y, title),
        _text("empty", _STACK_X, y + 28, "No layers"),
        "  </g>",
    ]


def _render_panel_line(label: str, value: str, y: int) -> str:
    return (
        f'    <text class="panel-label" x="{_PANEL_X + 16}" y="{y}">'
        f"{escape(label)}:</text>"
        f'    <text class="panel-value" x="{_PANEL_X + _PANEL_WIDTH - 18}" y="{y}" text-anchor="end">'
        f"{escape(value)}</text>"
    )


def _render_scenario_summary(view_model: FederalTaxStackViewModel) -> list[str]:
    source_ordinary_income = (
        view_model.ordinary_income - view_model.social_security.taxable_social_security
    )
    filing_status = {
        "single": "Single",
        "married_filing_jointly": "Married filing jointly",
        "married_filing_separately": "Married filing separately",
        "head_of_household": "Head of household",
    }.get(getattr(view_model.filing_status, "value", view_model.filing_status), str(view_model.filing_status))
    deduction_type = {
        "standard": "Standard",
        "itemized": "Itemized",
        "explicit": "Explicit",
    }.get(getattr(view_model.deduction_mode, "value", view_model.deduction_mode), str(view_model.deduction_mode))
    return [
        '  <g id="scenario-summary">',
        _text("section-title", _LEFT, 88, "Scenario"),
        _text(
            "context",
            _LEFT,
            110,
            f"Tax year: {view_model.tax_year} | Filing status: {filing_status}",
        ),
        _text("section-title", _LEFT, 132, "Income summary"),
        _text("context", 250, 152, "Taxable"),
        _text("context", 425, 152, "Non-taxable"),
        _text("context", _LEFT, 170, "Ordinary income"),
        _text("context", 300, 170, _format_currency(source_ordinary_income), "end"),
        _text("context", _LEFT, 188, "LTCG / qualified dividends"),
        _text("context", 300, 188, _format_currency(view_model.preferential_income), "end"),
        _text("context", _LEFT, 206, "Taxable Social Security"),
        _text("context", 300, 206, _format_currency(view_model.social_security.taxable_social_security), "end"),
        _text("context", _LEFT, 224, "Tax-free Social Security"),
        _text("context", 470, 224, _format_currency(view_model.social_security.tax_free_social_security), "end"),
        _text("context", _LEFT, 242, "Nontaxable income"),
        _text("context", 470, 242, _format_currency(view_model.nontaxable_income), "end"),
        _text("context", _LEFT, 260, "Deduction type"),
        _text("context", 300, 260, deduction_type),
        _text("context", _LEFT, 278, "Deduction amount"),
        _text("context", 300, 278, _format_currency(view_model.deduction_shielding_amount), "end"),
        "  </g>",
    ]


def _render_social_security_panel(view_model: FederalTaxStackViewModel) -> list[str]:
    social_security = view_model.social_security
    lines = [
        f'  <g id="social-security">',
        f'    <rect class="panel social-security-panel" x="{_PANEL_X}" y="145" '
        f'width="{_PANEL_WIDTH}" height="220" />',
        _text("panel-title", _PANEL_X + 16, 174, "Taxability"),
        _render_panel_line("Total Social Security", _format_currency(social_security.total_social_security), 204),
        _render_panel_line("Taxable Social Security", _format_currency(social_security.taxable_social_security), 232),
        _render_panel_line("Tax-free Social Security", _format_currency(social_security.tax_free_social_security), 260),
        _render_panel_line("Taxable percentage", _format_rate(
            social_security.taxable_social_security / social_security.total_social_security
            if social_security.total_social_security else 0.0
        ), 288),
        _render_panel_line("Provisional income", _format_currency(social_security.provisional_income), 316),
        "  </g>",
    ]
    return lines


def _render_niit_panel(view_model: FederalTaxStackViewModel) -> list[str]:
    niit = view_model.niit
    if niit.niit_tax == 0.0:
        return [
            '  <g id="niit">',
            f'    <rect class="panel niit-panel" x="{_PANEL_X}" y="375" width="{_PANEL_WIDTH}" height="88" />',
            _text("panel-title", _PANEL_X + 16, 404, "NIIT notice / overlay"),
            _text("panel-note", _PANEL_X + 16, 432, "NIIT: not applicable."),
            "  </g>",
        ]
    lines = [
        f'  <g id="niit">',
        f'    <rect class="panel niit-panel" x="{_PANEL_X}" y="375" '
        f'width="{_PANEL_WIDTH}" height="250" />',
        _text("panel-title", _PANEL_X + 16, 404, "NIIT notice / overlay"),
        _render_panel_line("Net investment income", _format_currency(niit.net_investment_income), 432),
        _render_panel_line("MAGI", _format_currency(niit.magi), 460),
        _render_panel_line("Threshold", _format_currency(niit.threshold_applied), 488),
        _render_panel_line("MAGI over threshold", _format_currency(niit.magi_over_threshold), 516),
        _render_panel_line("Tax base", _format_currency(niit.tax_base), 544),
        _render_panel_line("NIIT rate", _format_rate(niit.niit_rate), 572),
        _render_panel_line("NIIT tax", _format_currency(niit.niit_tax), 600),
        _text("panel-note", _PANEL_X + 16, 624, "Separate overlay; not an income-stack layer."),
        "  </g>",
    ]
    return lines


def render_federal_tax_stack_svg(
    view_model: FederalTaxStackViewModel,
) -> str:
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{_WIDTH}" height="{_HEIGHT}" '
        f'viewBox="0 0 {_WIDTH} {_HEIGHT}">',
        "  <title>Federal Tax Stack</title>",
        _text("title", _LEFT, 34, f"Federal Tax Stack ({view_model.tax_year})"),
        _text("context", _LEFT, 60, "Federal-only scope"),
        *_render_scenario_summary(view_model),
        '  <g id="top-left-tax-summary">',
        _text("section-title", _LEFT, 336, "Federal tax summary"),
        _text("total", _LEFT, 358, f"Total tax: {_format_currency(view_model.total_federal_tax)}"),
        _text("context", _LEFT, 378, f"Marginal rate: {_format_rate(view_model.ordinary_marginal_layers[-1].rate if view_model.ordinary_marginal_layers else 0.0)}"),
        _text("context", _LEFT, 396, f"Effective rate: {_format_rate(view_model.total_federal_tax / (view_model.ordinary_income + view_model.preferential_income + view_model.social_security.total_social_security + view_model.nontaxable_income) if (view_model.ordinary_income + view_model.preferential_income + view_model.social_security.total_social_security + view_model.nontaxable_income) else 0.0)} of total displayed income"),
        "  </g>",
        "  <style>",
        "    .title { font: bold 24px sans-serif; fill: #202124; }",
        "    .context, .total, .section-title, .layer-label, .layer-value, .layer-tax, .empty, .panel-title, .panel-label, .panel-value, .panel-note { font: 14px sans-serif; fill: #202124; }",
        "    .total { font-weight: bold; }",
        "    .section-title, .panel-title { font-weight: bold; }",
        "    .shielding { fill: #d9ead3; stroke: #6aa84f; stroke-width: 1; }",
        "    .ordinary { fill: #cfe2f3; stroke: #3d85c6; stroke-width: 1; }",
        "    .preferential { fill: #fce5cd; stroke: #e69138; stroke-width: 1; }",
        "    .panel { stroke-width: 1; opacity: 0.82; }",
        "    .social-security-panel { fill: #f3f3f3; stroke: #999999; }",
        "    .niit-panel { fill: #fff2cc; stroke: #bf9000; }",
        "    .layer-value, .layer-tax, .panel-note, .empty { fill: #5f6368; }",
        "    .panel-label { font-weight: bold; }",
        "  </style>",
    ]

    lines.append('  <g id="deduction-shielding">')
    lines.append(_text("section-title", _STACK_X, _STACK_BOTTOM, "Deduction zone (0% tax rate)"))
    lines.append(
        f'    <rect class="shielding" x="{_STACK_X}" y="{_STACK_BOTTOM + 15}" width="{_STACK_WIDTH}" height="44" />'
    )
    lines.append("  </g>")

    ordinary_top = _STACK_BOTTOM - len(view_model.ordinary_marginal_layers) * _ROW_HEIGHT
    if view_model.ordinary_marginal_layers:
        lines.append('  <g id="ordinary-layers">')
        lines.append(_text("section-title", _STACK_X, ordinary_top - 12, "Ordinary-income marginal layers"))
        for index, layer in enumerate(view_model.ordinary_marginal_layers):
            lines.extend(
                _render_layer(
                    "ordinary",
                    f"{_format_rate(layer.rate)} tax bracket",
                    layer.rate,
                    layer.taxed_amount,
                    layer.tax_generated,
                    ordinary_top + (len(view_model.ordinary_marginal_layers) - index - 1) * _ROW_HEIGHT,
                    "ordinary",
                )
            )
        lines.append("  </g>")
    else:
        lines.extend(_render_empty("ordinary-layers", "Ordinary-income marginal layers", ordinary_top - 12))

    preferential_top = ordinary_top - (len(view_model.preferential_rate_layers) + 1) * _ROW_HEIGHT
    if view_model.preferential_rate_layers:
        lines.append('  <g id="preferential-layers">')
        lines.append(_text("section-title", _STACK_X, preferential_top - 12, "LTCG/QD rate layers (above ordinary income)"))
        for index, layer in enumerate(view_model.preferential_rate_layers):
            lines.extend(
                _render_layer(
                    "preferential",
                    f"{_format_rate(layer.rate)} LTCG/QD tax bracket",
                    layer.rate,
                    layer.taxed_amount,
                    layer.rate * layer.taxed_amount,
                    preferential_top + (len(view_model.preferential_rate_layers) - index - 1) * _ROW_HEIGHT,
                    "preferential",
                )
            )
        lines.append("  </g>")
    else:
        lines.extend(_render_empty("preferential-layers", "LTCG/QD rate layers (above ordinary income)", preferential_top - 12))

    lines.extend(_render_social_security_panel(view_model))
    lines.extend(_render_niit_panel(view_model))
    lines.extend(
        [
            '  <g id="federal-totals">',
            _text("section-title", _PANEL_X, 650, "Federal totals"),
            _render_panel_line("Ordinary tax", _format_currency(view_model.ordinary_tax), 678),
            _render_panel_line("LTCG/QD tax", _format_currency(view_model.ltcg_qd_tax), 702),
            _render_panel_line("Total federal tax", _format_currency(view_model.total_federal_tax), 726),
            "  </g>",
            "</svg>",
        ]
    )
    return "\n".join(lines)