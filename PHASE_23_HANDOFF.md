# Phase 23 Handoff - Baseline Tax Stack SVG Renderer

## Objective

Add a federal-only, deterministic standalone SVG renderer for the Phase 22 baseline tax-stack view model. The renderer presents deduction shielding, ordinary marginal layers, LTCG/QD layers above ordinary income, Social Security explanation data, NIIT notice data, and federal totals.

## Files Changed

- `presentation/tax_stack_svg.py`
  - Added `render_federal_tax_stack_svg`.
- `tests/test_tax_stack_svg.py`
  - Added focused renderer coverage for structure, layout labels, ordering, formatting, escaping, zero and empty values, determinism, and immutability.
- `PHASE_23_HANDOFF.md`
  - Documents this phase.

## Public API

```python
def render_federal_tax_stack_svg(
    view_model: FederalTaxStackViewModel,
) -> str
```

The function returns a complete standalone SVG with fixed dimensions, embedded styles, no external assets, and no chart-library dependency.

## Validation

```text
python -m pytest -q tests/test_tax_stack_svg.py
7 passed

python -m pytest -q
146 passed
```

## Preserved Boundaries

- Federal-only renderer and focused tests only.
- No tax formulas, engines, orchestrator behavior, result contracts, or view-model/builder behavior changed.
- No existing display/chart models or renderer contracts changed.
- No state-tax display, federal-state integration, or IRMAA work added.
- No UI, CLI, serialization, chart-library, scenario-catalog, or interactive work added.

## Presentation Limitation

The renderer is conceptual and presentation-oriented. Its fixed-height stack rows communicate category and ordering without claiming pixel-perfect tax allocation. Deduction shielding is shown as a conceptual zone because the current view model does not define allocation across specific income categories. This phase does not add a tax-allocation engine or recalculate tax.

## Deferred Scope

State-tax display adapters, IRMAA economic overlays, user inputs, interactive application behavior, CLI and serialization, scenario catalogs, and sliver or marginal visualization remain deferred to separately approved phases.