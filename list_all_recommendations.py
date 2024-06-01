import glob
import json
import os

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

def get_recommendation_details(recommendation):
    details_file = os.path.join('recommendation_details', f'rd_{recommendation.replace(" ", "_").lower()}.json')
    if os.path.exists(details_file):
        try:
            with open(details_file, 'r') as file:
                details_data = json.load(file)
                details = details_data.get('details', 'No details provided')
                contact = details_data.get('contact', 'No contact provided')
                return details, contact
        except (json.JSONDecodeError, KeyError, OSError) as e:
            print(f"Error reading file {details_file}: {e}")
    return 'No details provided', 'No contact provided'

def get_all_recommendations_with_details():
    unique_recommendations = get_unique_recommendations()
    recommendations_with_details = []
    for recommendation in unique_recommendations:
        details, contact = get_recommendation_details(recommendation)
        recommendations_with_details.append({
            'recommendation': recommendation,
            'details': details,
            'contact': contact
        })
    return recommendations_with_details
