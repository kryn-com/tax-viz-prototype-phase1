# Phase 22 Handoff - Federal Tax Stack View Model

## Objective

Add a federal-only, immutable baseline tax-stack view model and deterministic pure builder. The model represents deduction shielding, ordinary-income marginal layers, LTCG/QD rate layers, taxable Social Security explanation, and NIIT notice information without rendering or changing tax logic.

## Files Changed

- `models/tax_stack_display.py`
  - Added immutable `FederalTaxStackSocialSecurity`, `FederalTaxStackNIIT`, and `FederalTaxStackViewModel` dataclasses.
- `presentation/tax_stack_data.py`
  - Added the pure `build_federal_tax_stack_view_model` adapter.
- `tests/test_tax_stack_data.py`
  - Added focused mapping, ordering, zero-value, determinism, immutability, and source-preservation coverage.
- `PHASE_22_HANDOFF.md`
  - Documents this phase.

## Public API

```python
@dataclass(frozen=True)
class FederalTaxStackSocialSecurity:
    total_social_security: float
    taxable_social_security: float
    tax_free_social_security: float
    provisional_income: float
```

```python
@dataclass(frozen=True)
class FederalTaxStackNIIT:
    net_investment_income: float
    magi: float
    threshold_applied: float
    magi_over_threshold: float
    tax_base: float
    niit_rate: float
    niit_tax: float
```

```python
@dataclass(frozen=True)
class FederalTaxStackViewModel:
    tax_year: int
    filing_status: FilingStatus
    ordinary_income: float
    taxable_ordinary_income: float
    preferential_income: float
    deduction_shielding_amount: float
    ordinary_marginal_layers: Tuple[FederalDisplayBracketSlice, ...]
    preferential_rate_layers: Tuple[FederalDisplayRateSlice, ...]
    social_security: FederalTaxStackSocialSecurity
    niit: FederalTaxStackNIIT
    agi: float
    magi: float
    ordinary_tax: float
    ltcg_qd_tax: float
    total_federal_tax: float
```

```python
def build_federal_tax_stack_view_model(
    result: FederalTaxResult,
) -> FederalTaxStackViewModel
```

## Mapping and Behavior

- Deduction shielding maps only from `result.ordinary_output.deduction_applied`.
- Ordinary marginal layers preserve the existing ordinary bracket trace order and values.
- Preferential rate layers reuse the existing federal display-builder mapping and preserve its 0%, 15%, and 20% order, including zero-valued layers.
- Social Security fields map directly from `result.ss_output`, including provisional income.
- NIIT notice fields map directly from `result.niit_output`.
- The adapter performs no tax recalculation and does not infer deduction allocation or new tax-treatment semantics.
- The new view-model dataclasses are frozen and the source result is not mutated.

## Validation

```text
python -m pytest -q tests/test_tax_stack_data.py
10 passed in 0.11s

python -m pytest -q
139 passed in 0.25s
```

## Preserved Boundaries

- Federal-only model, builder, and test work.
- No tax formulas, engines, or orchestrator behavior changed.
- No existing `FederalDisplayModel`, `FederalChartViewModel`, or SVG renderer contracts changed.
- No state-tax display or federal-state integration added.
- No IRMAA calculation or overlay added.
- No rendering, UI, CLI, serialization, chart-library, or scenario-catalog work added.

## Deferred Scope

Baseline tax-stack rendering, state-tax display adapters, IRMAA economic overlays, user inputs, interactive application behavior, CLI and serialization, scenario catalogs, and sliver or marginal visualization remain deferred to separately approved phases.
