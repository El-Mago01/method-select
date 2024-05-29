-- @Block
USE method_select;

CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_type VARCHAR(255) NOT NULL,
    complexity VARCHAR(255) NOT NULL,
    team_size INT NOT NULL,
    recommended_method VARCHAR(255) NOT NULL
);

--@Block
RENAME TABLE Projects TO Project;

--@Block
SELECT * FROM project

--@Block
USE method_select
DELETE FROM project

--@Block
CREATE TABLE first_level_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_type VARCHAR(255),
    complexity VARCHAR(255),
    team_size INT,
    knowledge_of_customer VARCHAR(255),
    recommendation VARCHAR(255)
);

CREATE TABLE second_level_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_level_id INT,
    question_name VARCHAR(255),
    response VARCHAR(255),
    method VARCHAR(255),
    FOREIGN KEY (first_level_id) REFERENCES first_level_responses(id)
);
