# Phase 24 Handoff - Federal Tax Stack Auditability Refinement

## Objective

Refine the federal tax-stack presentation so visible layers and scenario context are easy to audit without changing tax computation behavior.

## Files Changed

- `presentation/tax_stack_data.py`
  - Filters non-applicable zero-value layers and sorts visible ordinary and preferential layers by ascending rate.
- `presentation/tax_stack_svg.py`
  - Adds a deterministic scenario-input summary, uses audit-safe shielding wording, formats integral rates as whole percentages, places ascending layers bottom-up, and subordinates supporting panels.
- `tests/test_tax_stack_data.py`
  - Covers filtering and ascending presentation order.
- `tests/test_tax_stack_svg.py`
  - Covers scenario context, rate formatting, bottom-up placement, omitted preferential rates, and shielding wording.

## Preserved Boundaries

- Tax computation logic, formulas, thresholds, engines, orchestrator behavior, and result-object semantics are unchanged.
- The existing federal tax-stack view-model dataclass and SVG renderer API remain unchanged.
- No state-tax, IRMAA, UI, CLI, serialization, or interactive behavior was added.

## Validation

```text
python -m pytest -q tests/test_tax_stack_data.py tests/test_tax_stack_svg.py
17 passed

python -m pytest -q
147 passed
```