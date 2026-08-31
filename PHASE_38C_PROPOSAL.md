# Phase 38C Proposal - Provisional Federal Tax-Table Reproduction for Validation

## Objective

Add a narrow, deterministic federal tax-table reproduction path for validation scenarios with taxable income below 100,000 so the manual scenario runner can avoid false-positive discrepancies caused by comparing exact rate-schedule calculations against IRS-style printed-tax-table results.

## Why this phase exists

Phase 38B confirmed that the current runner and audit workflow can expose expected-vs-actual differences that are not true formula defects. For federal ordinary-income tax below the printed-table cutoff, the current analytical engine produces exact calculation results, while spreadsheet or manual validation may expect IRS printed-tax-table style results. Before sliver analysis proceeds, the validation path should be able to reproduce the project’s provisional printed-tax-table method so known table-versus-exact differences do not create noise.

## In scope

- Add a separate federal printed-tax-table reproduction helper or mode for supported filing statuses.
- Apply it only to taxable income below 100,000.
- Use the existing project provisional policy:
  1. map taxable income to the applicable tax-table interval,
  2. choose the interval midpoint,
  3. apply the official 2026 statutory ordinary-income rate schedule for the supported filing status,
  4. round the resulting tax to the nearest whole dollar using half-up rounding.
- Keep the exact-calculation planning path available and unchanged unless the validation runner explicitly requests printed-tax-table reproduction.
- Add focused tests for interval mapping, midpoint selection, rounding, and the 100,000 boundary.
- Update scenario-runner comparison flow as needed so below-100,000 validation rows can compare against the printed-tax-table reproduction result without changing broader domain boundaries.

## Out of scope

- Sliver analysis.
- UI or Streamlit work.
- Broad federal orchestrator redesign.
- NC formula changes.
- NIIT or projected IRMAA changes.
- Any claim that this reproduces the unpublished official 2026 IRS printed table exactly.
- Any expansion beyond the supported filing statuses already approved in the federal prototype.

## Required boundaries

1. Preserve the existing exact-calculation federal planning path.
2. Preserve separate federal, NC planning, NIIT, and projected IRMAA outputs.
3. Do not merge totals into a new combined contract.
4. Keep the implementation deterministic, auditable, and test-led.
5. Clearly label the new method as a project provisional validation policy pending official 2026 IRS table publication.

## Acceptance criteria

- Focused tests cover:
  - below-5, 5-to-less-than-15, 15-to-less-than-25, 25-dollar interval, and 50-dollar interval midpoint behavior;
  - half-up whole-dollar rounding behavior;
  - exact boundary handling at 100,000.
- Scenario-runner tests show below-100,000 validation cases can use printed-tax-table reproduction without false-positive discrepancies caused solely by table-versus-exact methodology.
- Full suite passes.
- Documentation is updated to describe the provisional status and later reconciliation requirement against the official 2026 IRS printed table.