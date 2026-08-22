from html import escape
from typing import Sequence

from models.chart_display import FederalChartSegment, FederalChartViewModel


_WIDTH = 800
_HEIGHT = 600
_LEFT = 40
_BAR_X = 270
_BAR_WIDTH = 360
_ROW_HEIGHT = 38
_SECTION_HEIGHT = 170


def _format_currency(value: float) -> str:
    return f"${value:,.2f}"


def _render_section(
    title: str,
    segments: Sequence[FederalChartSegment],
    top: int,
) -> list[str]:
    lines = [f'  <g id="{escape(title.lower().replace(" ", "-"))}">']
    lines.append(f'    <text class="section-title" x="{_LEFT}" y="{top}">{escape(title)}</text>')

    if not segments:
        lines.append(f'    <text class="empty" x="{_LEFT}" y="{top + 32}">No segments</text>')
    else:
        maximum = max((segment.value for segment in segments), default=0.0)
        maximum = max(maximum, 0.0)
        for index, segment in enumerate(segments):
            row_y = top + 24 + index * _ROW_HEIGHT
            width = 0.0 if maximum == 0.0 else max(segment.value, 0.0) / maximum * _BAR_WIDTH
            lines.append(
                f'    <text class="label" x="{_LEFT}" y="{row_y + 16}">{escape(segment.label)}</text>'
            )
            lines.append(
                f'    <rect class="bar" x="{_BAR_X}" y="{row_y}" width="{width:.2f}" height="20" />'
            )
            lines.append(
                f'    <text class="value" x="{_BAR_X + _BAR_WIDTH + 16}" y="{row_y + 16}">'
                f'{escape(_format_currency(segment.value))}</text>'
            )

    lines.append("  </g>")
    return lines


def render_federal_chart_svg(
    view_model: FederalChartViewModel,
) -> str:
    sections = (
        ("Federal tax components", view_model.tax_component_segments),
        ("Ordinary tax by bracket", view_model.ordinary_bracket_segments),
        ("Preferential income by rate", view_model.preferential_rate_segments),
    )
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{_WIDTH}" height="{_HEIGHT}" '
        f'viewBox="0 0 {_WIDTH} {_HEIGHT}">',
        "  <title>Federal tax chart</title>",
        f'  <text class="title" x="{_LEFT}" y="32">Federal Tax Overview ({view_model.tax_year})</text>',
        f'  <text class="total" x="{_LEFT}" y="58">Total federal tax: '
        f'{escape(_format_currency(view_model.total_federal_tax))}</text>',
        "  <style>",
        "    .title { font: bold 22px sans-serif; fill: #202124; }",
        "    .total, .section-title, .label, .value, .empty { font: 14px sans-serif; fill: #202124; }",
        "    .section-title { font-weight: bold; }",
        "    .bar { fill: #2f6f8f; }",
        "    .empty { font-style: italic; fill: #5f6368; }",
        "  </style>",
    ]
    for index, (title, segments) in enumerate(sections):
        lines.extend(_render_section(title, segments, 96 + index * _SECTION_HEIGHT))
    lines.append("</svg>")
    return "\n".join(lines)