-- Seed data for development and testing

-- Insert test users
INSERT INTO users (username, email, hashed_password) VALUES
('admin', 'admin@nutrition.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'), -- password: secret
('nutritionist1', 'nutri1@nutrition.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'),
('nutritionist2', 'nutri2@nutrition.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW');

-- Insert test children
INSERT INTO children (name, birth_date, gender, guardian_name, guardian_phone, address, community) VALUES
('María González', '2020-03-15', 'F', 'Ana González', '555-0101', 'Calle Principal 123', 'Centro'),
('Carlos Rodríguez', '2019-07-22', 'M', 'Luis Rodríguez', '555-0102', 'Avenida Norte 456', 'Norte'),
('Sofia Martínez', '2021-01-10', 'F', 'Carmen Martínez', '555-0103', 'Calle Sur 789', 'Sur'),
('Diego López', '2018-11-05', 'M', 'Pedro López', '555-0104', 'Avenida Este 321', 'Este'),
('Isabella Torres', '2020-09-18', 'F', 'María Torres', '555-0105', 'Calle Oeste 654', 'Oeste');

-- Insert test follow-ups
INSERT INTO followups (child_id, weight, height, bmi, clinical_observations, nutritional_status, assessment_date) VALUES
(1, 12.5, 85.0, 17.3, 'Desarrollo normal, activa y alerta', 'normal', '2024-01-15'),
(1, 13.2, 87.0, 17.4, 'Crecimiento adecuado', 'normal', '2024-02-15'),
(2, 15.8, 95.0, 17.5, 'Buen estado general', 'normal', '2024-01-20'),
(3, 10.2, 78.0, 16.8, 'Peso ligeramente bajo', 'riesgo', '2024-01-25'),
(4, 18.5, 105.0, 16.8, 'Desarrollo normal para la edad', 'normal', '2024-02-01'),
(5, 11.8, 82.0, 17.6, 'Estado nutricional adecuado', 'normal', '2024-02-10');

-- Insert test alerts
INSERT INTO alerts (child_id, alert_type, severity, message) VALUES
(3, 'underweight', 'medium', 'Peso por debajo del percentil 10 para la edad'),
(1, 'followup_due', 'low', 'Próxima evaluación programada para esta semana'),
(4, 'vaccination_due', 'medium', 'Vacunas pendientes según calendario'),
(2, 'growth_concern', 'low', 'Monitorear velocidad de crecimiento');

-- Initial data seeds - empty file for structure
