# Tax Visualization Project - Phase 1 Prototype

This is the foundational backend repository for a future comprehensive tax-visualization application. Phase 1 focuses strictly on domain modeling, validation, and federal ordinary-income computation for the 2026 tax year.

## Architecture

* **Models**: Pydantic models handling input schema definition and strict data validation (`models/inputs.py`). Dataclasses used for robust output structuring (`models/outputs.py`).
* **Rules**: Separated pure data representing tax policy configurations (`rules/federal/year_2026.py`), allowing logic to remain generic and uncoupled from tax law fluctuations.
* **Engines**: Pure Python deterministic calculation engines that process scenarios into bracket trace payloads.
* **Interfaces**: Empty stubs explicitly designating where Phase 2 systems (SS, LTCG, NIIT, IRMAA, States) will plug into the pipeline.

## Excluded from Phase 1

This phase intentionally omits:
* UI / Frontend
* Preferential taxation (LTCG, Social Security, NIIT)
* State tax logic
* IRMAA
* Perturbation and charting analysis

## Setup & Testing

**Requirements:**
Python 3.10+

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the test suite:
   ```bash
   pytest tests/
   ```
   The suite includes rigorous boundary, validation, and multi-bracket calculation tests.