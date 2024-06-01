# list_all_recommendations.py
from flask import Blueprint, render_template, request

list_all_recommendations_bp = Blueprint('list_all_recommendations', __name__)


@list_all_recommendations_bp.route('/list_all_recommendations')
def list_all_recommendations():
    # Placeholder function for listing all available recommendations
    return render_template('list_all_recommendations.html')