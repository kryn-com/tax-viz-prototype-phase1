from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from engines.federal_orchestrator import orchestrate_federal_tax
from models.inputs import TaxScenarioInput
from planning.nc_coordinator import orchestrate_nc_planning
from rules.irmaa_projected_2028 import build_projected_2028_overlay_result


def _to_serializable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "model_dump"):
        return _to_serializable(value.model_dump(mode="json"))
    if is_dataclass(value):
        return {key: _to_serializable(val) for key, val in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): _to_serializable(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_serializable(item) for item in value]
    return str(value)


def load_scenario_file(path: str | Path) -> TaxScenarioInput:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or "scenario" not in payload:
        raise ValueError("Scenario JSON must contain a top-level 'scenario' object.")
    scenario = TaxScenarioInput(**payload["scenario"])
    return scenario


def build_projected_irmaa_section(federal_result: Any, scenario: TaxScenarioInput) -> dict[str, Any]:
    filing_status = scenario.filing_status.value
    if filing_status not in {"single", "married_filing_jointly"}:
        return {
            "supported": False,
            "filing_status": filing_status,
            "result": None,
            "message": "Projected 2028 IRMAA planning mode only supports single and married_filing_jointly.",
        }

    result = build_projected_2028_overlay_result(
        filing_status=filing_status,
        magi=federal_result.magi,
        magi_source="federal_result.magi",
    )
    return {
        "supported": True,
        "result": _to_serializable(result),
    }


def run_manual_harness(scenario_path: str | Path) -> dict[str, Any]:
    scenario = load_scenario_file(scenario_path)
    federal_result = orchestrate_federal_tax(scenario)
    north_carolina_result = orchestrate_nc_planning(scenario)

    output = {
        "scenario": _to_serializable(scenario.model_dump(mode="json")),
        "federal": {"result": _to_serializable(federal_result)},
        "north_carolina": {"result": _to_serializable(north_carolina_result)},
        "niit": {"result": _to_serializable(federal_result.niit_output)},
        "projected_irmaa_2028": build_projected_irmaa_section(federal_result, scenario),
    }
    return output


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manual local scenario exploration harness for the approved 2026 prototype.")
    parser.add_argument("--scenario", type=str, required=True, help="Path to one scenario JSON file.")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    output = run_manual_harness(args.scenario)
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
