# list_all_recommendations.py
import glob
import json


def get_unique_recommendations():
    recommendations = set()
    config_files = glob.glob('config/*.json')

    for file_path in config_files:
        with open(file_path, 'r') as file:
            try:
                config = json.load(file)
                for rule in config.get('rules', []):
                    if 'method' in rule:
                        recommendations.add(rule['method'])
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error reading file {file_path}: {e}")

    return sorted(recommendations)
