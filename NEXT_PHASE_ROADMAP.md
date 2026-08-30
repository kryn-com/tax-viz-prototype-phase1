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

### Candidate Phase 35 — Federal Tax Stack Presentation Clarity Pass

Scope candidate:
- accounting-style numeric alignment,
- improved taxable/non-taxable row presentation,
- SS wording cleanup,
- NIIT simplification/removal when not applicable,
- deduction-zone label and layout cleanup,
- whitespace reduction,
- deterministic font modernization if technically safe.

Out of scope:
- ordinary-tax engine changes,
- LTCG/QD engine changes,
- NIIT formula changes,
- state-tax integration,
- IRMAA calculation, threshold expansion, or integration,
- interactive UI,
- new sliver computations.

### Candidate Phase 36 — Ordinary-Income Sliver Audit Report

Scope candidate:
- one deterministic sliver artifact/report for additional ordinary income,
- remaining-room-in-current-bracket indicator,
- explanation of how each additional $100 affects the total federal picture,
- full federal recomputation for each sliver scenario.

Out of scope:
- interactive sliders,
- LTCG-only sliver mode,
- state tax,
- IRMAA,
- redesign of the baseline tax-stack renderer except for any minimal shared formatting needed by the sliver report.

## Next logical deferred options

1. Define a separate composition/display boundary that can present the projected IRMAA overlay alongside a completed planning scenario without coupling it to federal or NC tax computation.
2. Evaluate projected MFJ IRMAA support only if actual planning scenarios require it and projected inputs are expressly approved.
3. Maintain or update official IRMAA reference tables only if a clearly defined non-planning use is approved.
4. Resume the paused federal tax-stack presentation/SVG clarity pass.

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