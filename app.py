from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with your secret key

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project_methods.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the database models
class FirstLevelResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_type = db.Column(db.String(255))
    complexity = db.Column(db.String(255))
    team_size = db.Column(db.Integer)
    knowledge_of_customer = db.Column(db.String(255))
    recommendation = db.Column(db.String(255))

class SecondLevelResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_level_id = db.Column(db.Integer, db.ForeignKey('first_level_response.id'))
    question_name = db.Column(db.String(255))
    response = db.Column(db.String(255))
    method = db.Column(db.String(255))
    first_level = db.relationship('FirstLevelResponse', backref=db.backref('second_level_responses', lazy=True))

# Create the database tables within the application context
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    with open('config/high_level_methods.json') as config_file:
        config = json.load(config_file)
    return render_template('index.html', parameters=config['parameters'], data=session.get('data', {}))

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.form.to_dict()
    session['data'] = data  # Save data to session
    first_level_recommendation = get_first_level_recommendation(data)
    session['first_level_recommendation'] = first_level_recommendation  # Save the recommendation in session

    if not first_level_recommendation:
        return render_template('error.html', message="No valid recommendation found for the provided inputs.")

    # Save the first level response to the database
    first_level_response = FirstLevelResponse(
        project_type=data.get('project_type'),
        complexity=data.get('complexity'),
        team_size=data.get('team_size'),
        knowledge_of_customer=data.get('knowledge_of_customer'),
        recommendation=first_level_recommendation
    )
    db.session.add(first_level_response)
    db.session.commit()

    try:
        second_level_config_file = f"config/{first_level_recommendation.replace(' ', '_').lower()}.json"
    except AttributeError:
        return render_template('error.html', message="Error processing recommendation. Please try again.")

    if os.path.exists(second_level_config_file):
        with open(second_level_config_file) as config_file:
            second_level_config = json.load(config_file)
        return render_template('second_level.html', parameters=second_level_config['parameters'], method=first_level_recommendation, data=session.get('second_data', {}), first_level_id=first_level_response.id)
    else:
        return render_template('error.html', message="Configuration for second level not found.")

@app.route('/second_recommend', methods=['POST'])
def second_recommend():
    data = request.form.to_dict()
    session['second_data'] = data  # Save second level data to session
    second_level_recommendation = get_second_level_recommendation(data)
    
    if not second_level_recommendation:
        return render_template('error.html', message="No valid second level recommendation found for the provided inputs.")

    # Save the second level response to the database
    first_level_id = data.pop('first_level_id')
    for key, value in data.items():
        second_level_response = SecondLevelResponse(
            first_level_id=first_level_id,
            question_name=key,
            response=value,
            method=second_level_recommendation
        )
        db.session.add(second_level_response)
    db.session.commit()
    
    return render_template('final_recommendation.html', method=second_level_recommendation)

@app.route('/clear_second_level', methods=['POST'])
def clear_second_level():
    session.pop('second_data', None)
    return redirect(url_for('index'))

@app.route('/second_level', methods=['POST'])
def second_level():
    method = session.get('first_level_recommendation')
    second_level_config_file = f"config/{method.replace(' ', '_').lower()}.json"
    if os.path.exists(second_level_config_file):
        with open(second_level_config_file) as config_file:
            second_level_config = json.load(config_file)
        return render_template('second_level.html', parameters=second_level_config['parameters'], method=method, data=session.get('second_data', {}))
    else:
        return render_template('error.html', message="Configuration for second level not found.")

@app.route('/second_level_back', methods=['POST'])
def second_level_back():
    method = session.get('first_level_recommendation')
    data = session.get('data', {})
    with open('config/high_level_methods.json') as config_file:
        config = json.load(config_file)
    return render_template('index.html', parameters=config['parameters'], data=data)

@app.route('/previous_recommendations')
def previous_recommendations():
    first_level_responses = FirstLevelResponse.query.all()
    recommendations = []
    for first in first_level_responses:
        second = SecondLevelResponse.query.filter_by(first_level_id=first.id).first()
        recommendations.append({
            'first_level': first,
            'second_level': second
        })
    return render_template('previous_recommendations.html', recommendations=recommendations)

def get_first_level_recommendation(data):
    print("Received data:", data)
    with open('config/high_level_methods.json') as config_file:
        config = json.load(config_file)
        for rule in config['rules']:
            print("Checking rule:", rule)
            if all(
                (rule.get(key) == data.get(key) or rule.get(key) is None)
                if key != "team_size" else
                (
                    rule.get(key) is None or
                    (rule[key].get('min', float('-inf')) <= int(data.get(key, 0)) <= rule[key].get('max', float('inf')))
                )
                for key in rule if key != "method"
            ):
                print("Matched rule:", rule)
                return rule['method']
    return None

def get_second_level_recommendation(data):
    method = data.pop('method')
    config_file = f"config/{method.replace(' ', '_').lower()}.json"
    with open(config_file) as file:
        config = json.load(file)
        print("Parsing rules for second level:")
        for rule in config['rules']:
            rule_info = ", ".join(f"{key}: {value}" for key, value in rule.items())
            print(f"Checking rule: {{{rule_info}}}")
            if all(rule.get(key) == data.get(key) for key in rule if key != 'method'):
                print("Rule matched!")
                return rule['method']
    return None

if __name__ == '__main__':
    app.run(debug=True)
