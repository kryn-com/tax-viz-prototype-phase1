import json
from pathlib import Path
from xml.etree import ElementTree

import pytest

from scripts.scenario_runner import (
    EXPECTED_TOLERANCE,
    discover_scenario_paths,
    load_scenario_fixture,
    run_all_scenarios,
    run_scenario,
)
from scripts import scenario_runner


SCENARIO = {
    "tax_year": 2026,
    "state_code": "NC",
    "filing_status": "single",
    "ordinary_income": 60000.0,
    "ltcg_qd_income": 20000.0,
    "social_security_income": 30000.0,
    "nontaxable_income": 0.0,
    "deduction_mode": "standard",
    "deduction_amount": 0.0,
}


def write_fixture(directory: Path, name: str, **overrides) -> Path:
    payload = {
        "schema_version": 1,
        "id": name,
        "description": "Test fixture",
        "scenario": {**SCENARIO, **overrides.pop("scenario", {})},
        **overrides,
    }
    path = directory / f"{name}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_load_scenario_fixture_validates_native_tax_input():
    path = write_fixture(Path(__file__).parent, "unused")
    try:
        fixture = load_scenario_fixture(path)
    finally:
        path.unlink()

    assert fixture["id"] == "unused"
    assert fixture["scenario"].filing_status.value == "single"
    assert fixture["scenario"].ordinary_income == 60000.0


def test_load_scenario_fixture_rejects_invalid_tax_input(tmp_path):
    path = write_fixture(tmp_path, "invalid", scenario={"tax_year": 2025})

    with pytest.raises(ValueError, match="Invalid tax scenario"):
        load_scenario_fixture(path)


def test_discover_scenario_paths_is_sorted_and_directory_scoped(tmp_path):
    write_fixture(tmp_path, "z-case")
    write_fixture(tmp_path, "a-case")
    (tmp_path / "defects.json").write_text("{}", encoding="utf-8")

    assert [path.name for path in discover_scenario_paths(tmp_path)] == [
        "a-case.json",
        "defects.json",
        "z-case.json",
    ]


def test_run_scenario_writes_deterministic_json_and_svg_artifacts(tmp_path):
    fixture_path = write_fixture(tmp_path, "artifact-case")
    first_output = tmp_path / "first"
    second_output = tmp_path / "second"

    first = run_scenario(fixture_path, first_output)
    run_scenario(fixture_path, second_output)

    first_dir = first_output / "artifact-case"
    second_dir = second_output / "artifact-case"
    assert first["status"] == "passed"
    assert (first_dir / "result.json").exists()
    assert (first_dir / "tax_stack.svg").exists()
    assert json.loads((first_dir / "result.json").read_text(encoding="utf-8"))["scenario_id"] == "artifact-case"
    assert ElementTree.fromstring((first_dir / "tax_stack.svg").read_text(encoding="utf-8")).tag.endswith("svg")
    assert (first_dir / "result.json").read_bytes() == (second_dir / "result.json").read_bytes()
    assert (first_dir / "tax_stack.svg").read_bytes() == (second_dir / "tax_stack.svg").read_bytes()


def test_run_scenario_compares_optional_expected_values_with_tolerance(tmp_path):
    path = write_fixture(
        tmp_path,
        "expected-case",
        expected={"total_federal_tax": 12980.0 + EXPECTED_TOLERANCE / 2},
    )

    summary = run_scenario(path, tmp_path / "artifacts")

    assert summary["status"] == "passed"
    assert summary["expected_comparison"]["passed"] is True
    assert summary["expected_comparison"]["tolerance"] == EXPECTED_TOLERANCE


def test_run_scenario_reports_expected_value_mismatch(tmp_path):
    path = write_fixture(
        tmp_path,
        "mismatch-case",
        expected={"total_federal_tax": 0.0},
    )

    summary = run_scenario(path, tmp_path / "artifacts")

    assert summary["status"] == "failed"
    assert summary["expected_comparison"]["fields"]["total_federal_tax"]["passed"] is False


def test_main_prints_absolute_artifact_paths_and_svg_url(tmp_path, capsys, monkeypatch):
    fixture_path = write_fixture(tmp_path, "link-case")
    output_dir = tmp_path / "artifacts"
    monkeypatch.setattr(
        "sys.argv",
        [
            "scenario_runner",
            "--scenario",
            str(fixture_path),
            "--output-dir",
            str(output_dir),
        ],
    )

    assert scenario_runner.main() == 0

    output = capsys.readouterr().out
    svg_path = (output_dir / "link-case" / "tax_stack.svg").resolve()
    assert str(svg_path) in output
    assert svg_path.as_uri() in output

def test_run_all_repository_scenarios_pass(tmp_path):
    scenario_dir = Path("scenarios/cases")
    summaries = run_all_scenarios(scenario_dir, tmp_path / "artifacts")

    scenario_ids = [summary["scenario_id"] for summary in summaries]

    assert scenario_ids == [
        "high-income-niit",
        "hoh-060k-014k-ltcg-030k-ss-standard",
        "hoh-395k-224500-ltcg-050k-ss-standard",
        "hoh-ordinary-only",
        "mf-joint-ordinary-only",
        "mfj-040k-005k-ltcg-standard",
        "mfj-099k-044k-ltcg-030k-ss-explicit-74k",
        "mfj-129k-046k-ss-standard",
        "mfj-201k-055k-ltcg-075k-ss-standard",
        "single-020k-003k-ltcg-standard",
        "single-050k-011k-ltcg-015k-ss-standard",
        "single-190k-080k-ltcg-020k-ss-explicit-30k",
        "single-800k-200k-ltcg-015k-ss-explicit-80k",
        "single-baseline",
        "zero-income",
    ]
    assert all(summary["status"] == "passed" for summary in summaries)