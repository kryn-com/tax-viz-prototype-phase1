from models.federal_display import FederalDisplayModel


def _format_currency(value: float) -> str:
    return f"${value:,.2f}"


def _format_rate(value: float) -> str:
    return f"{value:.2%}"


def render_federal_summary(model: FederalDisplayModel) -> str:
    lines = [
        f"Taxable ordinary income: {_format_currency(model.taxable_ordinary_income)}",
        f"Ordinary tax: {_format_currency(model.ordinary_tax)}",
        f"Taxable Social Security: {_format_currency(model.taxable_social_security)}",
        f"LTCG/qualified dividend income: {_format_currency(model.preferential_income)}",
        f"Preferential tax: {_format_currency(model.ltcg_qd_tax)}",
        f"NIIT tax: {_format_currency(model.niit_tax)}",
        f"Total federal tax: {_format_currency(model.total_federal_tax)}",
        "Ordinary bracket slices:",
    ]

    if model.ordinary_bracket_slices:
        lines.extend(
            (
                f"- rate={_format_rate(slice_.rate)}, "
                f"lower={_format_currency(slice_.lower_bound)}, "
                f"upper={_format_currency(slice_.upper_bound) if slice_.upper_bound is not None else 'none'}, "
                f"taxed={_format_currency(slice_.taxed_amount)}, "
                f"tax={_format_currency(slice_.tax_generated)}"
            )
            for slice_ in model.ordinary_bracket_slices
        )
    else:
        lines.append("- none")

    lines.append("Preferential rate slices:")
    if model.preferential_rate_slices:
        lines.extend(
            f"- rate={_format_rate(slice_.rate)}, taxed={_format_currency(slice_.taxed_amount)}"
            for slice_ in model.preferential_rate_slices
        )
    else:
        lines.append("- none")

    return "\n".join(lines)
