# Post-Phase-34 Roadmap Reset

## Current Position

Phase 34 is complete and pushed. It added a projected 2028 IRMAA planning overlay for 2026 MAGI decisions. The repository now includes a separate projected single-filer IRMAA overlay, and the pre-credit NC planning layer remains a separate concern from federal tax computation. The verified implementation baseline before the documentation reset was 205 passing tests.

## Product Direction

The intended future user experience is: 

- the user enters current-year planning information;
- the app presents federal tax, supported state tax, NIIT, and projected IRMAA two years ahead as separate but related outputs;
- the app later provides sliver analysis for incremental ordinary income and LTCG/QD income;
- Streamlit is a future consumer layer, not the next immediate implementation step.

## Approved Sequencing Recommendation

1. Phase 35 — Projected 2028 MFJ IRMAA Planning Support
   - estimate-only projected MFJ thresholds and surcharge lookup
   - explicit metadata retained
   - no tax-engine coupling, UI, or orchestration

2. Phase 36 — Manual Scenario Exploration Harness
   - small local/manual scenario-entry and result-inspection tool
   - intended to test many user-created scenarios and identify major issues before Streamlit
   - reuses existing engines; does not duplicate formulas
   - output sections remain distinct for federal tax, supported state tax, NIIT, and projected IRMAA

3. Phase 37 — Planning Scenario Composition Contract
   - typed deterministic composition of existing federal, NC, and IRMAA results
   - no merging of engines or tax calculations
   - app-ready consumer contract

4. Phase 38 — Incremental-Income Sliver Analysis
   - additional ordinary-income and LTCG/QD analysis
   - full applicable recomputation of federal tax, supported state tax, NIIT, and projected IRMAA for each altered scenario where inputs and support exist
   - explain separate federal, state, NIIT, and IRMAA effects where supported

5. Phase 39 — Initial Streamlit Planning App
   - consumer UI built on already-tested inputs and composed outputs
   - no new tax logic invented in the UI layer

## Deferred Work

- Federal SVG presentation clarity pass is low priority.
- Resume it only if needed to support the manual scenario harness or Streamlit consumer experience.
- Do not reopen official future premium-year maintenance as a routine obligation.
- Do not expand tax credits, broader state treatment, or unsupported Medicare logic without explicit approval.

## Handoff Instructions

A future Phase 35 chat should begin by reading:

- PROJECT_SCOPE.md
- NEXT_PHASE_ROADMAP.md
- PHASE_34_HANDOFF.md
- POST_PHASE_34_ROADMAP_RESET.md
- models/irmaa.py
- rules/irmaa_projected_2028.py
- relevant IRMAA tests
