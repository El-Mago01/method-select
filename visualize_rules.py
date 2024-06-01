# visualize_rules.py
from flask import Blueprint, render_template

visualize_rules_bp = Blueprint('visualize_rules', __name__)

@visualize_rules_bp.route('/visualize_rules')
def visualize_rules():
    return render_template('visualize_rules.html')
