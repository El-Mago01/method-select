from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from list_missing_json_files import list_missing_json_files_bp 
import json
import os

# Import blueprints
from update_rules import update_rules_bp
from visualize_rules import visualize_rules_bp
from list_all_recommendations import get_unique_recommendations

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with your secret key

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project_methods.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the database models
class RecommendationResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(255), nullable=False, unique=True)
    project_leader = db.Column(db.String(255))
    date_added = db.Column(db.DateTime, default=datetime.now)
    level_1_data = db.Column(db.Text)  # Store JSON data as text
    level_2_data = db.Column(db.Text)
    level_3_data = db.Column(db.Text)
    level_4_data = db.Column(db.Text)
    level_5_data = db.Column(db.Text)
    level_1_recommendation = db.Column(db.String(255))
    level_2_recommendation = db.Column(db.String(255))
    level_3_recommendation = db.Column(db.String(255))
    level_4_recommendation = db.Column(db.String(255))
    level_5_recommendation = db.Column(db.String(255))

    def __repr__(self):
        return '<Name %r>' % self.project_name

# Function to check if database needs to be reset
def check_database():
    try:
        # Try to get the first record from the RecommendationResponse table
        db.session.query(RecommendationResponse).first()
    except Exception as e:
        # If there is an exception, the table does not exist or is not in the correct format
        return True
    return False

# Function to prompt user for database reset
def prompt_reset_database():
    reset_db = input("The database structure might have changed. Do you want to reset the database? (yes/no): ")
    if reset_db.lower() == 'yes':
        with app.app_context():
            db.drop_all()
            db.create_all()
            print("Database has been reset.")
    else:
        print("Database has not been reset. Please ensure it matches the current model.")

# Check if the database needs to be reset
if check_database():
    prompt_reset_database()

# Maximum level constant
MAX_LEVEL = 5

# Print the current working directory
print(f"Current working directory: {os.getcwd()}")

@app.route('/')
def index():
    session.clear()  # Clear the session to start fresh
    return render_template('index.html', parameters=get_parameters('high_level_methods.json'), level=1)

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/view_recommendation/<int:rec_id>', methods=['GET', 'POST'])
def view_recommendation(rec_id):
    recommendation_response = RecommendationResponse.query.get_or_404(rec_id)
    levels_data = {}

    # Set session variables for project_name and project_leader
    session['project_name'] = recommendation_response.project_name
    session['project_leader'] = recommendation_response.project_leader

    for level in range(1, MAX_LEVEL + 1):
        data_attr = f'level_{level}_data'
        recommendation_attr = f'level_{level}_recommendation'

        levels_data[data_attr] = json.loads(getattr(recommendation_response, data_attr) or '{}')
        session[f'level_{level}_data'] = levels_data[data_attr]
        session[f'level_{level}_recommendation'] = getattr(recommendation_response, recommendation_attr)

        print(f"Level {level} data: {levels_data[data_attr]}")
        print(f"Level {level} recommendation: {session.get(f'level_{level}_recommendation')}")
        print(f"now the session contains: {session}")

    print("Clearing the recommendations in the database for levels 2-5")
    # Clear recommendations for levels 2 to 5 if viewing level 1
    for level in range(2, MAX_LEVEL + 1):
        setattr(recommendation_response, f'level_{level}_data', None)
        setattr(recommendation_response, f'level_{level}_recommendation', None)
    db.session.commit()

    if request.method == 'POST':
        level = int(request.form.get('level'))
        print(f"Received form data for level {level}: {request.form}")  # Debug print
        data = {key: request.form[key] for key in request.form if key != 'level'}
        setattr(recommendation_response, f'level_{level}_data', json.dumps(data))
        db.session.commit()

        new_recommendation, details, contact, link = get_recommendation(data, level)
        print(f"What details were received from get_recommendation? {new_recommendation}, {details}, {contact}, {link}.")
        setattr(recommendation_response, f'level_{level}_recommendation', new_recommendation)
        db.session.commit()

        session[f'level_{level}_recommendation'] = new_recommendation

        next_level = level + 1
        if next_level > MAX_LEVEL or new_recommendation is None:
            return redirect(url_for('previous_recommendations'))

        next_recommendation = new_recommendation
        print(f"Next recommendation for level {next_level}: {next_recommendation}")  # Debug print
        if next_recommendation:
            return render_template('recommend.html', parameters=get_parameters(f"{next_recommendation.replace(' ', '_').lower()}.json"), 
                                   level=next_level, 
                                   recommendation=next_recommendation, 
                                   data=data,
                                   details=details, 
                                   contact=contact, 
                                   link=link
                                   )
        else:
            return redirect(url_for('previous_recommendations'))

    level = 1
    data_attr = f'level_{level}_data'
    levels_data = {data_attr: json.loads(getattr(recommendation_response, data_attr) or '{}')}
    print(f"Rendering view_recommendation.html with levels_data: {levels_data}")  # Debug print

    recommendation_file = "high_level_methods.json"
    return render_template('view_recommendation.html', recommendation=recommendation_response, levels_data=levels_data, 
                           parameters=get_parameters(recommendation_file), level=level, max_level=MAX_LEVEL)

@app.route('/visualize_rules')
def visualize_rules():
    # Placeholder function for visualizing the rules algorithm
    return render_template('visualize_rules.html')

@app.route('/update_rules')
def update_rules():
    # Placeholder function for updating the rules algorithm
    return render_template('update_rules.html')

from list_all_recommendations import get_all_recommendations_with_details  # Update import

@app.route('/list_all_recommendations')
def list_all_recommendations():
    recommendations_with_details = get_all_recommendations_with_details()
    return render_template('list_all_recommendations.html', recommendations=recommendations_with_details)

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.form.to_dict()
    level = int(data.pop('level'))

    # Store answers in session (new lines)
    if f'level_{level}_data' not in session:
        session[f'level_{level}_data'] = {}
    session[f'level_{level}_data'].update(data)

    print(f"Current session: {session}")
    # Store project name and leader in the session if they are provided
    if level == 1:
        project_name = data.pop('project_name', None)
        project_leader = data.pop('project_leader', None)
        if project_name and project_leader:
            session['project_name'] = project_name
            session['project_leader'] = project_leader

    # Log the current level and data
    print(f"Current level: {level}")
    print(f"Received data: {data}")

    # Collect all answers from previous levels (new lines)
    all_data = {}
    for i in range(1, level + 1):
        all_data.update(session.get(f'level_{i}_data', {}))

    recommendation, details, contact, link = get_recommendation(all_data, level)  # Change data to all_data

    if not recommendation:
        print("No valid recommendation found for the provided inputs")
        return render_template('error.html', message=f"No valid recommendation found for the provided inputs for level {level}. Please check your inputs and try again.", level=level)

    print(f"Current recommendation: {recommendation}")
    print(f"Details: {details}")
    print(f"Contact: {contact}")
    print(f"Link: {link}")
    print(f"The following data will be stored in the database for level {level}:")

    session[f'level_{level}_data'] = data
    session[f'level_{level}_recommendation'] = recommendation

    print(f"Here is the content of session: {session}")

    # Retrieve or create a RecommendationResponse object
    if 'recommendation_id' not in session:
        if 'project_name' not in session or 'project_leader' not in session:
            return render_template('error.html', message="Project name and leader are required.", level=level)

        # Check if project name already exists
        print(f"Checking the content of data: {session}")
        existing_project = RecommendationResponse.query.filter_by(project_name=session['project_name']).first()
        if existing_project:
            # Use the existing project if found
            recommendation_response = existing_project
            session['recommendation_id'] = existing_project.id
        else:
            print("Creating a NEW RecommendationResponse object")
            recommendation_response = RecommendationResponse(
                project_name=session['project_name'],
                project_leader=session['project_leader']
            )
            print("Storing and committing the data")
            db.session.add(recommendation_response)
            db.session.commit()
            session['recommendation_id'] = recommendation_response.id
    else:
        print(f"Using an existing RecommendationResponse object")
        recommendation_response = RecommendationResponse.query.get(session['recommendation_id'])
        db.session.add(recommendation_response)
        print(f"Storing the recommendation in the database. {recommendation_response}")

    # Update the corresponding level recommendation
    setattr(recommendation_response, f'level_{level}_data', json.dumps(data))
    setattr(recommendation_response, f'level_{level}_recommendation', recommendation)
    db.session.commit()

    next_level = level + 1
    
    configfile_to_find = f'{recommendation.replace(" ", "_").lower()}.json'  # Change to double quotes
    print(f'Trying to locate config file {configfile_to_find}')
    config_path = None
    base_dir = 'config'
    for root, _, files in os.walk(base_dir):
        if configfile_to_find in files:
            config_path = os.path.join(root, configfile_to_find)
            break
        else:
            print(f"root {root} not found in  files={files}")

    print(f"Next level config file path: {config_path}")

    if level >= MAX_LEVEL or not config_path:
        if level >= MAX_LEVEL:
            print(f"Reached maximum level {MAX_LEVEL}")
        else: 
            print(f"No next level config file found config_path={config_path}. Showing final recommendation.")
        session[f'level_{level}_data'] = data
        session[f'level_{level}_recommendation'] = recommendation
        print(f"The following details will be provided {details}")
        return render_template('final_recommendation.html', method=recommendation, details=details, contact=contact, link=link)

    if config_path:
        print(f"Found next level config file: {config_path}")
        session[f'level_{level}_data'] = data
        session[f'level_{level}_recommendation'] = recommendation
        return render_template(
            'recommend.html', parameters=get_parameters(f"{recommendation.replace(' ', '_').lower()}.json"), 
            level=next_level, 
            recommendation=recommendation, 
            details=details, 
            contact=contact, 
            link=link
        )
    else:
        print(f"No next level config file found. Showing final recommendation.")
        return render_template('final_recommendation.html', method=recommendation, details=details, contact=contact, link=link)


@app.route('/previous_recommendations')
def previous_recommendations():
    print("Showing the content of the database:")
    recommendations = RecommendationResponse.query.all()
    print(f"These are the stored recommendations {recommendations}")
    return render_template('previous_recommendations.html', recommendations=recommendations, max_level=MAX_LEVEL)

@app.route('/back', methods=['POST'])
def back():
    level = int(request.form.get('level')) - 1
    print(f"The back-button is pressed. Going from level {level + 1} to level {level}")

    if level == 0:
        return redirect(url_for('index'))

    previous_recommendation = session.get(f'level_{level}_recommendation')
    previous_data = session.get(f'level_{level}_data')
    print(f"The content of all the session data is: {dict(session)}")
    print(f"The previous recommendation is: {previous_recommendation}")
    print(f"The previous input data is: {previous_data}")

    if level == 1:
        previous_level_config_file = 'high_level_methods.json'
    else:
        previous_level_config_file = f"config/{previous_recommendation.replace(' ', '_').lower()}.json"
    
    print(f"Loading previous level config file: {previous_level_config_file}")

    if os.path.exists(previous_level_config_file):
        print(f"Found previous level config file: {previous_level_config_file}")
        return render_template(
            'recommend.html', 
            parameters=get_parameters(previous_level_config_file), 
            level=level, 
            recommendation=previous_recommendation, 
            data=previous_data, 
            pre_filled=previous_data
        )
    else:
        print(f"No previous level config file found. Showing first recommendation.")
        session.clear()  # Clear the session to start fresh
        return render_template(
            'index.html', 
            parameters=get_parameters('high_level_methods.json'), 
            level=1, 
            data=previous_data, 
            pre_filled=previous_data
        )

def get_parameters(config_file):
    base_dir = 'config'
    for root, _, files in os.walk(base_dir):
        if config_file in files:
            config_path = os.path.join(root, config_file)
            print(f"Loading parameters from config path: {config_path}")
            try:
                with open(config_path) as file:
                    config = json.load(file)
                return config['parameters']
            except OSError as e:
                print(f"Error opening file {config_path}: {e}")
                return []
    print(f"Config file {config_file} not found in any subdirectory of {base_dir}.")
    return []


def get_recommendation(data, level):
    print(f"For get_recommendation function, this is the received level: {level}")
    if level == 1:
        config_file = 'high_level_methods.json'
    else:
        previous_recommendation = session.get(f'level_{level - 1}_recommendation')
        print(f"get_recommendation: input from session based on level_{level-1}_recommendation: {previous_recommendation}")
        if previous_recommendation:
            config_file = f"{previous_recommendation.replace(' ', '_').lower()}.json"
        else:
            print(f"No recommendation found for level {level-1}")
            print(f"This is the actual data for session: {session}")
            return None, 'no detailed information provided', 'no contact information provided', 'no link provided'

    config_path = None
    base_dir = 'config'
    for root, _, files in os.walk(base_dir):
        if config_file in files:
            config_path = os.path.join(root, config_file)
            break

    if not config_path:
        print(f"Config file {config_file} not found in any subdirectory of {base_dir}.")
        return None, 'no detailed information provided', 'no contact information provided', 'no link provided'

    print(f"Constructed config path: {config_path}")
    print(f"Checking rules in {config_path} for level {level} with data: {data}")

    try:
        with open(config_path) as file:
            config = json.load(file)
    except OSError as e:
        print(f"Error opening file {config_path}: {e}")
        return None, 'no detailed information provided', 'no contact information provided', 'no link provided'

    def match_rule_value(rule_value, data_value):
        if data_value is None:
            return rule_value is None
        if isinstance(rule_value, list):
            return data_value.lower() in (val.lower() for val in rule_value)
        elif isinstance(rule_value, str):
            return rule_value.lower() == data_value.lower()
        elif isinstance(rule_value, dict):
            return check_range(rule_value, data_value)
        return False

    for rule in config['rules']:
        print(f"Checking rule: {rule}")
        all_match = True
        for key in rule:
            if key == 'method':
                continue
            rule_value = rule.get(key)
            data_value = data.get(key)
            match = rule_value is None or match_rule_value(rule_value, data_value)
            print(f"  - Key: {key}, Rule Value: {rule_value}, Data Value: {data_value}, Match: {match}")
            if not match:
                all_match = False
                break
        if all_match:
            print(f"Matched rule: {rule}")
            method = rule['method']
            detail_file = f"rd_{method.replace(' ', '_').lower()}.json"
            detail_path = os.path.join('recommendation_details', detail_file)
            try:
                with open(detail_path) as file:
                    details_json = file.read()
                    print(f"Details JSON content: {details_json}")
                    details_json = json.loads(details_json)
                    details = details_json.get('details', 'no detailed information provided')
                    contact = details_json.get('contact', 'no contact information provided')
                    link = details_json.get('link', 'no link provided')
            except OSError:
                details = 'no detailed information provided'
                contact = 'no contact information provided'
                link = 'no link provided'
            return method, details, contact, link
    print("No matching rule found.")
    return None, 'no detailed information provided', 'no contact information provided', 'no link provided'


def check_range(range_dict, value):
    value = int(value)
    min_val = range_dict.get('min', float('-inf'))
    max_val = range_dict.get('max', float('inf'))
    return min_val <= value <= max_val

def get_level_recommendation(rec, level):
    return getattr(rec, f'level_{level}_recommendation', None)

app.jinja_env.globals.update(get_level_recommendation=get_level_recommendation)
app.jinja_env.globals.update(get_parameters=get_parameters)

# Register blueprints
app.register_blueprint(update_rules_bp)
app.register_blueprint(visualize_rules_bp)
app.register_blueprint(list_missing_json_files_bp)


if __name__ == '__main__':
    app.run(debug=True)
