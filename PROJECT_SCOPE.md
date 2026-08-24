# Project Scope — 2026 Federal Tax Prototype

## Purpose

This repository is a deterministic, explainable Python prototype for selected 2026 federal income-tax calculations. It is an analytical and educational model intended to support a future tax-visualization application; it is not a tax-preparation, tax-filing, or e-file product.

This document is the durable source of truth for future development sessions and the project owner. Before proposing or implementing work, read the current repository, this document, and the most recent phase handoff document.

## Current Status

Phases 1 through 31 are complete in the current prototype. Phases 22 through 25 completed the baseline federal tax-stack view model and SVG renderer, the deterministic predefined-demo and curated-scenario runner, and related auditability refinements. Phases 26 through 29 corrected and source-audited the supported 2026 ordinary-income bracket tables for Single, Married Filing Jointly, and Head of Household; added reviewed MFJ and HOH scenario fixtures; expanded exact-threshold and scenario-catalog coverage; and documented the resulting validation baseline. Phase 30 reconciled the durable project documentation, clarified that MFS rule-table data is inactive because the federal orchestrator rejects that filing status, and added a manual scenario-validation runbook for independent comparison with external tax calculators. Phase 31 enforced the filing-status standard-deduction floor for explicit deductions when the supplied amount is lower than standard, aligned LTCG/QD stacking with deduction-aware taxable ordinary income, updated direct regression coverage, and reconciled the scenario-runner catalog to the current 25 curated cases. The current verified test baseline is 170 passing tests.

Phase 13 completed state-contract and state-tax policy test hardening. No production code changed, and the full test suite passed with 90 tests.

Phase 14 added the Federal Display Model, a deterministic federal-only display-model layer for future visualization work. No tax logic recalculation changes were made, and the full test suite passed with 95 tests.

Phase 15 added deterministic federal display text formatting that consumes the Federal Display Model. No tax logic recalculation changes were made; the focused tests passed with 3 tests, and the full suite passed with 98 tests.

Phase 16 added deterministic federal sliver display models and text summaries for ordinary-income, LTCG/QD, and combined-income sliver results.

Phase 17 added baseline and altered federal component breakdowns for ordinary tax, LTCG/QD tax, NIIT, and total federal tax.

Phase 18 hardened the sliver presentation contract through focused tests covering component mapping, backward-compatible construction, incomplete optional data, delta arithmetic, formatting, and determinism. No production code changed in this phase.

Phase 19 added an immutable, chart-library-neutral federal chart view model containing ordered tax-component, ordinary-bracket, and preferential-rate segments.

Phase 20 added a deterministic renderer that converts the federal chart view model into a standalone SVG without a chart-library dependency.

Phase 21 added a predefined, non-interactive federal scenario demo that runs the existing pipeline and writes a standalone SVG chart.

The current end-to-end capability is:

```text
curated JSON scenario fixture
-> validated TaxScenarioInput
-> federal tax orchestration
-> federal display model
-> federal tax-stack and chart view models
-> deterministic result.json and standalone tax-stack SVG review artifacts
```

The current repository remains a prototype. Its outputs must stay deterministic, side-effect free, auditable, and test-led.

## Completed Federal Core

The current 2026 federal prototype includes:

- Strict typed scenario validation through Pydantic `TaxScenarioInput`
- A versionable federal-rule structure centered on `rules.federal.year_2026`
- A federal ordinary-income tax engine that produces taxable ordinary income, total ordinary tax, and a detailed bracket trace
- A Social Security taxability engine using provisional-income mechanics and statutory limits
- An LTCG/qualified-dividend engine that stacks combined preferential income above deduction-adjusted taxable ordinary income and traces the 0%, 15%, and 20% rate-band amounts
- A standalone NIIT engine that calculates the NIIT base and 3.8% liability from MAGI and net-investment-income inputs
- A Federal Pipeline Orchestrator that runs the completed engines in dependency order and returns a unified `FederalTaxResult`
- An isolated typed and numeric state-tax boundary for selected flat-tax and no-income-tax states
- Automated tests for individual engines and the Phase 3 orchestrator

## Phase 3 Result

The Phase 3 public entry point is:

```python
orchestrate_federal_tax(scenario: TaxScenarioInput) -> FederalTaxResult
```

The orchestrator:

1. Explicitly rejects Married Filing Separately.
2. Calculates taxable Social Security.
3. Creates an effective scenario that adds taxable Social Security to ordinary income.
4. Calculates ordinary-income tax using that effective scenario.
5. Calculates LTCG/QD tax using that effective scenario, preserving ordinary-income stacking behavior.
6. Calculates prototype AGI and MAGI.
7. Maps `ltcg_qd_income` to NIIT net investment income for the current prototype.
8. Returns preserved component outputs and transparent aggregate federal-tax totals.

The aggregate federal total is:

```text
ordinary tax + LTCG/QD tax + NIIT tax
```

### Actual Engine Interfaces

The orchestrator must adapt to existing engine interfaces; completed engines should not be renamed or rewritten merely to suit a future orchestration layer.

```python
compute_taxable_social_security(
    scenario: TaxScenarioInput,
) -> SocialSecurityOutput

compute_federal_ordinary_tax(
    scenario: TaxScenarioInput,
) -> FederalOrdinaryOutput

compute_preferential_tax(
    scenario: TaxScenarioInput,
) -> LTCG_QD_Output

compute_niit(
    filing_status: FilingStatus,
    magi: float,
    net_investment_income: float,
) -> NIITOutput

compute_taxable_ordinary_income(
    ordinary_income: float,
    deduction_amount: float,
) -> float
```

The deductions helper returns a scalar taxable-ordinary-income value. It does not currently return a separate structured deduction-output object, so `FederalTaxResult` must not invent or imply one.

For the current prototype, the applied deduction at the ordinary-tax boundary is the greater of the supplied explicit deduction amount and the filing-status standard deduction. Preferential LTCG/QD stacking must use the same resolved applied deduction so that ordinary-income taxation and preferential-rate calculations remain internally consistent.

## Current Constraints

The following remain outside the current approved product scope:

- User-entered scenario variables and interactive application behavior
- Baseline tax-stack view-model and renderer work beyond the current federal chart surface
- General-purpose CLI behavior, serialization, export architecture, and chart-library integration
- Progressive and multi-bracket state income-tax calculations
- IRMAA calculations or Medicare-premium determinations
- Tax credits
- Alternative Minimum Tax
- Payroll tax, self-employment tax, and business-entity taxation
- Tax filing, e-file, return preparation, or legal-tax-advice functionality
- Complex gain/loss netting
- Multi-state taxation
- Federal-state tax integration
- Interactive sliver visualization
- Broader scenario catalogs beyond the predefined demonstration scenario

Do not silently invent deduction allocation, income characterization, state-tax treatment, IRMAA assumptions, or other tax-treatment rules.

## Design Decisions

- The project is an analytical and explanatory model, not a filing product.
- The federal core must remain deterministic, side-effect free, typed, traceable, and test-led.
- Each major calculation engine must retain enough structured output to explain its result.
- Federal tax logic must remain separate from presentation logic.
- State tax remains separate from federal tax and must have its own display adapter or visual zone rather than being folded into federal tax results.
- IRMAA remains a separate future economic Medicare-surcharge overlay, not federal income tax.
- Taxable Social Security explanation and NIIT notices or overlays are semantic presentation elements of the baseline federal tax-stack view model.
- LTCG and qualified dividends remain one combined preferential-income input for this prototype.
- Chart view models remain immutable, deterministic, and independent of any specific chart library.
- Future marginal and sliver analyses must recompute the full applicable federal pipeline for each altered scenario. They must not shortcut a single tax module.
- Every future phase must be separately approved, narrow, deterministic, auditable, and test-led.
- Work proceeds in small, testable phases with no broad redesigns.

## Next-Phase Planning

No future phase is approved by this document. The following roadmap is directional and non-binding:

1. Baseline tax-stack view model, including taxable Social Security explanation and NIIT notices or overlays as required semantic elements
2. Baseline tax-stack renderer
3. Separate state-tax display adapter and visual zone
4. Separate IRMAA economic-overlay module
5. Sliver and marginal chart view models
6. Sliver renderer
7. Controlled scenario catalog
8. Future user-input boundary and interactive application shell

Each roadmap item requires its own written approval and focused handoff before implementation.

Before selecting or implementing a future phase:

1. Read the current source code, tests, this document, and the newest phase handoff.
2. Identify one narrow, testable objective.
3. Write or update the phase proposal before coding.
4. Verify real callable signatures, result types, and existing tests.
5. Preserve the federal, state-tax, presentation, and IRMAA boundaries.
6. Do not alter completed tax formulas or engine interfaces without an explicit approved scope change.

## Long-Term Product Vision

The eventual product may accept user-entered scenario variables such as age, filing status, ordinary income, combined LTCG/QD income, Social Security income, deduction selection or amount, nontaxable income, state assumptions, and later Medicare-related assumptions.

The baseline tax-stack view model should semantically represent:

- The baseline income-and-tax stack
- A deduction or 0% shielding zone
- Ordinary marginal-rate layers
- LTCG/QD rate layers stacked above ordinary income
- An explanation of taxable Social Security
- NIIT notices or overlays

The baseline renderer should present those federal semantic elements visually. Taxable Social Security explanation and NIIT notices or overlays are part of the baseline tax-stack view-model contract; they do not require separate modules before baseline rendering.

State tax should be represented through a separate display adapter and separate state-tax visual zone. It should not be folded into the federal tax stack.

IRMAA should be added later as a separate economic-overlay module. It should be shown as a Medicare-surcharge effect, never as federal income tax.

The product may also provide marginal or sliver analysis for:

- Additional ordinary income
- Additional LTCG/QD income
- Roth conversions
- Deferral decisions

Federal tax logic, state tax, presentation, and IRMAA must remain distinct architectural concerns. Federal tax calculations should feed presentation models; state tax should use a separate tax and display boundary; and IRMAA should be represented as an economic Medicare-surcharge overlay rather than federal income tax.

This vision is directional only. It does not approve implementation of user inputs, interactive UI, state integration, IRMAA calculations, or any other future capability.