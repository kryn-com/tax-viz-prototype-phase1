from models.sliver_display import FederalSliverDisplayModel


def _format_currency(value: float) -> str:
    return f"${value:,.2f}"


def render_federal_sliver_summary(model: FederalSliverDisplayModel) -> str:
    lines = [
        f"Result type: {model.result_kind}",
        f"Baseline federal tax: {_format_currency(model.baseline_total_federal_tax)}",
        f"Altered federal tax: {_format_currency(model.altered_total_federal_tax)}",
        f"Federal tax delta: {_format_currency(model.federal_tax_delta)}",
    ]

    if model.ordinary_income_increment:
        lines.append(
            f"Ordinary income increment: {_format_currency(model.ordinary_income_increment)}"
        )
    if model.ltcg_qd_income_increment:
        lines.append(
            f"LTCG/QD income increment: {_format_currency(model.ltcg_qd_income_increment)}"
        )

    return "\n".join(lines)
