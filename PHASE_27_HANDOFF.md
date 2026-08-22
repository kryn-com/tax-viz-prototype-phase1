# Phase 27 Handoff - Rule-Based Standard Deduction Resolution

## Objective

Resolve `DeductionMode.STANDARD` to the 2026 standard deduction by filing status in the federal ordinary-income calculation path.

## Files Changed

- `rules/federal/year_2026.py`
  - Added 2026 standard deduction amounts and filing-status lookup.
- `engines/deductions.py`
  - Added deduction-mode resolution while preserving supplied non-standard amounts.
- `engines/federal_ordinary.py`
  - Applies the resolved deduction and reports it through `FederalOrdinaryOutput.deduction_applied`.
- `tests/test_engines.py`
  - Added single, married-filing-jointly, and non-standard deduction coverage.
- `tests/test_scenario_runner.py`
  - Updated the expected total used by the standard-mode tolerance test.

## Rule Values

- Single: `$16,100`
- Married filing jointly: `$32,200`
- Married filing separately: `$16,100`
- Head of household: `$24,150`

## Preserved Boundaries

- Explicit and itemized modes continue using the supplied `deduction_amount`.
- Taxable ordinary income remains floored at zero.
- No presentation, SVG, runner behavior, state tax, IRMAA, AMT, credits, or payroll-tax logic changed.

## Validation

```text
python -m pytest -q tests/test_engines.py tests/test_federal_orchestrator.py tests/test_scenario_runner.py
python -m pytest -q
```
