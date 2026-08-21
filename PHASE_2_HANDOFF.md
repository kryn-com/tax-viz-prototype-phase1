# Phase 2 Handoff Document

## Completed Engines & Features

- **Strict typed input validation**: via Pydantic (`TaxScenarioInput`). Automatically rejects invalid states such as negative deductions and unsupported years.
- **Tax bracket framework**: A versionable rule structure (`rules.federal.year_2026`) that cleanly segregates tax policy data from engine logic.
- **Ordinary income tax engine**: Determines `taxable_ordinary_income` and generates a precise `bracket_trace` showing the exact slice of income taxed per bracket.
- **Social Security taxability engine**: Computes taxable benefits using provisional income mechanics and statutory limits.
- **LTCG and qualified dividends engine**: Stacks preferential income on top of ordinary income to calculate slices running through the 0%, 15%, and 20% thresholds.
- **Net Investment Income Tax (NIIT) engine**: Computes the NIIT tax base and 3.8% tax liability based on MAGI thresholds and net investment income.

## Scope Exclusions

- **Married Filing Separately (MFS)**: Permanently out of scope across all engines due to complex edge cases.
- **State tax logic**: Out of scope for the current federal prototype phase.
- **IRMAA cliffs**: Out of scope for the current phase.
- **UI / Frontend**: Out of scope.

## Recommended Next Step

- **Pipeline orchestrator**: Create a top-level runner to sequence data flow between completed engines and assemble a unified federal tax summary.

## Future Expansion

- State tax plugin abstraction remains a future-phase item.
- IRMAA surcharge modules remain a future-phase item.

## Major Design Choices

- **Standalone calculation engines**: Engines operate cleanly on standard inputs. An orchestration manager can assemble individual outputs into a unified tax summary.
- **Hardcoded thresholds**: To prevent scope creep, threshold parameters for NIIT, Social Security, and preferential tax rates are maintained within their respective engine implementations.