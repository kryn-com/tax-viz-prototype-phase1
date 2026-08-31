# Federal Tax Stack — Next Development Roadmap

## Goal

Plan the next narrow development batch for the federal tax-stack report and related sliver output, without changing approved federal tax formulas or crossing presentation/state/IRMAA boundaries.

## Working assumptions

- The repository remains a deterministic 2026 federal tax prototype.
- Work must stay within one narrow approved phase at a time.
- Federal tax formulas, supported filing-status policy, and engine interfaces should remain unchanged unless a separate tax-core defect is proven.
- State tax remains a separate future module; IRMAA is now a separate projected 2028 planning overlay and not a federal tax module.
- The current baseline includes deterministic SVG generation and curated scenario review artifacts.

## Requested changes grouped by type

### A. Safe presentation/layout changes for the federal tax-stack report

These appear suitable for one narrow presentation-focused phase:

1. Right-align all dollar amounts while visually separating or left-aligning the dollar sign in an accounting-table style.
2. Use a clearer two-column income layout showing taxable and non-taxable amounts separately where applicable.
3. Remove the taxable Social Security footnote if the visual itself becomes self-explanatory.
4. Change the Social Security box heading/explanation wording to "Taxability".
5. Right-align the numbers in the Social Security section consistently with the rest of the report.
6. Remove unnecessary footnotes in the Social Security box.
7. Simplify or remove the NIIT notice when NIIT does not apply.
8. Rearrange zones to reduce wasted white space.
9. Use a more modern font if that can be done deterministically and safely in SVG output.

### B. Presentation changes that need explicit semantic decisions before implementation

These should be clarified in the proposal before coding:

1. Effective rate definition: whether it should be total federal tax divided by AGI, taxable income, or another displayed base.
2. Deduction-zone redesign:
   - label the full deduction area as a 0% tax bracket,
   - show the deduction amount inside the zone,
   - show computed tax on the right as `$ 0`,
   - ensure no marginal layer visually overwrites the deduction zone.
3. Two-column income presentation details:
   - which rows get taxable and non-taxable splits,
   - whether deduction should appear as a taxable-side reduction row to support AGI display,
   - how Social Security split amounts should be shown without implying double counting.

### C. Separate future sliver-analysis phase

This should likely be a different phase from the tax-stack layout pass:

1. Create one new sliver report.
2. Show remaining room in the current ordinary-income bracket.
3. Explain how each additional $100 of ordinary income changes total federal tax.
4. Recompute the full pipeline so the sliver can reflect ordinary-tax effects, possible taxable-Social-Security changes, and possible LTCG/QD stacking effects.

## Recommended phase split

### Candidate Phase 34 — Projected IRMAA Planning Overlay Completion

This phase is now complete.

### Phase 35 — Projected 2028 MFJ IRMAA Planning Support — Complete

Completed scope:
- Added estimate-only projected 2028 `married_filing_jointly` threshold and surcharge lookup alongside the existing Single path
- Preserved the existing IRMAA result contract, surcharge math, validation patterns, and estimate metadata
- Preserved Single projected-overlay behavior unchanged
- Kept unsupported projected filing statuses rejected
- Kept IRMAA separate from federal tax, NC tax, UI, and orchestration

Verification:
- Focused IRMAA projection and contract tests passed
- Full suite: 219 passed

Still out of scope:
- Official future-premium-year maintenance
- HOH, MFS, or other filing-status support
- Federal-tax or state-tax integration
- UI, Streamlit, scenario composition, sliver analysis, or presentation work

### Phase 36 — Manual Scenario Exploration Harness

Scope candidate:
- Small local/manual scenario-entry and result-inspection tool
- Reuse existing federal, NC, and projected IRMAA engines without duplicating formulas
- Keep federal tax, supported state tax, NIIT, and projected IRMAA results visibly separate
- Use the harness for validation and discovery before Streamlit work

Out of scope:
- Polished consumer UI
- New tax formulas
- IRMAA integration into tax calculations
- State-credit expansion
- Final product styling or app-shell design

### Candidate Phase 37 — Planning Scenario Composition Contract

Scope candidate:
- typed deterministic composition of existing federal, NC, and IRMAA results,
- no merging of engines or tax calculations,
- app-ready consumer contract.

Out of scope:
- user interface implementation,
- new tax logic,
- broader state or Medicare behavior beyond the supported results.

### Candidate Phase 38 — Incremental-Income Sliver Analysis

Scope candidate:
- additional ordinary-income and LTCG/QD analysis,
- full applicable recomputation of federal tax, supported state tax, NIIT, and projected IRMAA for each altered scenario where inputs and support exist,
- explain separate federal, state, NIIT, and IRMAA effects where supported.

Out of scope:
- Streamlit app construction,
- UI-only simulation,
- unsupported Medicare logic,
- tax-core rework beyond scenario recomputation.

### Phase 39 — Initial Streamlit Planning App — Complete

Completed scope:
- Added a minimal local Streamlit entry point in `streamlit_app.py`.
- Reused existing typed inputs, federal orchestration, NC planning, projected IRMAA, and ordinary-income/LTCG-QD sliver composition callables.
- Added baseline, ordinary-income sliver, and LTCG/QD sliver result sections.
- Kept federal tax, NC tax, NIIT, and projected IRMAA visibly separate.
- Added explicit unsupported-case messages and example default scenarios.
- Verified the focused harness/sliver suite with 18 passed tests and the full suite with 302 passed tests.

Preserved boundaries:
- re-deriving or reimplementing tax formulas in the front end,
- arbitrary state or Medicare expansions,
- combined federal, NC, NIIT, or projected IRMAA totals,
- broad product scope before local testing feedback.

### Next Likely Phase — Feedback-Driven Streamlit Refinement and Validation Cleanup

Scope candidate:
- collect local testing feedback on the initial shell,
- address one or two concrete usability or validation-workflow issues,
- keep the app thin and aligned with existing backend contracts,
- clarify or simplify result inspection where feedback identifies a need.

Out of scope:
- new tax formulas or engine changes,
- broad product redesign,
- chart/export/persistence architecture,
- expanded state or Medicare treatment,
- combined tax totals.

## Deferred Work

- Federal SVG presentation clarity pass remains a low-priority deferred item.
- Resume it only if needed to support the manual scenario harness or Streamlit consumer experience.
- Initial Streamlit shell refinement remains deferred until local testing feedback identifies a narrow target.
- Do not reopen official future premium-year maintenance as a routine obligation.
- Do not expand tax credits, broader state treatment, or unsupported Medicare logic without explicit approval.

## Open design questions to resolve before implementation

1. Is effective rate defined here as:
   - total federal tax / AGI, or
   - total federal tax / total economic income, or
   - total federal tax / taxable income?
2. Should AGI be displayed directly in the report header or income table?
3. Should the NIIT area be omitted entirely when NIIT = 0, or should it remain as a simple one-line “NIIT does not apply” message?
4. Should the deduction zone say “0% tax bracket,” “deduction zone,” or some hybrid label?
5. Should Social Security show:
   - total SS,
   - taxable SS,
   - non-taxable SS,
   in a split row, or in a dedicated taxability panel?

## Acceptance Style For The Next Implementation Phase

- Narrow and feedback-driven.
- Focused on Streamlit usability or validation-workflow cleanup.
- No tax formula changes unless a verified defect is found first.
- Deterministic SVG output preserved.
- Focused tests added or updated first.
- Full test suite must pass.
- Generated artifacts stay untracked.