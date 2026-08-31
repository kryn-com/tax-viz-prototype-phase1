# Phase 36 Handoff - Manual Scenario Exploration Harness

## Status
Completed.

- Branch: `phase-2-social-security`
- Verification:
  - `python -m pytest tests/test_manual_scenario_harness.py -q`
  - `python -m pytest tests/test_federal_orchestrator.py -q`
  - `python -m pytest tests/test_state_contract.py -q`
  - `python -m pytest tests/test_irmaa_projection.py -q`
  - `python -m pytest -q`
- Result: 223 passed

## Objective completed
Phase 36 added a small local/manual scenario exploration harness for validating existing federal, NC planning, NIIT, and projected IRMAA results before any UI or app work.

The harness reuses existing public call paths and result contracts without duplicating formulas or changing engine interfaces. It keeps the four domains visibly separate: federal tax, North Carolina planning, NIIT, and projected IRMAA.

## What changed
- Added a local/manual harness entry point in `scripts/manual_scenario_harness.py`.
- Added a Phase 36 sample input at `scripts/sample_inputs/phase36_demo.json` outside the curated scenario catalog so it is not picked up by the curated scenario runner.
- Reused the approved public paths:
  - `orchestrate_federal_tax(...)` from `engines.federal_orchestrator`
  - `orchestrate_nc_planning(...)` from `planning.nc_coordinator`
  - `build_projected_2028_overlay_result(...)` from `rules.irmaa_projected_2028`
- Kept output sections separate as:
  - `federal`
  - `north_carolina`
  - `niit`
  - `projected_irmaa_2028`
- Preserved the existing result contracts and kept NIIT sourced from the federal result path rather than a separate recomputation.

## Files changed
- `scripts/manual_scenario_harness.py`
- `scripts/sample_inputs/phase36_demo.json`
- `tests/test_manual_scenario_harness.py`

## Tests added or updated
- Added focused Phase 36 harness tests covering:
  - happy path with separate output sections
  - unsupported projected IRMAA handling remains explicit and separate
  - NIIT is exposed as its own output section from the federal result contract
  - required top-level section names remain stable

## Verification
- Focused harness tests passed.
- Scenario runner tests passed.
- Full suite baseline is now 223 passing tests.

## Preserved boundaries / out of scope still unchanged
- No tax formulas were changed.
- No engine interfaces were changed.
- No Streamlit or UI work was introduced.
- No new domain contract beyond the local harness output wrapper was introduced.
- IRMAA remains estimate-only projected 2028 planning support for `single` and `married_filing_jointly`.
- IRMAA remains separate from federal tax calculations and NC tax calculations.
- The curated scenario runner contract remains unchanged.

## Current limitations
- This is a local/manual harness only; it is not a user-facing app.
- The sample input is intentionally kept out of the curated scenario catalog.
- Projected IRMAA remains estimate-only and separate from the tax engines.
- Unsupported projected IRMAA statuses remain explicitly rejected rather than silently folded into tax calculations.

## Recommended next decision
Proceed to Phase 37 - Planning Scenario Composition Contract.

This remains the narrow recommended follow-up: typed composition of existing federal, NC, and IRMAA results without merging engines or formulas, and without introducing UI or broader state/Medicare behavior.
