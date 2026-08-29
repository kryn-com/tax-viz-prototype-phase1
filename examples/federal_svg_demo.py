from pathlib import Path

from engines.federal_orchestrator import orchestrate_federal_tax
from models.inputs import DeductionMode, FilingStatus, TaxScenarioInput
from presentation.chart_data import build_federal_chart_view_model
from presentation.federal_chart_svg import render_federal_chart_svg
from presentation.federal_display import build_federal_display_model


_OUTPUT_FILENAME = "federal_tax_chart.svg"


def create_representative_federal_scenario() -> TaxScenarioInput:
    return TaxScenarioInput(
        tax_year=2026,
        state_code="NC",
        filing_status=FilingStatus.SINGLE,
        taxpayer_age=45,
        ordinary_income=220000.0,
        ltcg_qd_income=50000.0,
        social_security_income=30000.0,
        nontaxable_income=0.0,
        deduction_mode=DeductionMode.STANDARD,
        deduction_amount=0.0,
    )


def render_representative_federal_svg() -> str:
    scenario = create_representative_federal_scenario()
    result = orchestrate_federal_tax(scenario)
    display_model = build_federal_display_model(result)
    chart_view_model = build_federal_chart_view_model(display_model)
    return render_federal_chart_svg(chart_view_model)


def main() -> None:
    svg = render_representative_federal_svg()
    Path(_OUTPUT_FILENAME).write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
