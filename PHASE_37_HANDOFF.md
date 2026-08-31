# Phase 37 Handoff - Planning Scenario Composition Contract

## Status
Completed.

- Branch: `phase-2-social-security`
- Implementation commit: `58f1d03`
- Verification:
  - python -m pytest tests/test_planning_scenario_contract.py -q
  - python -m pytest tests/test_federal_orchestrator.py -q
  - python -m pytest tests/test_state_contract.py -q
  - python -m pytest tests/test_irmaa_projection.py -q
  - python -m pytest -q
- Result: 226 passed

## Objective completed
Phase 37 added a typed deterministic planning scenario composition contract as a minimal frozen sidecar wrapper around the existing federal, NC planning, and projected IRMAA results.

The implementation keeps all domains separate and does not introduce any new orchestration layer, tax calculation, or merged totals contract.

## What changed
- Added `models/planning_scenario.py`.
- Added `PlanningScenarioResult`, a frozen sidecar wrapper with the approved fields:
  - `scenario`
  - `federal_result`
  - `nc_planning_result`
  - `projected_irmaa_2028`
- Kept NIIT owned by `FederalTaxResult` and reachable via `federal_result.niit_output`.
- Kept the existing result contracts and public call paths unchanged.
- Added focused contract tests covering immutability, exact object identity preservation, and absence of duplicate/combined totals fields.
- No compose function or new orchestrator was added.
- No tax formulas, engine interfaces, or filing-status behavior were changed.
- No combined totals were introduced.

## Files changed
- models/planning_scenario.py
- tests/test_planning_scenario_contract.py

## Tests added or updated
- Added focused Phase 37 contract tests covering:
  - immutability of the frozen wrapper
  - exact object identity preservation
  - absence of combined or duplicated top-level fields

## Verification
- Focused contract tests passed.
- Focused federal orchestrator, state contract, and IRMAA projection suites passed.
- Full suite baseline is now 226 passing tests.

## Preserved boundaries / out of scope still unchanged
- No tax formulas were changed.
- No engine interfaces were changed.
- No new orchestrator was introduced.
- No Streamlit or UI work was introduced.
- No combined federal+NC+IRMAA totals contract was introduced.
- IRMAA remains a separate estimate-only projected 2028 planning overlay for `single` and `married_filing_jointly`.
- NIIT remains a federal-result-owned component rather than a duplicated top-level wrapper field.

## Current limitations
- This is a typed sidecar composition contract only; it does not implement a user-facing app.
- The wrapper does not add new tax logic, state expansion, or broader Medicare behavior.
- IRMAA remains estimate-only and separate from the actual federal and NC tax calculations.
- The supported projected IRMAA statuses remain limited to `single` and `married_filing_jointly`.

## Recommended next decision
Proceed to Phase 38 - Incremental-Income Sliver Analysis.

This remains the narrow next follow-up: recompute the applicable federal pipeline for incremental ordinary and LTCG/QD scenarios while preserving the existing federal, NC, NIIT, and projected IRMAA boundaries.
