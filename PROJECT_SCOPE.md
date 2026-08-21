Read the imported repository before proposing any changes.

This repository is a Python 2026 federal-income-tax prototype that will eventually power an explanatory tax-visualization application. Your task in this step is documentation only.

Create or replace one Markdown document at the repository root named:

PROJECT_SCOPE.md

Do not modify Python source files, tests, rule tables, package configuration, README, or handoff files. Do not implement any code. Do not invent any tax rules or thresholds.

The purpose of PROJECT_SCOPE.md is to be the durable source of truth for future Gemini sessions and for the human project owner. It must reconcile the long-term product vision with the actual current implementation state.

Use these current facts as authoritative:

CURRENTLY COMPLETED FOR THE 2026 FEDERAL PROTOTYPE
- Strict typed validation through Pydantic using TaxScenarioInput.
- A versionable federal rule structure centered on rules.federal.year_2026.
- A federal ordinary-income tax engine that produces taxable ordinary income and a detailed bracket trace.
- A Social Security taxability engine using provisional-income mechanics and statutory limits.
- An LTCG/qualified-dividend engine that stacks preferential income above ordinary income and traces slices through the 0%, 15%, and 20% rate bands.
- A standalone NIIT engine that calculates the NIIT base and 3.8% liability from MAGI threshold and net-investment-income inputs.
- Tests exist, but the repository remains a prototype and outputs must remain auditable and test-led.

CURRENT PHASE EXCLUSIONS
- Married Filing Separately is permanently out of scope. Engines must reject it clearly rather than calculate it.
- State tax calculations are not part of the current federal prototype.
- IRMAA is not part of the current federal prototype.
- UI, API, web framework, Streamlit, FastAPI, Plotly, and chart construction are not part of the current phase.
- No tax filing, e-file, credits, AMT, payroll tax, self-employment tax, business-entity taxation, multi-state taxation, or complex netting/return-preparation logic.

IMPORTANT CURRENT DESIGN DECISIONS
- The project is an analytical and explanatory model, not a tax filing product.
- The federal core must be deterministic, side-effect free, and traceable.
- Each major engine must expose enough structured information to explain its result.
- Tax logic must remain separate from presentation logic.
- Threshold values for Social Security, preferential-income bands, and NIIT are intentionally kept inside their relevant engines during this prototype to prevent scope creep. Note this as a deliberate prototype decision and identify migration to centralized year-rule tables as a later maintenance improvement, not current work.
- LTCG and qualified dividends remain a single combined preferential-income input for this prototype.
- The project will proceed in small, testable phases; no broad redesigns.

THE NEXT IMPLEMENTATION PHASE
The next phase is a Federal Pipeline Orchestrator only.

Its responsibility will be to accept one validated TaxScenarioInput, call the already-completed federal engines in the correct dependency order, assemble a unified and typed federal result, calculate transparent aggregate federal totals, and preserve the output traces from each component.

It is not permitted to:
- change tax formulas or threshold values;
- rewrite completed engines;
- add state tax, IRMAA, perturbations, charts, UI, APIs, or framework dependencies;
- add new user inputs unless absolutely required to reconcile an existing engine interface;
- silently invent deduction allocation or tax-treatment rules if the existing code does not already define them.

LONG-TERM PRODUCT VISION
The eventual product will accept a compact scenario including age, filing status, ordinary income, combined LTCG/QD income, Social Security income, deduction choice/amount, nontaxable income, and later state/Medicare assumptions. It will display:
- a main explanatory income-and-tax stack;
- deduction shielding;
- taxable Social Security;
- ordinary-income bracket slices;
- LTCG/QD preferential-rate slices;
- future state and threshold markers;
- three future marginal “sliver” analyses: +$100 ordinary income, +$100 LTCG/QD income, and +$100 of both.

Future sliver analysis must recompute the full federal result for each scenario rather than shortcut individual tax modules. State tax and IRMAA will eventually be separate modules; IRMAA must always be represented as an economic Medicare-surcharge overlay, never as income tax.
