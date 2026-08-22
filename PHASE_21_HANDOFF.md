# Phase 21 Handoff - Predefined Federal SVG Scenario Demo

## Objective

Provide one deterministic, non-interactive example that runs a predefined federal tax scenario through the existing federal pipeline and writes a standalone SVG chart.

## Files Changed

- `examples/federal_svg_demo.py`
- `tests/test_federal_svg_demo.py`
- `PHASE_21_HANDOFF.md`

## Public and Demo Surface

```python
def render_representative_federal_svg() -> str
```

The example module also provides a fresh fixed-scenario factory and a narrow `main()` that writes `federal_tax_chart.svg` as UTF-8.

## Pipeline

The demo calls the existing contracts in order:

1. `TaxScenarioInput`
2. `orchestrate_federal_tax`
3. `build_federal_display_model`
4. `build_federal_chart_view_model`
5. `render_federal_chart_svg`

The fixed scenario is a 2026 North Carolina single filer with ordinary income, LTCG/QD income, and Social Security income, using the standard deduction mode.

## Validation

```text
python -m pytest -q tests/test_federal_svg_demo.py
6 passed

python -m pytest -q
129 passed
```

The focused Phase 21 suite and the full test suite both pass.

## Preserved Boundaries

- No tax formulas, engines, or orchestrator behavior changed.
- No display-model, chart-view-model, or SVG renderer contracts changed.
- No state-tax integration changed.
- No UI framework, chart library, serialization layer, or general-purpose CLI added.
- No interactive inputs, multiple scenarios, or sliver demo support added.

## Deferred Scope

Interactive inputs, UI integration, general-purpose CLI behavior, chart libraries, broader export architecture, multiple scenarios, and sliver visualization remain deferred.
