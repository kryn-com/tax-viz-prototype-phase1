# Phase 39 Handoff - Initial Streamlit Planning Shell

## Status

Completed: initial thin Streamlit planning shell for local testing.

## Objective

Expose the current tested planning paths through a minimal local app without adding tax formulas, changing engine interfaces, or merging federal, NC, NIIT, and projected IRMAA results.

## Implemented

- Added a Streamlit entry point in `streamlit_app.py`.
- Added simple inputs for the current `TaxScenarioInput` planning fields and both supported sliver increments.
- Added two example defaults so the app can run immediately:
  - an NC Single baseline scenario,
  - a Head of Household / non-NC scenario that demonstrates unsupported NC and projected IRMAA messages.
- Added a run action with separate sections for:
  - baseline results,
  - ordinary-income sliver results,
  - LTCG/QD sliver results.
- Displayed separate rows for ordinary tax, LTCG/QD tax, NIIT tax, total federal tax, NC tax when supported, and projected IRMAA annual surcharge when supported.
- Displayed explicit unsupported-case messages for NC and projected IRMAA rather than silently omitting values.
- Reused the existing federal orchestrator, NC tax callable, projected IRMAA builder, and ordinary-income/LTCG-QD composition callables.
- Added the Streamlit runtime dependency to `requirements.txt`.

## Verification

Focused planning tests:

- `pytest tests/test_manual_scenario_harness.py tests/test_ordinary_income_sliver_composition.py tests/test_ltcg_qd_sliver_composition.py -q` - 18 passed

Full suite:

- `pytest -q` - 302 passed

The full suite result is recorded as the current verified baseline; no additional test run is required for this documentation-only closeout.

## Changed Files In This Baseline

Phase 38C provisional validation path:

- `engines/federal_ordinary.py`
- `scripts/scenario_runner.py`
- `tests/test_engines.py`
- `tests/test_scenario_runner.py`
- `tests/fixtures/phase38a_sample_bank.csv`

Ordinary-income sliver composition:

- `models/ordinary_income_sliver.py`
- `planning/ordinary_income_sliver.py`
- `tests/test_ordinary_income_sliver_composition.py`

LTCG/QD sliver composition:

- `models/ltcg_qd_sliver.py`
- `planning/ltcg_qd_sliver.py`
- `tests/test_ltcg_qd_sliver_composition.py`

Initial local app shell:

- `streamlit_app.py`
- `requirements.txt`

## Preserved Boundaries

- The exact federal planning path remains the default path.
- Printed-tax-table behavior remains provisional and validation-only for the below-100,000 comparison path; it does not alter federal planning outputs.
- Federal tax, NC planning tax, NIIT, and projected IRMAA remain separate outputs and concerns.
- The app does not create a combined federal + NC + NIIT + IRMAA total contract.
- The Streamlit shell is a thin local-testing wrapper over existing tested callables only.
- The ordinary-income and LTCG/QD sliver compositions recompute the applicable existing pipelines rather than duplicating tax formulas in the UI.
- Projected IRMAA remains an estimate-only 2028 overlay for 2026 planning and is supported only for Single and Married Filing Jointly.
- NC display remains limited to the existing NC planning callable and its supported state boundary.

## Provisional Printed-Tax-Table Validation Policy

The project-controlled provisional policy applies only to independent validation comparisons for taxable ordinary income below 100,000. It maps income to the applicable IRS-style interval, uses the interval midpoint, applies the supported 2026 statutory rate schedule, and rounds the reproduced result to whole dollars using half-up rounding. At 100,000 and above, validation uses the exact schedule method.

The exact federal planning calculation remains unchanged and is still the default. When the official 2026 IRS printed tax table is available, representative ranges must be revalidated and the policy or implementation revised only if official material requires it.

## Streamlit Shell Scope And Limitations

The shell is intentionally minimal and testing-oriented. It accepts the current scenario inputs, runs the baseline and two independent sliver compositions, and exposes separate backend results and deltas. It does not provide charts, exports, persistence, authentication, tax filing behavior, tax advice, broader state treatment, expanded Medicare behavior, or new scenario orchestration.

The current shell also does not replace the manual scenario harness or scenario-bank validation workflow. Those remain useful for deterministic inspection and expected-versus-actual validation.

## Deferred Work

- Feedback-driven Streamlit refinement after local user testing.
- Validation-workflow cleanup or a small app-facing helper only where feedback identifies a concrete need.
- Any broader UI redesign, chart integration, export flow, persistence, or product expansion.
- Official future-premium-year IRMAA maintenance and unsupported filing-status expansion.
- New tax formulas, tax-engine changes, combined totals, and broader state-tax integration.

## Recommended Next Phase

Proceed with a narrow feedback-driven Streamlit refinement and validation-workflow cleanup phase. Use local testing feedback to identify one or two concrete usability or validation issues, preserve the current backend and domain boundaries, and avoid broad product expansion.
