import json

from scripts.manual_scenario_harness import run_manual_harness


def test_manual_harness_happy_path_has_distinct_sections():
    result = run_manual_harness("scripts/sample_inputs/phase36_demo.json")

    assert set(result.keys()) == {"scenario", "federal", "north_carolina", "niit", "projected_irmaa_2028"}
    assert result["scenario"]["filing_status"] == "single"

    federal = result["federal"]["result"]
    north_carolina = result["north_carolina"]["result"]
    niit = result["niit"]["result"]
    irmaa = result["projected_irmaa_2028"]

    assert federal["scenario"]["filing_status"] == "single"
    assert north_carolina["federal_result"]["scenario"]["filing_status"] == "single"
    assert north_carolina["nc_state_result"]["state_code"] == "NC"
    assert niit == federal["niit_output"]
    assert irmaa["supported"] is True
    assert irmaa["result"]["filing_status"] == "single"
    assert irmaa["result"]["premium_year"] == 2028


def test_manual_harness_unsupported_irmaa_remains_explicit_and_separate(tmp_path):
    scenario_path = tmp_path / "unsupported_irmaa.json"
    scenario_path.write_text(
        json.dumps(
            {
                "scenario": {
                    "tax_year": 2026,
                    "state_code": "NC",
                    "filing_status": "head_of_household",
                    "taxpayer_age": 45,
                    "ordinary_income": 120000.0,
                    "ltcg_qd_income": 20000.0,
                    "social_security_income": 15000.0,
                    "nontaxable_income": 0.0,
                    "deduction_mode": "standard",
                    "deduction_amount": 0.0,
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = run_manual_harness(scenario_path)

    assert result["projected_irmaa_2028"]["supported"] is False
    assert result["projected_irmaa_2028"]["result"] is None
    assert "single and married_filing_jointly" in result["projected_irmaa_2028"]["message"]
    assert "federal" in result
    assert "north_carolina" in result
    assert "niit" in result


def test_manual_harness_sample_input_keeps_required_sections():
    result = run_manual_harness("scripts/sample_inputs/phase36_demo.json")

    assert set(result.keys()) == {"scenario", "federal", "north_carolina", "niit", "projected_irmaa_2028"}


def test_manual_harness_niit_is_exposed_as_its_own_output_section():
    result = run_manual_harness("scripts/sample_inputs/phase36_demo.json")

    niit = result["niit"]["result"]
    federal_niit = result["federal"]["result"]["niit_output"]

    assert niit == federal_niit
    assert "niit_tax" in federal_niit
    assert "tax_base" in niit
    assert set(result.keys()) == {"scenario", "federal", "north_carolina", "niit", "projected_irmaa_2028"}
