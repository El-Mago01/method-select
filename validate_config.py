"""Static checks for JSON recommendation configurations.

Run: python validate_config.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "config"
DETAILS = ROOT / "recommendation_details"


def validate(root=ROOT):
    config_dir = root / "config"
    details_dir = root / "recommendation_details"
    files = sorted(config_dir.rglob("*.json"))
    errors, warnings = [], []
    by_name = {}
    configs = {}
    for path in files:
        by_name.setdefault(path.name.lower(), []).append(path)
        try:
            config = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        configs[path] = config
        if not isinstance(config, dict) or not isinstance(config.get("rules"), list):
            errors.append(f"{path}: expected a 'rules' list")
            continue
        params = {p.get("id"): p for p in config.get("parameters", [])
                  if isinstance(p, dict) and isinstance(p.get("id"), str)}
        seen = set()
        for index, rule in enumerate(config["rules"], 1):
            if not isinstance(rule, dict) or not isinstance(rule.get("method"), str):
                errors.append(f"{path}: rule {index} requires a method string")
                continue
            signature = json.dumps(rule, sort_keys=True)
            if signature in seen:
                warnings.append(f"{path}: duplicate rule {index}")
            seen.add(signature)
            for key, value in rule.items():
                if key == "method" or key not in params:
                    # Rules may use answers inherited from previous levels.
                    continue
                options = params[key].get("options")
                if not isinstance(options, list) or value is None or isinstance(value, dict):
                    continue
                values = value if isinstance(value, list) else [value]
                invalid = [v for v in values if not any(
                    isinstance(v, str) and isinstance(opt, str) and v.casefold() == opt.casefold()
                    for opt in options)]
                if invalid:
                    errors.append(f"{path}: rule {index}, {key}: values not offered: {invalid}")
    for name, paths in by_name.items():
        if len(paths) > 1:
            warnings.append(f"Ambiguous config filename {name}: {paths}")
    # A details file is required for every unique recommendation, including endpoints.
    # Report each missing method once rather than once per matching rule.
    recommendations = {}
    for path, config in configs.items():
        if not isinstance(config, dict):
            continue
        for rule in config.get("rules", []):
            if isinstance(rule, dict) and isinstance(rule.get("method"), str):
                recommendations.setdefault(rule["method"], path)
    for method, source in sorted(recommendations.items()):
        detail_name = "rd_" + method.replace(" ", "_").lower() + ".json"
        detail = details_dir / detail_name
        if not detail.is_file():
            errors.append(f"Missing recommendation details for {method!r} (used in {source})")
            continue
        try:
            payload = json.loads(detail.read_text(encoding="utf-8"))
            if not isinstance(payload, dict) or not isinstance(payload.get("details"), str) or not payload["details"].strip():
                errors.append(f"{detail}: missing non-empty 'details' description")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{detail}: invalid details JSON: {exc}")
    return errors, warnings


if __name__ == "__main__":
    errors, warnings = validate()
    for item in errors:
        print("ERROR:", item)
    for item in warnings:
        print("WARNING:", item)
    print(f"Validation finished: {len(errors)} error(s), {len(warnings)} warning(s).")
    raise SystemExit(1 if errors else 0)
