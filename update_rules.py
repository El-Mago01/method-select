# update_rules.py
from flask import Blueprint, render_template, request

update_rules_bp = Blueprint('update_rules', __name__)

@update_rules_bp.route('/update_rules')
def update_rules():
    return render_template('update_rules.html')

@update_rules_bp.route('/update_rules', methods=['POST'])
def update_rules_post():
    # Implement your rule update logic here
    # You can access form data using request.form
    return render_template('update_rules.html', message="Rules updated successfully!")
