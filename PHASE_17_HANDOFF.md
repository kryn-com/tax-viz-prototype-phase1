# Phase 17 Handoff - Federal Sliver Component Breakdown

## Status

Phase 17 is complete. The federal sliver presentation layer now exposes baseline and altered component-level federal tax values and renders their deterministic deltas.

## Objective

Add a display-only component breakdown for existing sliver-analysis results. Preserve the Phase 16 display surface while making ordinary tax, LTCG/QD tax, NIIT, and total federal tax available for baseline and altered results.

## API Decision

An adjacent immutable `FederalSliverTaxBreakdown` dataclass was added rather than expanding the existing display model with four additional scalar fields. This keeps component values grouped by baseline or altered state and matches the repository's existing frozen presentation dataclass pattern.

`FederalSliverDisplayModel` retains every Phase 16 field and adds optional `baseline_breakdown` and `altered_breakdown` fields defaulting to `None`. The defaults preserve compatibility for existing positional and keyword construction. Models built by the Phase 16 builder functions populate both breakdowns; the summary renders the new component section when both are present.

## Public Dataclasses

```python
@dataclass(frozen=True)
class FederalSliverTaxBreakdown:
    ordinary_tax: float
    ltcg_qd_tax: float
    niit_tax: float
    total_federal_tax: float
```

```python
@dataclass(frozen=True)
class FederalSliverDisplayModel:
    ...
    baseline_breakdown: Optional[FederalSliverTaxBreakdown] = None
    altered_breakdown: Optional[FederalSliverTaxBreakdown] = None
```

Existing public builder and renderer signatures remain unchanged:

```python
build_federal_sliver_display_model(result: FederalSliverResult) -> FederalSliverDisplayModel
build_federal_ltcg_qd_sliver_display_model(result: FederalLTCGQDSLiverResult) -> FederalSliverDisplayModel
build_federal_combined_sliver_display_model(result: FederalCombinedSliverResult) -> FederalSliverDisplayModel
render_federal_sliver_summary(model: FederalSliverDisplayModel) -> str
```

## Files Changed

- `models/sliver_display.py`
  - Added `FederalSliverTaxBreakdown`.
  - Added backward-compatible optional baseline and altered breakdown fields.
- `presentation/sliver_display.py`
  - Maps existing `FederalTaxResult` component totals into both breakdowns.
- `presentation/sliver_summary.py`
  - Renders fixed-order ordinary, LTCG/QD, and NIIT baseline, altered, and delta values.
- `tests/test_sliver_summary.py`
  - Added component mapping, component delta, rendering, zero-value, and supported-variant coverage.
- `PHASE_17_HANDOFF.md`
  - Documents the completed scope and validation.

## Test Coverage

- Existing summary fields remain present.
- Baseline and altered component values map from existing federal result contracts.
- Ordinary, LTCG/QD, and combined sliver builders remain supported.
- Ordinary, LTCG/QD, and NIIT component deltas render as altered minus baseline.
- Zero-valued components and deltas render as `$0.00`.
- Repeated rendering remains deterministic.

## Validation

```text
python -m pytest -q tests/test_sliver_summary.py
6 passed in 0.15s

python -m pytest -q
104 passed in 0.19s
```

## Preserved Boundaries

- No tax calculation logic changed.
- No sliver-analysis engine behavior changed.
- No federal orchestrator behavior changed.
- No federal/state integration was added.
- No CLI or demo entry point was added.
- No API surface, serialization/export format, charts, or UI was added.
- Tax logic remains separate from presentation logic.
- Existing Phase 16 builder and renderer call signatures remain unchanged.

## Deferred Scope

CLI/demo entry points, serialization/export, chart-ready view models, UI integration, federal/state integration, richer cross-result reporting, and tax-engine changes remain deferred to separately approved phases.
