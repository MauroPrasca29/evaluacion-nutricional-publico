-- Initial database schema for nutritional assessment system

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Children table
CREATE TABLE children (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    gender VARCHAR(1) CHECK (gender IN ('M', 'F')),
    guardian_name VARCHAR(100) NOT NULL,
    guardian_phone VARCHAR(20),
    address TEXT,
    community VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Follow-ups table
CREATE TABLE followups (
    id SERIAL PRIMARY KEY,
    child_id INTEGER REFERENCES children(id) ON DELETE CASCADE,
    weight DECIMAL(5,2),
    height DECIMAL(5,2),
    bmi DECIMAL(4,2),
    arm_circumference DECIMAL(4,2),
    head_circumference DECIMAL(4,2),
    triceps_skinfold DECIMAL(4,2),
    abdominal_perimeter DECIMAL(5,2),
    hemoglobin DECIMAL(4,2),
    clinical_observations TEXT,
    nutritional_status VARCHAR(50),
    recommendations TEXT,
    assessment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Images table for storing photos
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    followup_id INTEGER REFERENCES followups(id) ON DELETE CASCADE,
    image_type VARCHAR(20) CHECK (image_type IN ('eye', 'gum', 'general')),
    image_path VARCHAR(255),
    analysis_result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Alerts table
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    child_id INTEGER REFERENCES children(id) ON DELETE CASCADE,
    alert_type VARCHAR(50),
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    message TEXT,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better performance
CREATE INDEX idx_children_name ON children(name);
CREATE INDEX idx_children_community ON children(community);
CREATE INDEX idx_followups_child_id ON followups(child_id);
CREATE INDEX idx_followups_date ON followups(assessment_date);
CREATE INDEX idx_alerts_child_id ON alerts(child_id);
CREATE INDEX idx_alerts_resolved ON alerts(is_resolved);
