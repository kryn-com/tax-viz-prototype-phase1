# Phase 19 Handoff - Federal Chart-Ready Presentation View Model

## Status

Phase 19 is complete. The federal display presentation layer now exposes a deterministic, immutable, chart-library-neutral view model for federal tax components, ordinary bracket slices, and preferential-rate slices.

## Objective

Adapt the existing `FederalDisplayModel` into explicit ordered chart segments without changing tax logic, engine interfaces, orchestration, state integration, or adding a chart dependency.

## Files Changed

- `models/chart_display.py`
  - Added immutable `FederalChartSegment` and `FederalChartViewModel` dataclasses.
- `presentation/chart_data.py`
  - Added `build_federal_chart_view_model`.
- `tests/test_chart_data.py`
  - Added focused contract coverage for mapping, ordering, zero values, empty tuples, immutability, and determinism.
- `PHASE_19_HANDOFF.md`
  - Documents this phase.

## Public API

```python
@dataclass(frozen=True)
class FederalChartSegment:
    label: str
    value: float
    rate: Optional[float] = None
```

```python
@dataclass(frozen=True)
class FederalChartViewModel:
    tax_year: int
    filing_status: FilingStatus
    total_federal_tax: float
    tax_component_segments: Tuple[FederalChartSegment, ...]
    ordinary_bracket_segments: Tuple[FederalChartSegment, ...]
    preferential_rate_segments: Tuple[FederalChartSegment, ...]
```

```python
def build_federal_chart_view_model(
    model: FederalDisplayModel,
) -> FederalChartViewModel
```

## Ordering and Value Rules

- Tax components always appear as ordinary tax, LTCG/QD tax, and NIIT tax.
- Ordinary bracket segments preserve source order and use `tax_generated` as the segment value.
- Preferential-rate segments preserve source order and use `taxed_amount` as the segment value.
- Zero-valued source segments remain explicit.
- Empty ordinary and preferential source tuples remain empty tuples.

## Preserved Boundaries

- No tax formulas changed.
- No engine interfaces changed.
- No orchestrator behavior changed.
- No state-tax integration changed.
- No serialization or export format added.
- No UI, web framework, chart library, demo, CLI, or report surface added.
- No sliver chart adapter was added.

## Deferred Scope

A concrete chart renderer or visualization entry point, serialization/export, sliver chart adapters, UI integration, and broader reporting remain deferred to separately approved phases.

## Validation

```text
python -m pytest -q tests/test_chart_data.py
6 passed

python -m pytest -q
117 passed
```
