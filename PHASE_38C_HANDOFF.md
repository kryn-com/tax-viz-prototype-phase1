# Phase 38C Handoff - Provisional Federal Printed-Tax-Table Reproduction for Validation

## Status

Completed: narrow Phase 38C validation-path implementation.

Verification completed:

- pytest tests/test_engines.py tests/test_scenario_runner.py -q -> 90 passed
- pytest -q -> 288 passed

## Objective Delivered

Added and integrated a deterministic, validation-only provisional federal printed-tax-table reproduction path for taxable ordinary income below 100,000, while preserving the existing exact federal planning calculation path.

## Scope Completed

### Federal ordinary-tax helper (validation-only)

- Added a dedicated provisional reproduction helper that:
  1. maps taxable income to IRS-style table intervals,
  2. selects the interval midpoint,
  3. computes midpoint tax using the existing supported 2026 statutory rate schedule,
  4. rounds to whole dollars using half-up rounding,
  5. falls back to exact schedule calculation at and above 100,000.
- Added a method label explicitly stating provisional status pending official 2026 IRS printed-table publication.
- Kept the existing exact planning entry point unchanged as the default path.

### Scenario-runner comparison integration

- Integrated the provisional helper only into expected-vs-actual validation comparison behavior for below-100,000 taxable ordinary income.
- Kept federal planning outputs unchanged in summary payloads.
- Preserved NC planning behavior, NIIT behavior, and IRMAA boundary behavior.
- Did not introduce any combined federal + NC + NIIT + IRMAA total contract.

## Files in Phase 38C Scope

- engines/federal_ordinary.py
- scripts/scenario_runner.py
- tests/test_engines.py
- tests/test_scenario_runner.py
- tests/fixtures/phase38a_sample_bank.csv
- PHASE_38C_HANDOFF.md

## Key Boundary Confirmations

- Exact federal planning calculation remains the default and unchanged.
- Federal, NC planning, NIIT, and projected IRMAA remain separate outputs and concerns.
- No federal orchestrator redesign was introduced.
- No UI, Streamlit, sliver-analysis, or NC formula changes were introduced.

## Test Coverage Added/Validated for Phase 38C

Focused coverage confirms:

- midpoint behavior for:
  - below 5,
  - 5 to less than 15,
  - 15 to less than 25,
  - 25-dollar interval ranges,
  - 50-dollar interval ranges,
- whole-dollar half-up rounding,
- exact fallback boundary behavior at 100,000,
- below-100,000 scenario-runner comparison support for expected ordinary and expected federal total validation cases,
- preserved exact-method comparison behavior at and above 100,000,
- preserved NC/NIIT/IRMAA boundary behavior in comparison payloads.

## Provisional Policy and Future Reconciliation Requirement

This implementation is a project-controlled provisional validation policy for below-100,000 printed-tax-table reproduction pending publication of the official 2026 IRS printed tax table.

When official 2026 IRS printed tables are published, representative rows across below-3,000 and 3,000-to-less-than-100,000 ranges should be revalidated and this policy/implementation should be revised only if official published data requires it.
