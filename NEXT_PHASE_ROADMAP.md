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

### Candidate Phase 35 — Projected 2028 MFJ IRMAA Planning Support

Scope candidate:
- estimate-only projected MFJ thresholds and surcharge lookup,
- explicit metadata retained,
- no tax-engine coupling, UI, or orchestration.

Out of scope:
- official premium-year maintenance,
- federal tax calculation changes,
- state-tax integration,
- UI or app work,
- broader Medicare logic beyond the approved projected planning overlay.

### Candidate Phase 36 — Manual Scenario Exploration Harness

Scope candidate:
- small local/manual scenario-entry and result-inspection tool,
- intended to test many user-created scenarios and identify major issues before Streamlit,
- reuses existing engines; does not duplicate formulas,
- output sections remain distinct for federal tax, supported state tax, NIIT, and projected IRMAA.

Out of scope:
- polished consumer UI,
- new tax formulas,
- state-credit expansion,
- IRMAA integration into tax calculations,
- final product styling or app shell design.

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

### Candidate Phase 39 — Initial Streamlit Planning App

Scope candidate:
- consumer UI built on already-tested inputs and composed outputs,
- no new tax logic invented in the UI layer.

Out of scope:
- re-deriving or reimplementing tax formulas in the front end,
- arbitrary state or Medicare expansions,
- broad feature scope before the contract and harness are stable.

## Deferred work

- Federal SVG presentation clarity pass remains a low-priority deferred item.
- Resume it only if needed to support the manual scenario harness or Streamlit consumer experience.
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

## Acceptance style for the next implementation phase

- Narrow and presentation-focused.
- No tax formula changes unless a verified defect is found first.
- Deterministic SVG output preserved.
- Focused tests added or updated first.
- Full test suite must pass.
- Generated artifacts stay untracked.