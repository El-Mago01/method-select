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
    for path, config in configs.items():
        for index, rule in enumerate(config.get("rules", []), 1):
            if not isinstance(rule, dict) or not isinstance(rule.get("method"), str):
                continue
            method = rule["method"]
            filename = method.replace(" ", "_").lower() + ".json"
            detail = details_dir / ("rd_" + filename)
            if filename not in by_name and not detail.exists():
                warnings.append(f"{path}: rule {index}: no next-level config or details for {method!r}")
            elif not detail.exists():
                warnings.append(f"{path}: rule {index}: missing optional details for {method!r}")
    return errors, warnings


if __name__ == "__main__":
    errors, warnings = validate()
    for item in errors:
        print("ERROR:", item)
    for item in warnings:
        print("WARNING:", item)
    print(f"Validation finished: {len(errors)} error(s), {len(warnings)} warning(s).")
    raise SystemExit(1 if errors else 0)
