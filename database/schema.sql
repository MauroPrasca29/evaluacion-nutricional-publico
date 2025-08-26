-- Nutritional Assessment Database Schema
-- PostgreSQL 15+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE user_role AS ENUM ('admin', 'nutritionist', 'health_worker');
CREATE TYPE gender_type AS ENUM ('male', 'female');
CREATE TYPE nutritional_status AS ENUM ('normal', 'underweight', 'overweight', 'obese', 'severe_malnutrition');
CREATE TYPE alert_level AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE evaluation_status AS ENUM ('pending', 'completed', 'cancelled');

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role user_role DEFAULT 'health_worker',
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Communities/Locations table
CREATE TABLE communities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    municipality VARCHAR(100),
    department VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Colombia',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    population INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Children table
CREATE TABLE children (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender gender_type NOT NULL,
    birth_weight DECIMAL(5, 3), -- in kg
    birth_height DECIMAL(5, 2), -- in cm
    community_id UUID REFERENCES communities(id),
    guardian_name VARCHAR(200),
    guardian_phone VARCHAR(20),
    guardian_relationship VARCHAR(50),
    address TEXT,
    medical_history TEXT,
    allergies TEXT,
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Follow-up evaluations table
CREATE TABLE followups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    child_id UUID NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    evaluator_id UUID NOT NULL REFERENCES users(id),
    evaluation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    age_months INTEGER NOT NULL,
    weight DECIMAL(5, 3) NOT NULL, -- in kg
    height DECIMAL(5, 2) NOT NULL, -- in cm
    bmi DECIMAL(5, 2) GENERATED ALWAYS AS (weight / ((height/100) * (height/100))) STORED,
    head_circumference DECIMAL(5, 2), -- in cm
    arm_circumference DECIMAL(5, 2), -- in cm
    triceps_skinfold DECIMAL(5, 2), -- in mm
    abdominal_perimeter DECIMAL(5, 2), -- in cm
    hemoglobin DECIMAL(4, 2), -- in g/dL
    nutritional_status nutritional_status,
    clinical_observations TEXT,
    symptoms TEXT[],
    physical_signs TEXT[],
    complementary_exams JSONB,
    guardian_comments TEXT,
    recommendations TEXT,
    next_followup_date DATE,
    status evaluation_status DEFAULT 'completed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Images table for photo documentation
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    followup_id UUID NOT NULL REFERENCES followups(id) ON DELETE CASCADE,
    image_type VARCHAR(50) NOT NULL, -- 'eyes', 'gums', 'general', etc.
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Alerts table
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    child_id UUID NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    followup_id UUID REFERENCES followups(id) ON DELETE CASCADE,
    alert_type VARCHAR(100) NOT NULL,
    level alert_level NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    is_resolved BOOLEAN DEFAULT false,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- WHO Growth Standards reference data
CREATE TABLE who_standards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    gender gender_type NOT NULL,
    age_months INTEGER NOT NULL,
    measurement_type VARCHAR(20) NOT NULL, -- 'weight', 'height', 'bmi'
    l_value DECIMAL(8, 6), -- Lambda (skewness)
    m_value DECIMAL(8, 4), -- Mu (median)
    s_value DECIMAL(8, 6), -- Sigma (coefficient of variation)
    p3 DECIMAL(8, 4),  -- 3rd percentile
    p15 DECIMAL(8, 4), -- 15th percentile
    p50 DECIMAL(8, 4), -- 50th percentile (median)
    p85 DECIMAL(8, 4), -- 85th percentile
    p97 DECIMAL(8, 4), -- 97th percentile
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Import logs table
CREATE TABLE import_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER,
    total_records INTEGER,
    successful_records INTEGER,
    failed_records INTEGER,
    errors JSONB,
    status VARCHAR(50) DEFAULT 'processing',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better performance
CREATE INDEX idx_children_community ON children(community_id);
CREATE INDEX idx_children_created_by ON children(created_by);
CREATE INDEX idx_children_date_of_birth ON children(date_of_birth);
CREATE INDEX idx_children_active ON children(is_active);

CREATE INDEX idx_followups_child ON followups(child_id);
CREATE INDEX idx_followups_evaluator ON followups(evaluator_id);
CREATE INDEX idx_followups_date ON followups(evaluation_date);
CREATE INDEX idx_followups_status ON followups(status);
CREATE INDEX idx_followups_nutritional_status ON followups(nutritional_status);

CREATE INDEX idx_alerts_child ON alerts(child_id);
CREATE INDEX idx_alerts_level ON alerts(level);
CREATE INDEX idx_alerts_resolved ON alerts(is_resolved);
CREATE INDEX idx_alerts_created ON alerts(created_at);

CREATE INDEX idx_images_followup ON images(followup_id);
CREATE INDEX idx_images_type ON images(image_type);

CREATE INDEX idx_who_standards_lookup ON who_standards(gender, age_months, measurement_type);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_communities_updated_at BEFORE UPDATE ON communities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_children_updated_at BEFORE UPDATE ON children
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_followups_updated_at BEFORE UPDATE ON followups
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries
CREATE VIEW children_with_latest_followup AS
SELECT 
    c.*,
    f.evaluation_date as last_evaluation_date,
    f.weight as last_weight,
    f.height as last_height,
    f.bmi as last_bmi,
    f.nutritional_status as last_nutritional_status,
    com.name as community_name
FROM children c
LEFT JOIN LATERAL (
    SELECT * FROM followups 
    WHERE child_id = c.id 
    ORDER BY evaluation_date DESC 
    LIMIT 1
) f ON true
LEFT JOIN communities com ON c.community_id = com.id
WHERE c.is_active = true;

CREATE VIEW active_alerts AS
SELECT 
    a.*,
    c.first_name || ' ' || c.last_name as child_name,
    c.date_of_birth,
    com.name as community_name
FROM alerts a
JOIN children c ON a.child_id = c.id
LEFT JOIN communities com ON c.community_id = com.id
WHERE a.is_resolved = false
ORDER BY a.level DESC, a.created_at DESC;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
