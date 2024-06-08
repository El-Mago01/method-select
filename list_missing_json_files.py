from flask import Blueprint, render_template
import os
import json

list_missing_json_files_bp = Blueprint('list_missing_json_files', __name__)

@list_missing_json_files_bp.route('/list_missing_json_files')
def list_missing_json_files():
    config_dir = 'config'
    recommendation_details_dir = 'recommendation_details'
    method_files = set()
    methods_in_rules = set()

    # Collect all json filenames in the config directory and subdirectories
    for root, _, files in os.walk(config_dir):
        for file in files:
            if file.endswith('.json'):
                method_files.add(file)

    # Collect all methods from the rules in the json files
    for root, _, files in os.walk(config_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    config_data = json.load(f)
                    if 'rules' in config_data:
                        for rule in config_data['rules']:
                            if 'method' in rule:
                                method_json_filename = f"{rule['method'].replace(' ', '_').lower()}.json"
                                methods_in_rules.add(method_json_filename)

    # Prepare data for the table
    table_data = []
    for method in methods_in_rules:
        exists_in_config = method in method_files
        detailed_file_exists = os.path.exists(os.path.join(recommendation_details_dir, f"rd_{method}"))
        table_data.append((method, exists_in_config, detailed_file_exists))

    return render_template('list_missing_json_files.html', table_data=table_data)
