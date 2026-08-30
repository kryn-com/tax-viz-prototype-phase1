# Phase 35 Handoff — Projected 2028 MFJ IRMAA Planning Support

## Status
Completed and committed.

- Branch: `phase-2-social-security`
- Commit: `0a1aa30` — Add projected 2028 MFJ IRMAA planning support
- Verification:
  - `python -m pytest tests/test_irmaa_projection.py -q`
  - `python -m pytest tests/test_irmaa_contract.py -q`
  - `python -m pytest -q`
- Result: 219 passed

## Objective completed
Phase 35 extended the existing estimate-only projected 2028 IRMAA planning overlay to support `married_filing_jointly` as a narrow additive extension of the completed single-filer path.

This work remained separate from federal tax computation and North Carolina tax computation. It did not introduce UI, orchestration, Streamlit, official future-premium-year maintenance, or broader Medicare logic.

## What changed
- Added projected 2028 MFJ threshold rows to the active projected IRMAA rule table in `rules/irmaa_projected_2028.py`.
- Extended projected lookup/build support to allow `married_filing_jointly` alongside the existing `single` path.
- Preserved existing estimate-only metadata behavior:
  - `income_year = 2026`
  - `premium_year = 2028`
  - `is_estimate = True`
  - `is_official = False`
  - `estimate_basis` unchanged
  - `source_note` unchanged
  - `rule_version = projected_2028_v1`
- Preserved surcharge math and annualized surcharge behavior.
- Kept unsupported projected statuses rejected.
- Preserved existing projected single-filer behavior unchanged.

## Projected MFJ thresholds added
Projected MFJ threshold starts:
- 226001
- 286001
- 358001
- 430001
- 750000

Projected MFJ surcharge tiers:
- Tier 1: Part B `89.00`, Part D `15.80`
- Tier 2: Part B `224.00`, Part D `40.60`
- Tier 3: Part B `358.00`, Part D `65.50`
- Tier 4: Part B `492.00`, Part D `90.20`
- Tier 5: Part B `537.00`, Part D `98.80`

## Files changed
- `rules/irmaa_projected_2028.py`
- `tests/test_irmaa_projection.py`

## Tests added or updated
- Unsupported projected statuses remain rejected.
- MFJ threshold boundary coverage at exact tier starts.
- MFJ surcharge value coverage by tier.
- MFJ estimate-only metadata coverage.
- MFJ total monthly and annual surcharge math coverage.
- Regression coverage confirming projected single-filer behavior remains unchanged.

## Current supported IRMAA scope
- Separate projected 2028 planning overlay for 2026 MAGI decisions
- Supported projected filing statuses:
  - `single`
  - `married_filing_jointly`

Still out of scope:
- Official 2028 premium-year maintenance
- HOH, MFS, or broader filing-status expansion
- Federal-tax or NC-tax integration
- UI, orchestration, Streamlit, or presentation work
- Broader Medicare enrollment or premium modeling

## Current verified baseline
The verified full-suite baseline is now 219 passing tests.

## Recommended next decision
Return to the approved roadmap sequence after Phase 35:
1. Phase 36 manual scenario exploration harness
2. Phase 37 planning scenario composition contract
3. Phase 38 incremental-income sliver analysis
4. Phase 39 initial Streamlit planning app

## Next-phase guardrails

Phase 36 should be a small local/manual scenario-entry and result-inspection
harness for validating existing capabilities before any Streamlit work.

It should reuse existing federal, NC planning, NIIT, and projected IRMAA engines
and result contracts without duplicating formulas or merging their calculations.
Its output must keep federal tax, supported state tax, NIIT, and projected IRMAA
as distinct sections.

Still out of scope for Phase 36:
- New tax formulas or tax-engine changes
- IRMAA integration into federal or NC tax calculations
- State-credit expansion or broader state-tax treatment
- Polished consumer UI, final styling, or application-shell work

## Documentation convention

Beginning after Phase 35, each completed phase should produce one consolidated
`PHASE_XX_HANDOFF.md` rather than both a phase handoff and a separate post-phase
roadmap-reset document.

The consolidated handoff must record the completed work, verification, durable
scope decisions, current limitations, and the recommended next narrow phase.

`PROJECT_SCOPE.md` remains the durable project source of truth, and
`NEXT_PHASE_ROADMAP.md` remains the forward-looking sequencing document.

## Read first next session

Before planning or implementing Phase 36, read:
- `PROJECT_SCOPE.md`
- `NEXT_PHASE_ROADMAP.md`
- `PHASE_35_HANDOFF.md`
- The current public interfaces and focused tests for the federal, NC planning,
  NIIT, and projected IRMAA result paths that Phase 36 would reuse