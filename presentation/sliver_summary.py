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

    if model.baseline_breakdown is not None and model.altered_breakdown is not None:
        lines.extend(
            [
                "Federal tax components:",
                f"- baseline ordinary tax: {_format_currency(model.baseline_breakdown.ordinary_tax)}",
                f"- altered ordinary tax: {_format_currency(model.altered_breakdown.ordinary_tax)}",
                f"- ordinary tax delta: {_format_currency(model.altered_breakdown.ordinary_tax - model.baseline_breakdown.ordinary_tax)}",
                f"- baseline LTCG/QD tax: {_format_currency(model.baseline_breakdown.ltcg_qd_tax)}",
                f"- altered LTCG/QD tax: {_format_currency(model.altered_breakdown.ltcg_qd_tax)}",
                f"- LTCG/QD tax delta: {_format_currency(model.altered_breakdown.ltcg_qd_tax - model.baseline_breakdown.ltcg_qd_tax)}",
                f"- baseline NIIT tax: {_format_currency(model.baseline_breakdown.niit_tax)}",
                f"- altered NIIT tax: {_format_currency(model.altered_breakdown.niit_tax)}",
                f"- NIIT tax delta: {_format_currency(model.altered_breakdown.niit_tax - model.baseline_breakdown.niit_tax)}",
            ]
        )

    return "\n".join(lines)
