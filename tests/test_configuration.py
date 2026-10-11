"""Regression tests for the JSON rules and first-match recommendation semantics."""
import json
from pathlib import Path

from validate_config import validate

ROOT = Path(__file__).resolve().parents[1]


def first_match(config_file, answers):
    """Pure equivalent of the current engine's ordered JSON rule matching."""
    config = json.loads((ROOT / "config" / config_file).read_text(encoding="utf-8"))
    for rule in config["rules"]:
        def matches(key, expected):
            if expected is None:
                return True
            actual = answers.get(key)
            if actual is None:
                return False
            if isinstance(expected, list):
                return str(actual).casefold() in [str(x).casefold() for x in expected]
            if isinstance(expected, dict):
                number = int(actual)
                return expected.get("min", float("-inf")) <= number <= expected.get("max", float("inf"))
            return str(actual).casefold() == str(expected).casefold()
        if all(matches(k, v) for k, v in rule.items() if k != "method"):
            return rule["method"]
    return None


def test_configuration_has_no_invalid_options_or_duplicate_rules():
    errors, warnings = validate(ROOT)
    assert not errors, "\n".join(errors)
    assert not [w for w in warnings if "duplicate rule" in w], "\n".join(warnings)


def test_agile_short_iterations_recommend_scrum():
    answers = {"knowledge_of_technology": "high", "iterations": "yes",
               "predictability": "Coming 2 weeks"}
    assert first_match("Agile_Methods/agile_methods.json", answers) == "Scrum"


def test_agile_low_technology_knowledge_preserves_existing_priority():
    answers = {"knowledge_of_technology": "low", "iterations": "yes",
               "predictability": "Coming 3 months"}
    assert first_match("Agile_Methods/agile_methods.json", answers) == "Scrum"


def test_high_level_known_technology_and_requirements():
    answers = {"knowledge_of_technology": "high",
               "knowledge_of_customer_requirements": "high",
               "project_type": "SW-design", "team_size": "5"}
    assert first_match("high_level_methods.json", answers) == "classical_project_methods"


def test_no_match_returns_none():
    answers = {"knowledge_of_technology": "high", "iterations": "no",
               "predictability": "Coming year"}
    assert first_match("Agile_Methods/agile_methods.json", answers) is None


def test_every_recommendation_has_details():
    errors, _ = validate(ROOT)
    assert not errors, "\\n".join(errors)


def test_missing_details_is_an_error(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (tmp_path / "recommendation_details").mkdir()
    (config_dir / "sample.json").write_text(
        json.dumps({"parameters": [], "rules": [
            {"method": "Unspecified Method"}, {"method": "Unspecified Method"}
        ]}), encoding="utf-8"
    )
    errors, _ = validate(tmp_path)
    missing = [error for error in errors if "Missing recommendation details" in error]
    assert len(missing) == 1
