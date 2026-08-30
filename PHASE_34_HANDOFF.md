# Phase 34 Handoff — Projected 2028 IRMAA Planning Overlay

## Status

**Completed and pushed**

- Branch: `phase-2-social-security`
- Commit: `4f7e371` — `Refocus IRMAA on projected 2028 planning overlay`
- Verification: `python -m pytest -q` → **205 passed in 0.54s**

## Objective Completed

Phase 34 added a narrow, explainable, planning-only IRMAA overlay for evaluating the projected 2028 Medicare premium impact of 2026 MAGI decisions.

This remains separate from federal tax computation and NC tax computation. It is intentionally not described as an official CMS/SSA 2028 premium-year table, and it is not treated as federal income tax.

## What Was Added

- `models/irmaa.py` — immutable overlay result and threshold-row contract
- `rules/irmaa_projected_2028.py` — active projected 2028 planning table and lookup logic
- `tests/test_irmaa_contract.py` — core validation and math contract tests
- `tests/test_irmaa_projection.py` — planning overlay estimate metadata and threshold tests
- `rules/irmaa_2026.py` retained as reference-only, non-primary logic

## Planning Contract

The IRMAA overlay is intentionally explicit about its planning status.

Required metadata fields in the overlay output:

- `income_year = 2026`
- `premium_year = 2028`
- `is_estimate = True`
- `is_official = False`
- `estimate_basis = "Projected 2028 premium-year estimate based on 2026 MAGI planning"`
- `source_note = "Estimate only; not an official premium-year IRMAA table."`
- `rule_version = "projected_2028_v1"`

The contract still preserves the surcharge math fields:

- `part_b_monthly_surcharge`
- `part_d_monthly_surcharge`
- `total_monthly_surcharge`
- `annual_surcharge`

## Current Supported Scope

- Projected single-filer thresholds only
- Threshold starts: `113001`, `143001`, `179001`, `215001`, `500000`
- Separate overlay, not federal or NC tax computation
- No UI or orchestration integration yet
- No later official-2028 replacement or maintenance requirement
- Projection remains estimate-only and visibly labeled as such

## Preserved Boundaries and Limitations

- Not a complete Medicare enrollment, coverage, or premium estimator
- Not a tax engine and does not alter federal or NC calculations
- Projected values are assumptions and must remain visibly labeled
- No MFJ or other filing-status projection until expressly approved
- The reference 2026 table is not the default actionable planning path
- No attempt to imply that projected values are official CMS/SSA premium-year results

## Recommended Next Decision

Choose one narrow direction:

A. Define how a completed planning scenario can compose/display the separate projected IRMAA overlay without changing tax calculations.
B. Evaluate whether projected MFJ IRMAA support is needed for actual planning scenarios.
C. Resume the paused presentation/SVG review.
D. Narrow NC planning refinement/reconciliation work.

## Diff Summary

- Added: `PHASE_34_HANDOFF.md`
- Updated: `PROJECT_SCOPE.md` to reflect that IRMAA is now an implemented, estimate-only planning overlay rather than a future or hypothetical module.
- Updated: `NEXT_PHASE_ROADMAP.md` to mark the Phase 34 IRMAA planning overlay as complete and remove the implied official-2026 rule-table path from near-term planning.
- Phase implementation files retained: `models/irmaa.py`, `rules/irmaa_projected_2028.py`, `rules/irmaa_2026.py`, `tests/test_irmaa_contract.py`, `tests/test_irmaa_projection.py`.
