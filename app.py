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
class RecommendationResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level_1_recommendation = db.Column(db.String(255))
    level_2_recommendation = db.Column(db.String(255))
    level_3_recommendation = db.Column(db.String(255))
    level_4_recommendation = db.Column(db.String(255))
    level_5_recommendation = db.Column(db.String(255))

# Drop and recreate the tables within the application context
with app.app_context():
    db.drop_all()
    db.create_all()

# Maximum level constant
MAX_LEVEL = 5

# Print the current working directory
print(f"Current working directory: {os.getcwd()}")

@app.route('/')
def index():
    session.clear()  # Clear the session to start fresh
    return render_template('index.html', parameters=get_parameters('high_level_methods.json'), level=1)

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.form.to_dict()
    level = int(data.pop('level'))

    # Log the current level and data
    print(f"Current level: {level}")
    print(f"Received data: {data}")

    recommendation = get_recommendation(data, level)

    if not recommendation:
        print("No valid recommendation found for the provided inputs.")
        return render_template('error.html', message="No valid recommendation found for the provided inputs. Please check your inputs and try again.")

    session[f'level_{level}_data'] = data
    session[f'level_{level}_recommendation'] = recommendation

    # Retrieve or create a RecommendationResponse object
    if 'recommendation_id' not in session:
        recommendation_response = RecommendationResponse()
        db.session.add(recommendation_response)
        db.session.commit()
        session['recommendation_id'] = recommendation_response.id
    else:
        recommendation_response = RecommendationResponse.query.get(session['recommendation_id'])

    # Update the corresponding level recommendation
    setattr(recommendation_response, f'level_{level}_recommendation', recommendation)
    db.session.commit()

    if level >= MAX_LEVEL:
        print(f"Reached maximum level {MAX_LEVEL}. Showing final recommendation.")
        return render_template('final_recommendation.html', method=recommendation)

    next_level = level + 1
    next_level_config_file = os.path.join('config', f"{recommendation.replace(' ', '_').lower()}.json")
    print(f"Next level config file path: {next_level_config_file}")

    if os.path.exists(next_level_config_file):
        print(f"Found next level config file: {next_level_config_file}")
        return render_template('recommend.html', parameters=get_parameters(f"{recommendation.replace(' ', '_').lower()}.json"), level=next_level, recommendation=recommendation)
    else:
        print(f"No next level config file found. Showing final recommendation.")
        return render_template('final_recommendation.html', method=recommendation)

@app.route('/previous_recommendations')
def previous_recommendations():
    recommendations = RecommendationResponse.query.all()
    return render_template('previous_recommendations.html', recommendations=recommendations, max_level=MAX_LEVEL)

@app.route('/back', methods=['POST'])
def back():
    level = int(request.form.get('level')) - 1
    if level == 0:
        return redirect(url_for('index'))

    previous_recommendation = session.get(f'level_{level}_recommendation')
    previous_data = session.get(f'level_{level}_data')
    previous_level_config_file = os.path.join('config', f"{previous_recommendation.replace(' ', '_').lower()}.json") if level > 1 else 'high_level_methods.json'

    return render_template('recommend.html', parameters=get_parameters(previous_level_config_file), level=level, recommendation=previous_recommendation, data=previous_data)

def get_parameters(config_file):
    config_path = os.path.join('config', config_file)
    print(f"Loading parameters from config path: {config_path}")
    try:
        with open(config_path) as file:
            config = json.load(file)
    except OSError as e:
        print(f"Error opening file {config_path}: {e}")
        return []
    return config['parameters']

def get_recommendation(data, level):
    if level == 1:
        config_file = 'high_level_methods.json'
    else:
        recommendation = session.get(f'level_{level - 1}_recommendation')
        if recommendation:
            config_file = f"{recommendation.replace(' ', '_').lower()}.json"
        else:
            print(f"No recommendation found for level {level - 1}")
            return None

    config_path = os.path.join('config', config_file)
    print(f"Constructed config path: {config_path}")
    print(f"Checking rules in {config_path} for level {level} with data: {data}")

    try:
        with open(config_path) as file:
            config = json.load(file)
    except OSError as e:
        print(f"Error opening file {config_path}: {e}")
        return None

    for rule in config['rules']:
        print(f"Checking rule: {rule}")
        if all((rule.get(key) is None or
                (isinstance(rule.get(key), list) and data.get(key) is not None and data.get(key).lower() in [val.lower() for val in rule.get(key)]) or
                (isinstance(rule.get(key), str) and data.get(key) is not None and rule.get(key).lower() == data.get(key).lower())) for key in rule if key != 'method'):
            print(f"Matched rule: {rule}")
            return rule['method']
    print("No matching rule found.")
    return None

def get_level_recommendation(rec, level):
    return getattr(rec, f'level_{level}_recommendation', None)

app.jinja_env.globals.update(get_level_recommendation=get_level_recommendation)
 
if __name__ == '__main__':
    app.run(debug=True)
