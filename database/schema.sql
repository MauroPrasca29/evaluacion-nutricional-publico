-- Database schema for Nutritional Assessment System

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Locations/Sedes table
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Colombia',
    phone VARCHAR(20),
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Children table
CREATE TABLE children (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    identification_number VARCHAR(50) UNIQUE,
    identification_type VARCHAR(20) DEFAULT 'TI',
    location_id UUID REFERENCES locations(id),
    guardian_name VARCHAR(255),
    guardian_phone VARCHAR(20),
    guardian_email VARCHAR(255),
    address TEXT,
    birth_weight DECIMAL(5,2),
    birth_height DECIMAL(5,2),
    gestational_age INTEGER,
    medical_conditions TEXT,
    allergies TEXT,
    medications TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

-- Nutritional assessments/followups table
CREATE TABLE nutritional_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    child_id UUID REFERENCES children(id) ON DELETE CASCADE,
    assessment_date DATE NOT NULL,
    age_months INTEGER NOT NULL,
    weight DECIMAL(5,2) NOT NULL,
    height DECIMAL(5,2) NOT NULL,
    head_circumference DECIMAL(5,2),
    arm_circumference DECIMAL(5,2),
    bmi DECIMAL(5,2) GENERATED ALWAYS AS (weight / ((height/100) * (height/100))) STORED,
    weight_for_age_zscore DECIMAL(5,2),
    height_for_age_zscore DECIMAL(5,2),
    weight_for_height_zscore DECIMAL(5,2),
    bmi_for_age_zscore DECIMAL(5,2),
    nutritional_status VARCHAR(50),
    growth_status VARCHAR(50),
    feeding_type VARCHAR(50),
    dietary_intake TEXT,
    physical_activity TEXT,
    clinical_observations TEXT,
    recommendations TEXT,
    next_appointment DATE,
    assessed_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Alerts table
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    child_id UUID REFERENCES children(id) ON DELETE CASCADE,
    assessment_id UUID REFERENCES nutritional_assessments(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Reports table
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    parameters JSONB,
    file_path VARCHAR(500),
    file_size INTEGER,
    generated_by UUID REFERENCES users(id),
    location_id UUID REFERENCES locations(id),
    date_from DATE,
    date_to DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- File uploads table
CREATE TABLE file_uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    upload_type VARCHAR(50),
    uploaded_by UUID REFERENCES users(id),
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_children_location ON children(location_id);
CREATE INDEX idx_children_active ON children(is_active);
CREATE INDEX idx_children_birth_date ON children(date_of_birth);
CREATE INDEX idx_assessments_child ON nutritional_assessments(child_id);
CREATE INDEX idx_assessments_date ON nutritional_assessments(assessment_date);
CREATE INDEX idx_alerts_child ON alerts(child_id);
CREATE INDEX idx_alerts_resolved ON alerts(is_resolved);
CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_location ON reports(location_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_locations_updated_at BEFORE UPDATE ON locations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_children_updated_at BEFORE UPDATE ON children FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_assessments_updated_at BEFORE UPDATE ON nutritional_assessments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
