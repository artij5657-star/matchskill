-- Database: Railway MySQL

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'employer', 'admin') DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Skills Table
CREATE TABLE IF NOT EXISTS skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- 3. Interests Table
CREATE TABLE IF NOT EXISTS interests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- 4. User Skills Table
CREATE TABLE IF NOT EXISTS user_skills (
    user_id INT NOT NULL,
    skill_id INT NOT NULL,
    PRIMARY KEY (user_id, skill_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- 5. User Interests Table
CREATE TABLE IF NOT EXISTS user_interests (
    user_id INT NOT NULL,
    interest_id INT NOT NULL,
    PRIMARY KEY (user_id, interest_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (interest_id) REFERENCES interests(id) ON DELETE CASCADE
);

-- 6. Opportunities Table
CREATE TABLE IF NOT EXISTS opportunities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    type ENUM('Job','Internship','Project','Hackathon') DEFAULT 'Job',
    company VARCHAR(150),
    location VARCHAR(100),
    deadline DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Opportunity Skills Table
CREATE TABLE IF NOT EXISTS opportunity_skills (
    opportunity_id INT NOT NULL,
    skill_id INT NOT NULL,
    PRIMARY KEY (opportunity_id, skill_id),
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- 8. Opportunity Interests Table
CREATE TABLE IF NOT EXISTS opportunity_interests (
    opportunity_id INT NOT NULL,
    interest_id INT NOT NULL,
    PRIMARY KEY (opportunity_id, interest_id),
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(id) ON DELETE CASCADE,
    FOREIGN KEY (interest_id) REFERENCES interests(id) ON DELETE CASCADE
);

-- 9. Applications Table
CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    opportunity_id INT NOT NULL,
    status ENUM('Applied','Shortlisted','Rejected','Selected') DEFAULT 'Applied',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(id) ON DELETE CASCADE,
    UNIQUE (user_id, opportunity_id)
);

-- Default Skills Data
INSERT IGNORE INTO skills (name) VALUES 
('C'),('C++'),('Python'),('Java'),('JavaScript'),('HTML'),('CSS'),
('React'),('Node.js'),('Flask'),('Django'),('MySQL'),('MongoDB'),
('SQL'),('Data Structures'),('Algorithms'),('Machine Learning'),
('Artificial Intelligence'),('Deep Learning'),('Data Science'),
('Web Development'),('App Development'),('Git'),('GitHub'),
('Cloud Computing'),('Cyber Security'),('Computer Networks');

-- Default Interests Data
INSERT IGNORE INTO interests (name) VALUES 
('Web Development'),('App Development'),('Artificial Intelligence'),
('Machine Learning'),('Data Science'),('Cyber Security'),('Cloud Computing'),
('Software Development'),('UI/UX Design'),('Database'),('Research'),
('Open Source'),('Competitive Programming'),('Hackathons'),('Startups');

-- Sample Opportunities Data
INSERT INTO opportunities (title, description, type, company, location, deadline) VALUES
('Python Developer Intern', 'Work on Python based applications and backend development.', 'Internship', 'Tech Solutions', 'Remote', '2026-12-31'),
('Frontend Developer', 'Develop responsive websites using HTML, CSS and JavaScript.', 'Job', 'WebTech', 'Pune', '2026-11-30'),
('Machine Learning Project', 'Build a machine learning model for real-world prediction.', 'Project', 'AI Research Team', 'Remote', '2026-12-15'),
('Web Development Hackathon', 'Build an innovative web development project.', 'Hackathon', 'Innovation Club', 'Mumbai', '2026-10-30');