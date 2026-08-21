# Tax Visualization Project - Federal Tax Prototype

This is the foundational backend repository for a future comprehensive tax-visualization application. The current focus is strictly on domain modeling, validation, and core federal tax computations for the 2026 tax year.

## Architecture

- **Models**: Pydantic models handling input schema definition and strict data validation (`models/inputs.py`). Dataclasses are used for robust output structuring (`models/outputs.py`).
- **Rules**: Separated pure data representing tax policy configurations (`rules/federal/year_2026.py`), allowing logic to remain generic and uncoupled from tax law fluctuations.
- **Engines**: Pure Python deterministic calculation engines that process scenarios into structural payloads (Ordinary Income, Social Security Taxability, LTCG/Qualified Dividends, and Net Investment Income Tax).
- **Interfaces**: Structural stubs designating where Phase 3+ systems (for example, State Tax and IRMAA) can integrate into the calculation pipeline.

## Excluded from Current Phase

This phase intentionally omits:

- UI / Frontend
- State tax logic
- IRMAA (Medicare B/D surcharges)
- Married Filing Separately (MFS) filing status, permanently out of scope across all engines
- Perturbation and charting analysis

## Setup & Testing

**Requirements:** Python 3.10+

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the test suite:

```bash
pytest tests/
```

The suite includes boundary, validation, and calculation tests across all implemented engines.