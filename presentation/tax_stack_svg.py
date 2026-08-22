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


def _format_currency(value: float) -> str:
    return f"${value:,.2f}"


def _format_rate(value: float) -> str:
    percentage = value * 100
    if percentage.is_integer():
        return f"{percentage:.0f}%"
    return f"{percentage:.2f}%"


def _text(class_name: str, x: int, y: int, value: str) -> str:
    return f'    <text class="{class_name}" x="{x}" y="{y}">{escape(value)}</text>'


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
            f"{_format_rate(rate)} | {_format_currency(amount)}",
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
        f'    <text class="panel-value" x="{_PANEL_X + 174}" y="{y}">'
        f"{escape(value)}</text>"
    )


def _render_scenario_summary(view_model: FederalTaxStackViewModel) -> list[str]:
    return [
        '  <g id="scenario-summary">',
        _text("section-title", _LEFT, 88, "Scenario inputs (audit target)"),
        _text(
            "context",
            _LEFT,
            110,
            f"Tax year: {view_model.tax_year} | Filing status: {view_model.filing_status}",
        ),
        _text(
            "context",
            _LEFT,
            130,
            f"Ordinary income: {_format_currency(view_model.ordinary_income)} | "
            f"Preferential income: {_format_currency(view_model.preferential_income)}",
        ),
        _text(
            "context",
            _LEFT,
            150,
            f"Social Security: {_format_currency(view_model.social_security.total_social_security)} | "
            f"Shielding amount: {_format_currency(view_model.deduction_shielding_amount)}",
        ),
        "  </g>",
    ]


def _render_social_security_panel(view_model: FederalTaxStackViewModel) -> list[str]:
    social_security = view_model.social_security
    lines = [
        f'  <g id="social-security">',
        f'    <rect class="panel social-security-panel" x="{_PANEL_X}" y="145" '
        f'width="{_PANEL_WIDTH}" height="190" />',
        _text("panel-title", _PANEL_X + 16, 174, "Social Security explanation"),
        _render_panel_line("Total Social Security", _format_currency(social_security.total_social_security), 202),
        _render_panel_line("Taxable Social Security", _format_currency(social_security.taxable_social_security), 226),
        _render_panel_line("Tax-free Social Security", _format_currency(social_security.tax_free_social_security), 250),
        _render_panel_line("Provisional income", _format_currency(social_security.provisional_income), 274),
        _text("panel-note", _PANEL_X + 16, 310, "Explanation only; included in ordinary-income result."),
        "  </g>",
    ]
    return lines


def _render_niit_panel(view_model: FederalTaxStackViewModel) -> list[str]:
    niit = view_model.niit
    lines = [
        f'  <g id="niit">',
        f'    <rect class="panel niit-panel" x="{_PANEL_X}" y="355" '
        f'width="{_PANEL_WIDTH}" height="250" />',
        _text("panel-title", _PANEL_X + 16, 384, "NIIT notice / overlay"),
        _render_panel_line("Net investment income", _format_currency(niit.net_investment_income), 412),
        _render_panel_line("MAGI", _format_currency(niit.magi), 436),
        _render_panel_line("Threshold", _format_currency(niit.threshold_applied), 460),
        _render_panel_line("MAGI over threshold", _format_currency(niit.magi_over_threshold), 484),
        _render_panel_line("Tax base", _format_currency(niit.tax_base), 508),
        _render_panel_line("NIIT rate", _format_rate(niit.niit_rate), 532),
        _render_panel_line("NIIT tax", _format_currency(niit.niit_tax), 556),
        _text("panel-note", _PANEL_X + 16, 584, "Overlay; not an income-stack layer."),
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
        _text("total", _LEFT, 178, f"Total federal tax: {_format_currency(view_model.total_federal_tax)}"),
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
    lines.append(_text("section-title", _STACK_X, 665, "Deduction / 0% shielding (conceptual zone)"))
    lines.append(
        f'    <rect class="shielding" x="{_STACK_X}" y="680" width="{_STACK_WIDTH}" height="44" />'
    )
    lines.append(_text("layer-label", _STACK_X + 12, 698, "0% shielding"))
    lines.append(
        _text(
            "layer-value",
            _STACK_X + 12,
            716,
            "Conceptual shielding zone; allocation not specified",
        )
    )
    lines.append("  </g>")

    ordinary_top = 665 - len(view_model.ordinary_marginal_layers) * _ROW_HEIGHT
    if view_model.ordinary_marginal_layers:
        lines.append('  <g id="ordinary-layers">')
        lines.append(_text("section-title", _STACK_X, ordinary_top - 12, "Ordinary-income marginal layers"))
        for index, layer in enumerate(view_model.ordinary_marginal_layers):
            lines.extend(
                _render_layer(
                    "ordinary",
                    f"Ordinary layer {index + 1}",
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
                    f"LTCG/QD layer {index + 1}",
                    layer.rate,
                    layer.taxed_amount,
                    None,
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