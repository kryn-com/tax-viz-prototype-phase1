from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from engines.federal_orchestrator import orchestrate_federal_tax
from engines.state_tax import compute_nc_tax
from models.inputs import DeductionMode, FilingStatus, NCDeductionMode, TaxScenarioInput
from models.outputs import FederalTaxResult
from planning.ltcg_qd_sliver import compose_additional_ltcg_qd_income_sliver
from planning.ordinary_income_sliver import compose_additional_ordinary_income_sliver
from rules.irmaa_projected_2028 import build_projected_2028_overlay_result


@dataclass(frozen=True)
class SupportedValue:
    supported: bool
    value: float | None
    message: str | None = None


EXAMPLE_SCENARIOS: dict[str, dict[str, float | int | str | None]] = {
    "NC Single Baseline": {
        "tax_year": 2026,
        "state_code": "NC",
        "filing_status": "single",
        "taxpayer_age": 45,
        "spouse_age": None,
        "ordinary_income": 120000.0,
        "ltcg_qd_income": 20000.0,
        "social_security_income": 15000.0,
        "nontaxable_income": 0.0,
        "deduction_mode": "standard",
        "deduction_amount": 0.0,
        "nc_deduction_mode": "standard",
        "nc_itemized_deduction_amount": None,
        "ordinary_sliver_increment": 1000.0,
        "ltcg_sliver_increment": 1000.0,
    },
    "PA HOH Unsupported Overlay Demo": {
        "tax_year": 2026,
        "state_code": "PA",
        "filing_status": "head_of_household",
        "taxpayer_age": 50,
        "spouse_age": None,
        "ordinary_income": 210000.0,
        "ltcg_qd_income": 25000.0,
        "social_security_income": 0.0,
        "nontaxable_income": 0.0,
        "deduction_mode": "standard",
        "deduction_amount": 0.0,
        "nc_deduction_mode": "standard",
        "nc_itemized_deduction_amount": None,
        "ordinary_sliver_increment": 1000.0,
        "ltcg_sliver_increment": 1000.0,
    },
}


def _fmt_money(value: float | None) -> str:
    if value is None:
        return "Unsupported"
    return f"${value:,.2f}"


def _copy_with_updates(scenario: TaxScenarioInput, updates: dict) -> TaxScenarioInput:
    if hasattr(scenario, "model_copy"):
        return scenario.model_copy(update=updates)
    return scenario.copy(update=updates)


def _compute_nc_supported_value(
    scenario: TaxScenarioInput,
    federal_result: FederalTaxResult,
) -> SupportedValue:
    if scenario.state_code.upper() != "NC":
        return SupportedValue(
            supported=False,
            value=None,
            message="NC planning tax is only supported when state_code is NC.",
        )

    nc_ready_scenario = _copy_with_updates(
        scenario,
        {
            "federal_agi": federal_result.agi,
            "federal_taxable_social_security": federal_result.ss_output.taxable_social_security,
        },
    )
    nc_result = compute_nc_tax(nc_ready_scenario)
    return SupportedValue(
        supported=True,
        value=nc_result.nc_income_tax_before_credits,
        message=None,
    )


def _compute_projected_irmaa_supported_value(
    scenario: TaxScenarioInput,
    federal_result: FederalTaxResult,
) -> SupportedValue:
    filing_status = scenario.filing_status.value
    if filing_status not in {"single", "married_filing_jointly"}:
        return SupportedValue(
            supported=False,
            value=None,
            message=(
                "Projected 2028 IRMAA planning mode only supports single "
                "and married_filing_jointly."
            ),
        )

    irmaa_result = build_projected_2028_overlay_result(
        filing_status=filing_status,
        magi=federal_result.magi,
        magi_source="federal_result.magi",
    )
    return SupportedValue(
        supported=True,
        value=irmaa_result.annual_surcharge,
        message=None,
    )


def _render_tax_metrics(
    federal_result: FederalTaxResult,
    nc_tax: SupportedValue,
    projected_irmaa: SupportedValue,
) -> None:
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    col1.metric("Ordinary tax", _fmt_money(federal_result.ordinary_tax))
    col2.metric("LTCG/QD tax", _fmt_money(federal_result.ltcg_qd_tax))
    col3.metric("NIIT tax", _fmt_money(federal_result.niit_tax))

    col4.metric("Total federal tax", _fmt_money(federal_result.total_federal_tax))
    col5.metric("NC tax", _fmt_money(nc_tax.value))
    col6.metric(
        "Projected IRMAA annual surcharge",
        _fmt_money(projected_irmaa.value),
    )

    if not nc_tax.supported and nc_tax.message:
        st.info(f"NC unsupported: {nc_tax.message}")
    if not projected_irmaa.supported and projected_irmaa.message:
        st.info(f"Projected IRMAA unsupported: {projected_irmaa.message}")


def _render_delta_table(
    *,
    federal_ordinary_delta: float,
    federal_ltcg_qd_delta: float,
    federal_niit_delta: float,
    federal_total_delta: float,
    nc_delta: float | None,
    irmaa_delta: float | None,
) -> None:
    st.table(
        {
            "Metric": [
                "Ordinary tax delta",
                "LTCG/QD tax delta",
                "NIIT tax delta",
                "Total federal tax delta",
                "NC tax delta",
                "Projected IRMAA annual surcharge delta",
            ],
            "Value": [
                _fmt_money(federal_ordinary_delta),
                _fmt_money(federal_ltcg_qd_delta),
                _fmt_money(federal_niit_delta),
                _fmt_money(federal_total_delta),
                _fmt_money(nc_delta),
                _fmt_money(irmaa_delta),
            ],
        }
    )


def _load_preset_to_state(preset_name: str) -> None:
    preset = EXAMPLE_SCENARIOS[preset_name]
    for key, value in preset.items():
        st.session_state[key] = value


def _ensure_default_state() -> None:
    if "preset_loaded" not in st.session_state:
        _load_preset_to_state("NC Single Baseline")
        st.session_state.preset_loaded = True


def _build_scenario_from_state() -> TaxScenarioInput:
    return TaxScenarioInput(
        tax_year=int(st.session_state.tax_year),
        state_code=str(st.session_state.state_code).upper(),
        filing_status=st.session_state.filing_status,
        taxpayer_age=int(st.session_state.taxpayer_age),
        spouse_age=(
            int(st.session_state.spouse_age)
            if st.session_state.filing_status == FilingStatus.MARRIED_FILING_JOINTLY.value
            else None
        ),
        ordinary_income=float(st.session_state.ordinary_income),
        ltcg_qd_income=float(st.session_state.ltcg_qd_income),
        social_security_income=float(st.session_state.social_security_income),
        nontaxable_income=float(st.session_state.nontaxable_income),
        deduction_mode=st.session_state.deduction_mode,
        deduction_amount=float(st.session_state.deduction_amount),
        federal_agi=0.0,
        federal_taxable_social_security=0.0,
        net_nc_interest_dividend_adjustment=0.0,
        bailey_exempt_pension_amount=None,
        nc_deduction_mode=st.session_state.nc_deduction_mode,
        nc_itemized_deduction_amount=(
            float(st.session_state.nc_itemized_deduction_amount)
            if st.session_state.nc_deduction_mode == NCDeductionMode.ITEMIZED.value
            else None
        ),
    )


def main() -> None:
    st.set_page_config(page_title="Tax Planning Shell", layout="wide")
    st.title("Tax Planning Shell (Phase 39 Initial)")
    st.caption(
        "Minimal local testing shell. Uses existing federal, NC, NIIT, projected IRMAA, "
        "and sliver composition callables only."
    )

    _ensure_default_state()

    st.subheader("Example defaults")
    preset_name = st.selectbox("Choose preset", list(EXAMPLE_SCENARIOS.keys()))
    if st.button("Load preset values"):
        _load_preset_to_state(preset_name)

    with st.form("scenario_form"):
        st.subheader("Inputs")
        c1, c2, c3 = st.columns(3)

        c1.number_input("Tax year", key="tax_year", step=1)
        c2.text_input("State code", key="state_code")
        c3.selectbox(
            "Filing status",
            [status.value for status in FilingStatus],
            key="filing_status",
        )

        c4, c5, c6 = st.columns(3)
        c4.number_input("Taxpayer age", key="taxpayer_age", step=1)
        c5.number_input("Spouse age (MFJ only)", key="spouse_age", step=1, min_value=0)
        c6.selectbox(
            "Deduction mode",
            [mode.value for mode in DeductionMode],
            key="deduction_mode",
        )

        c7, c8, c9 = st.columns(3)
        c7.number_input("Deduction amount", key="deduction_amount", step=100.0)
        c8.selectbox(
            "NC deduction mode",
            [mode.value for mode in NCDeductionMode],
            key="nc_deduction_mode",
        )
        c9.number_input(
            "NC itemized deduction amount (required for NC itemized mode)",
            key="nc_itemized_deduction_amount",
            step=100.0,
        )

        c10, c11, c12 = st.columns(3)
        c10.number_input("Ordinary income", key="ordinary_income", step=1000.0)
        c11.number_input("LTCG/QD income", key="ltcg_qd_income", step=1000.0)
        c12.number_input("Social Security income", key="social_security_income", step=1000.0)

        c13, c14, c15 = st.columns(3)
        c13.number_input("Nontaxable income", key="nontaxable_income", step=1000.0)
        c14.number_input(
            "Ordinary-income sliver increment",
            key="ordinary_sliver_increment",
            min_value=1.0,
            step=100.0,
        )
        c15.number_input(
            "LTCG/QD sliver increment",
            key="ltcg_sliver_increment",
            min_value=1.0,
            step=100.0,
        )

        run = st.form_submit_button("Run planning analysis")

    if not run:
        return

    try:
        scenario = _build_scenario_from_state()

        baseline_federal = orchestrate_federal_tax(scenario)
        baseline_nc = _compute_nc_supported_value(scenario, baseline_federal)
        baseline_irmaa = _compute_projected_irmaa_supported_value(scenario, baseline_federal)

        ordinary_sliver = compose_additional_ordinary_income_sliver(
            scenario,
            additional_ordinary_income=float(st.session_state.ordinary_sliver_increment),
        )
        ltcg_sliver = compose_additional_ltcg_qd_income_sliver(
            scenario,
            additional_ltcg_qd_income=float(st.session_state.ltcg_sliver_increment),
        )
    except Exception as exc:  # noqa: BLE001
        st.error(str(exc))
        return

    st.subheader("Baseline results")
    _render_tax_metrics(baseline_federal, baseline_nc, baseline_irmaa)

    st.subheader("Ordinary-income sliver results")
    with st.expander("Baseline scenario", expanded=True):
        _render_tax_metrics(
            ordinary_sliver.baseline_federal_result,
            SupportedValue(
                ordinary_sliver.baseline_nc_result.supported,
                (
                    ordinary_sliver.baseline_nc_result.result.nc_income_tax_before_credits
                    if ordinary_sliver.baseline_nc_result.result is not None
                    else None
                ),
                ordinary_sliver.baseline_nc_result.message,
            ),
            SupportedValue(
                ordinary_sliver.baseline_projected_irmaa_2028.supported,
                (
                    ordinary_sliver.baseline_projected_irmaa_2028.result.annual_surcharge
                    if ordinary_sliver.baseline_projected_irmaa_2028.result is not None
                    else None
                ),
                ordinary_sliver.baseline_projected_irmaa_2028.message,
            ),
        )

    with st.expander("Altered scenario", expanded=True):
        _render_tax_metrics(
            ordinary_sliver.altered_federal_result,
            SupportedValue(
                ordinary_sliver.altered_nc_result.supported,
                (
                    ordinary_sliver.altered_nc_result.result.nc_income_tax_before_credits
                    if ordinary_sliver.altered_nc_result.result is not None
                    else None
                ),
                ordinary_sliver.altered_nc_result.message,
            ),
            SupportedValue(
                ordinary_sliver.altered_projected_irmaa_2028.supported,
                (
                    ordinary_sliver.altered_projected_irmaa_2028.result.annual_surcharge
                    if ordinary_sliver.altered_projected_irmaa_2028.result is not None
                    else None
                ),
                ordinary_sliver.altered_projected_irmaa_2028.message,
            ),
        )

    _render_delta_table(
        federal_ordinary_delta=ordinary_sliver.deltas.federal_ordinary_tax_delta,
        federal_ltcg_qd_delta=ordinary_sliver.deltas.federal_ltcg_qd_tax_delta,
        federal_niit_delta=ordinary_sliver.deltas.federal_niit_tax_delta,
        federal_total_delta=ordinary_sliver.deltas.federal_total_tax_delta,
        nc_delta=ordinary_sliver.deltas.nc_income_tax_before_credits_delta,
        irmaa_delta=ordinary_sliver.deltas.projected_irmaa_annual_surcharge_delta,
    )

    st.subheader("LTCG/QD sliver results")
    with st.expander("Baseline scenario", expanded=True):
        _render_tax_metrics(
            ltcg_sliver.baseline_federal_result,
            SupportedValue(
                ltcg_sliver.baseline_nc_result.supported,
                (
                    ltcg_sliver.baseline_nc_result.result.nc_income_tax_before_credits
                    if ltcg_sliver.baseline_nc_result.result is not None
                    else None
                ),
                ltcg_sliver.baseline_nc_result.message,
            ),
            SupportedValue(
                ltcg_sliver.baseline_projected_irmaa_2028.supported,
                (
                    ltcg_sliver.baseline_projected_irmaa_2028.result.annual_surcharge
                    if ltcg_sliver.baseline_projected_irmaa_2028.result is not None
                    else None
                ),
                ltcg_sliver.baseline_projected_irmaa_2028.message,
            ),
        )

    with st.expander("Altered scenario", expanded=True):
        _render_tax_metrics(
            ltcg_sliver.altered_federal_result,
            SupportedValue(
                ltcg_sliver.altered_nc_result.supported,
                (
                    ltcg_sliver.altered_nc_result.result.nc_income_tax_before_credits
                    if ltcg_sliver.altered_nc_result.result is not None
                    else None
                ),
                ltcg_sliver.altered_nc_result.message,
            ),
            SupportedValue(
                ltcg_sliver.altered_projected_irmaa_2028.supported,
                (
                    ltcg_sliver.altered_projected_irmaa_2028.result.annual_surcharge
                    if ltcg_sliver.altered_projected_irmaa_2028.result is not None
                    else None
                ),
                ltcg_sliver.altered_projected_irmaa_2028.message,
            ),
        )

    _render_delta_table(
        federal_ordinary_delta=ltcg_sliver.deltas.federal_ordinary_tax_delta,
        federal_ltcg_qd_delta=ltcg_sliver.deltas.federal_ltcg_qd_tax_delta,
        federal_niit_delta=ltcg_sliver.deltas.federal_niit_tax_delta,
        federal_total_delta=ltcg_sliver.deltas.federal_total_tax_delta,
        nc_delta=ltcg_sliver.deltas.nc_income_tax_before_credits_delta,
        irmaa_delta=ltcg_sliver.deltas.projected_irmaa_annual_surcharge_delta,
    )


if __name__ == "__main__":
    main()
