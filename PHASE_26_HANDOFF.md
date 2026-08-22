# Phase 26 Handoff - Tax-Stack Presentation Clarity and Runner Artifact Links

## Objective

Improve the clarity and auditability of the federal tax-stack SVG and make generated runner artifacts easier to open locally, without changing tax computation behavior.

## Files Changed

- `models/tax_stack_display.py`
  - Added the existing scenario's `nontaxable_income` as an additive display field.
  - Added the existing scenario's `deduction_mode` as an additive display field.
- `presentation/tax_stack_data.py`
  - Maps nontaxable income into the tax-stack view model.
- `presentation/tax_stack_svg.py`
  - Uses human-readable filing status text.
  - Uses a compact source-income tabulation that avoids double counting taxable Social Security.
  - Shows deduction type and amount, with clearer deduction-relief wording.
  - Clarifies income and Social Security wording.
  - Shows auditable income inputs, whole-dollar values, federal tax rates, bracket-style labels, per-layer LTCG/QD tax, Social Security taxable percentage, and simplified zero-NIIT output.
  - Removes repeated rate text from layer detail lines and reserves vertical space for the summary before rendering the left stack.
  - Separates the top-left area into scenario, income-summary, and federal-tax-summary blocks with stable row spacing, without changing the fixed SVG canvas or side panels.
- `scripts/scenario_runner.py`
  - Prints absolute artifact paths and a local `file:///...` URL after successful runs.
- `tests/test_tax_stack_data.py`
- `tests/test_tax_stack_svg.py`
- `tests/test_scenario_runner.py`
  - Updated presentation expectations and added coverage for applicable NIIT and artifact links.

## Preserved Boundaries

- Tax computation logic, formulas, thresholds, engines, orchestrator signatures, and result semantics are unchanged.
- No true Social Security stack layers, NIIT stack layer, GUI, web interface, or state-tax integration was added.
- The only view-model change is additive and presentation-specific.
- Source ordinary income is derived for display from the existing effective ordinary income and taxable Social Security fields; no result values are changed.
- Focused SVG coverage asserts that ordinary-income and LTCG/QD section origins remain below the summary block.
- Focused SVG coverage asserts the top-left block coordinates and single-line Social Security inclusion note.

## Validation

```text
python -m pytest -q tests/test_tax_stack_data.py tests/test_tax_stack_svg.py tests/test_scenario_runner.py
python -m pytest -q
```
