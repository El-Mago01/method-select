# Project Method Recommender

A rule-based web application that helps project leaders explore suitable project management methodologies based on the 
characteristics of their projects.

**Status:** Proof of Concept (POC) — not intended for production use.

## Background and Motivation

The project started during an informal Friday afternoon coding session with the director of an R&D center. We were 
experimenting with ChatGPT-assisted software development and exploring how generative AI could help us build applications.

What started as a coding experiment quickly became a personal project, often extending well beyond normal working hours. 
It was also an opportunity for me to reconnect with my earlier background in software development.

The idea for the application emerged from a challenge within our R&D organization: project leaders often chose familiar 
project management methodologies by default, rather than considering which approach might best suit their particular project.

We wanted to provide an advisory tool that would encourage project leaders to reflect on their choices and explore alternatives.

## The Concept

The Project Method Recommender guides users through a series of configurable questions about their project, for instance:

- Type of project
- Number of team members
- Familiarity with the technology involved
- Understanding of customer requirements
- Clarity and agreement on project scope

Based on the answers, the application evaluates configurable decision rules and recommends a suitable family of project management 
methodologies, such as Agile, Lean or classical project management.

Users can then explore more specific methods through additional recommendation levels.

The intention was not to replace the project leader's judgment, but to support a more deliberate and informed decision.

### Configurable Decision Rules

An important design principle was to separate the recommendation logic from the application code.

The decision rules and questions are stored in JSON configuration files. This allows the recommendation logic 
to be adapted without rewriting the core application.

The original intention was for the Project Office Manager and me to maintain these rules, drawing on our knowledge of 
project management methodologies and incorporating lessons learned.

## Features

The proof of concept includes:

- A web interface for entering project characteristics
- Multi-level, rule-based methodology recommendations
- JSON-based configuration of questions and decision rules
- Additional descriptions and information about recommended methods
- Database storage of project information and recommendations
- An overview of previously stored recommendations
- Supporting utilities for inspecting recommendation rules and configuration files

Some administrative functionality, including editing and visualizing rules through the web interface, remains incomplete.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application programming |
| Flask | Web framework and routing |
| Flask-SQLAlchemy | Database access using an ORM |
| SQLite | Database used in the current repository |
| JSON | Configurable questions and recommendation rules |
| Jinja2 | HTML template rendering |
| HTML, CSS and JavaScript | Web interface |
| Flask-Migrate | Database migration tooling included in the project |

## Project Structure

The main components are organized as follows:

```text
method-select/
├── app.py
├── config/
│   └── high_level_methods.json
├── recommendation_details/
├── templates/
├── static/
├── migrations/
├── list_all_recommendations.py
├── list_missing_json_files.py
├── update_rules.py
├── visualize_rules.py
└── requirements.txt
```

- `app.py` contains the Flask application, database model, routes and recommendation workflow.
- `config/` contains the questions and rules for selecting methodologies at different levels.
- `recommendation_details/` contains additional information about recommended approaches.
- `templates/` and `static/` contain the web interface.
- The supporting Python modules provide configuration inspection and experimental rule-management functionality.

## Installation and Configuration

### 1. Clone the repository

```bash
git clone https://github.com/El-Mago01/method-select.git
cd method-select
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Flask secret key

Create a `.env` file in the project root:

```env
SECRET_KEY=replace-with-a-randomly-generated-secret
```

Generate a suitable value with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

The application loads environment variables using `python-dotenv` and reads `SECRET_KEY` when initializing Flask.

**Important:** Never commit `.env` or real secret keys to version control. Make sure `.env` is listed in `.gitignore`.

### 5. Start the application

```bash
python app.py
```

The application uses a local SQLite database, configured in `app.py`.

**Note:** The existing POC contains an interactive database-check/reset mechanism. Depending on the local database state, 
startup may require additional steps. Do not reset an existing database without first checking whether its contents need 
to be preserved.

## Development Approach

This project was developed through hands-on experimentation with AI-assisted software development, using ChatGPT to support coding, 
troubleshooting and iterative improvements.

The development process combined generated code with my own decisions about the application concept, functionality, rules 
and implementation.

Although generative AI was used to assist in developing the application, **the application itself does not use an LLM to 
generate its recommendations**. Recommendations are determined by configurable JSON-based rules.

## Project Scope and Status

This application was developed as an exploratory POC within an R&D organization.

Its purpose was to demonstrate the concept and provide a basis for discussion, rather than to deliver a production-ready system.

If the initiative had been prioritized as an internal *in-silico* improvement project, the internal software development 
department would have used the POC as input for designing and implementing a production solution.

The initiative ultimately did not receive sufficient priority to proceed to product development.

As a result, this repository reflects the original exploratory work, including experimental implementation choices, 
incomplete functionality and opportunities for further improvement.

## Known Limitations

- The application was not designed for production deployment.
- The rule-management functionality is not fully implemented.
- Recommendation quality depends on the completeness and correctness of the configured rules.
- The existing database initialization and reset mechanism needs improvement.
- Automated testing and dependency management require further attention.
- Security, error handling and maintainability would need additional work before production use.

## Potential Future Development

If the concept were developed further, possible improvements could include:

- A user-friendly interface for maintaining and validating decision rules
- Automated tests for recommendation logic and rule coverage
- Clear separation between business logic, database access and web routes
- More robust database migrations and configuration management
- Feedback from project leaders to improve the recommendations
- Evaluation of recommendation quality against real project cases

## Author

**Martin Gorren**

Developed as an exploratory project combining experience in organizational development, project methodologies and 
software engineering with renewed hands-on programming through AI-assisted development.