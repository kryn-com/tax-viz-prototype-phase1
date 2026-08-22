# Phase 25 Handoff - Deterministic Self-Service Tax Scenario Runner

## Objective

Provide a local, deterministic runner for curated federal tax scenario fixtures. Each case is loaded from JSON, routed through the existing federal pipeline and tax-stack presentation boundary, and written as machine-readable and SVG review artifacts.

## Files Changed

- `scripts/scenario_runner.py`
  - Loads and validates versioned JSON fixtures through `TaxScenarioInput`.
  - Discovers cases in stable filename order.
  - Runs one case or all cases through the existing orchestration and tax-stack rendering pipeline.
  - Writes `result.json` and `tax_stack.svg` under a per-scenario output directory.
  - Compares optional expected numeric values with an absolute tolerance of `$0.01`.
- `scripts/__init__.py`
- `scenarios/cases/single-baseline.json`
- `scenarios/cases/high-income-niit.json`
- `scenarios/cases/zero-income.json`
- `scenarios/defects.json`
  - Separate defect registry; it is not a curated case.
- `artifacts/.gitkeep`
- `tests/test_scenario_runner.py`
- `.gitignore`

## Usage

```text
python -m scripts.scenario_runner --scenario scenarios/cases/single-baseline.json
python -m scripts.scenario_runner --all
```

The default output directory is `artifacts/phase25`. Override it with `--output-dir`; override case discovery with `--scenario-dir`.

## Fixture Contract

Each case is a JSON object with `schema_version: 1`, a unique `id`, an optional description and tags, a `scenario` object using native `TaxScenarioInput` field and enum values, and an optional `expected` object. Expected keys are limited to the documented scalar federal result fields. The separate `scenarios/defects.json` registry is intentionally excluded from case discovery by the `scenarios/cases` directory boundary.

## Preserved Boundaries

- Tax computation logic, formulas, thresholds, engines, orchestrator signatures, and result semantics are unchanged.
- Existing tax-stack view-model and SVG renderer APIs are unchanged.
- No state tax, IRMAA, GUI, web API, database, or interactive behavior was added.

## Validation

```text
python -m pytest -q tests/test_scenario_runner.py
python -m pytest -q
```
