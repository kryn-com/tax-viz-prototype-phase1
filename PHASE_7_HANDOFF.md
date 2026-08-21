# Phase 7 Handoff — LTCG/QD Sliver Analysis

## Status

Phase 7 is complete. This phase added LTCG/QD sliver analysis.

## Files Changed

- `engines/sliver_analysis.py`
- `models/outputs.py`
- `tests/test_sliver_analysis.py`

## Public Function

```python
analyze_ltcg_qd_sliver(
    scenario: TaxScenarioInput,
    increment: float,
) -> FederalLTCGQDSLiverResult
```

The function accepts positive absolute-dollar LTCG/QD increments only. It recomputes both baseline and altered scenarios through `orchestrate_federal_tax`, preserves the original scenario, and keeps ordinary income unchanged in the altered scenario.

It returns both full pipeline results and the total federal-tax delta.

The existing ordinary-income sliver API remains unchanged. MFS rejection continues to propagate from the existing orchestrator.

## Important Constraints Preserved

- No formulas changed.
- No thresholds changed.
- No scenario inputs changed.
- No existing engine interfaces changed.
- `FederalTaxResult` was not changed.
- Combined slivers remain out of scope.

## Validation

- `python -m pytest -q tests/test_sliver_analysis.py` — `12 passed`
- `python -m pytest -q` — `49 passed`

## Starting Point for Next Phase

Phase 8 has not been selected. Read `PROJECT_SCOPE.md` and the latest phase handoff before proposing further work. Select one narrow, testable objective before coding.
