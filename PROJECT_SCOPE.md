# Project Scope — 2026 Federal Tax Prototype

## Purpose

This repository is a deterministic, explainable Python prototype for selected 2026 federal income-tax calculations. It is an analytical and educational model intended to support a future tax-visualization application; it is not a tax-preparation, tax-filing, or e-file product.

This document is the durable source of truth for future development sessions and the project owner. Before proposing or implementing work, read the current repository, this document, and the most recent phase handoff document.

## Current Status

Phases 1 through 3 are complete and merged into the `phase-2-social-security` branch.

Phase 3 was merged through PR #1. The full test suite passed locally after the merge:

```text
33 passed in 0.11s
```

The current repository remains a prototype. Its outputs must stay deterministic, side-effect free, auditable, and test-led.

## Completed Federal Core

The current 2026 federal prototype includes:

- Strict typed scenario validation through Pydantic `TaxScenarioInput`
- A versionable federal-rule structure centered on `rules.federal.year_2026`
- A federal ordinary-income tax engine that produces taxable ordinary income, total ordinary tax, and a detailed bracket trace
- A Social Security taxability engine using provisional-income mechanics and statutory limits
- An LTCG/qualified-dividend engine that stacks combined preferential income above taxable ordinary income and traces the 0%, 15%, and 20% rate-band amounts
- A standalone NIIT engine that calculates the NIIT base and 3.8% liability from MAGI and net-investment-income inputs
- A Federal Pipeline Orchestrator that runs the completed engines in dependency order and returns a unified `FederalTaxResult`
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

## Current Constraints

The following are deliberately out of scope for the current federal prototype:

- Married Filing Separately calculations; engines must reject MFS clearly rather than calculate it
- State income-tax calculations
- IRMAA calculations
- Tax credits
- Alternative Minimum Tax
- Payroll tax, self-employment tax, and business-entity taxation
- Tax filing, e-file, return preparation, or legal-tax-advice functionality
- Complex gain/loss netting
- Multi-state taxation
- UI, API, web framework, Streamlit, FastAPI, Plotly, charts, or presentation-layer implementation

Do not add user inputs unless they are required to reconcile an already-existing engine interface. Do not silently invent deduction allocation, income characterization, or tax-treatment rules.

## Design Decisions

- The project is an analytical and explanatory model, not a filing product.
- The federal core must remain deterministic, side-effect free, typed, traceable, and test-led.
- Each major calculation engine must retain enough structured output to explain its result.
- Tax logic must remain separate from future presentation logic.
- LTCG and qualified dividends remain one combined preferential-income input for this prototype.
- Social Security, preferential-income, and NIIT threshold values currently remain in their respective engines to avoid prototype scope creep.
- Centralizing thresholds into year-rule tables is a future maintenance improvement, not current work.
- Work proceeds in small, testable phases with no broad redesigns.

## Next-Phase Planning

No Phase 4 implementation scope has been approved yet.

Before selecting or implementing a next phase:

1. Read the current source code, tests, this document, and `PHASE_3_HANDOFF.md`.
2. Identify one narrow, testable objective.
3. Write or update the phase proposal before coding.
4. Verify real callable signatures, result types, and existing tests before proposing adapters.
5. Do not alter completed tax formulas or engine interfaces without an explicit approved scope change.

Potential future capabilities may include fuller deduction modeling, centralized federal year-rule tables, additional trace/reconciliation support, a carefully isolated state-tax module, IRMAA as a separate economic overlay, or a presentation layer. These are possibilities only, not approved implementation instructions.

## Long-Term Product Vision

The eventual product may accept a compact scenario containing age, filing status, ordinary income, combined LTCG/QD income, Social Security income, deduction selection or amount, nontaxable income, and later state or Medicare assumptions.

A future presentation layer may explain:

- Main income-and-tax stack
- Deduction shielding
- Taxable Social Security
- Ordinary-income bracket slices
- LTCG/QD preferential-rate slices
- Future state-tax and threshold markers
- Marginal “sliver” analyses for incremental ordinary income, LTCG/QD income, and both combined

Future sliver analysis must recompute the full federal pipeline for each altered scenario. It must not shortcut a single tax module.

State tax and IRMAA must remain separate future modules. IRMAA must always be represented as an economic Medicare-surcharge overlay, never as federal income tax.