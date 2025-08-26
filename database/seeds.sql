-- Seed data for Nutritional Assessment System
-- This file contains test data for development

-- Insert communities
INSERT INTO communities (id, name, code, municipality, department, country, latitude, longitude, population) VALUES
(uuid_generate_v4(), 'La Esperanza', 'ESP001', 'Medellín', 'Antioquia', 'Colombia', 6.2442, -75.5812, 1500),
(uuid_generate_v4(), 'Villa Nueva', 'VN002', 'Medellín', 'Antioquia', 'Colombia', 6.2518, -75.5636, 2200),
(uuid_generate_v4(), 'El Progreso', 'PRG003', 'Bello', 'Antioquia', 'Colombia', 6.3370, -75.5547, 1800),
(uuid_generate_v4(), 'San José', 'SJ004', 'Itagüí', 'Antioquia', 'Colombia', 6.1845, -75.5990, 3200),
(uuid_generate_v4(), 'Buenos Aires', 'BA005', 'Envigado', 'Antioquia', 'Colombia', 6.1701, -75.5847, 2800);

-- Insert default admin user
INSERT INTO users (id, email, password_hash, first_name, last_name, role, phone, is_active) VALUES
(uuid_generate_v4(), 'admin@nutricional.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VcSAg/9S2', 'Admin', 'Sistema', 'admin', '+57 300 123 4567', true),
(uuid_generate_v4(), 'nutricionista@nutricional.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VcSAg/9S2', 'María', 'González', 'nutritionist', '+57 301 234 5678', true),
(uuid_generate_v4(), 'trabajador@nutricional.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VcSAg/9S2', 'Carlos', 'Rodríguez', 'health_worker', '+57 302 345 6789', true);

-- Insert sample children
WITH community_ids AS (
    SELECT id, name FROM communities LIMIT 5
),
user_ids AS (
    SELECT id FROM users WHERE role IN ('nutritionist', 'health_worker') LIMIT 2
)
INSERT INTO children (id, first_name, last_name, date_of_birth, gender, birth_weight, birth_height, community_id, guardian_name, guardian_phone, guardian_relationship, address, created_by) 
SELECT 
    uuid_generate_v4(),
    first_names.name,
    last_names.name,
    birth_dates.date_of_birth,
    genders.gender,
    birth_weights.weight,
    birth_heights.height,
    (SELECT id FROM community_ids ORDER BY random() LIMIT 1),
    guardians.name,
    phones.phone,
    'Madre',
    addresses.address,
    (SELECT id FROM user_ids ORDER BY random() LIMIT 1)
FROM 
    (VALUES 
        ('Ana'), ('Luis'), ('María'), ('Carlos'), ('Sofia'), ('Diego'), ('Isabella'), ('Mateo'), 
        ('Valentina'), ('Santiago'), ('Camila'), ('Sebastián'), ('Mariana'), ('Alejandro'), ('Gabriela'),
        ('Nicolás'), ('Daniela'), ('Andrés'), ('Valeria'), ('Felipe'), ('Natalia'), ('Emilio'), ('Lucía'),
        ('Tomás'), ('Elena'), ('Joaquín'), ('Adriana'), ('Martín'), ('Carolina'), ('Rodrigo')
    ) AS first_names(name)
CROSS JOIN 
    (VALUES 
        ('García'), ('Rodríguez'), ('López'), ('Martínez'), ('González'), ('Pérez'), ('Sánchez'), ('Ramírez'),
        ('Cruz'), ('Flores'), ('Gómez'), ('Díaz'), ('Reyes'), ('Morales'), ('Jiménez'), ('Herrera'),
        ('Medina'), ('Castro'), ('Vargas'), ('Ortiz'), ('Rubio'), ('Marín'), ('Alonso'), ('Gutiérrez'),
        ('Romero'), ('Navarro'), ('Torres'), ('Domínguez'), ('Vázquez'), ('Ramos')
    ) AS last_names(name)
CROSS JOIN 
    (VALUES 
        ('2018-01-15'::date), ('2018-03-22'::date), ('2018-06-10'::date), ('2018-09-05'::date), ('2018-12-18'::date),
        ('2019-02-28'::date), ('2019-05-14'::date), ('2019-08-30'::date), ('2019-11-12'::date), ('2020-01-25'::date),
        ('2020-04-08'::date), ('2020-07-20'::date), ('2020-10-03'::date), ('2021-01-16'::date), ('2021-04-29'::date),
        ('2021-08-11'::date), ('2021-11-24'::date), ('2022-02-07'::date), ('2022-05-21'::date), ('2022-09-04'::date),
        ('2022-12-17'::date), ('2023-03-02'::date), ('2023-06-15'::date), ('2023-09-28'::date), ('2024-01-10'::date)
    ) AS birth_dates(date_of_birth)
CROSS JOIN 
    (VALUES ('male'::gender_type), ('female'::gender_type)) AS genders(gender)
CROSS JOIN 
    (VALUES (2.8), (3.2), (3.5), (3.8), (4.1), (2.9), (3.3), (3.6), (3.9), (4.2)) AS birth_weights(weight)
CROSS JOIN 
    (VALUES (48.5), (49.2), (50.1), (51.0), (51.8), (48.8), (49.5), (50.4), (51.3), (52.1)) AS birth_heights(height)
CROSS JOIN 
    (VALUES 
        ('Carmen Rodríguez'), ('Ana López'), ('María González'), ('Luz Martínez'), ('Rosa García'),
        ('Patricia Sánchez'), ('Gloria Ramírez'), ('Esperanza Cruz'), ('Dolores Flores'), ('Pilar Gómez')
    ) AS guardians(name)
CROSS JOIN 
    (VALUES 
        ('+57 300 111 2233'), ('+57 301 222 3344'), ('+57 302 333 4455'), ('+57 303 444 5566'), ('+57 304 555 6677'),
        ('+57 305 666 7788'), ('+57 306 777 8899'), ('+57 307 888 9900'), ('+57 308 999 0011'), ('+57 309 000 1122')
    ) AS phones(phone)
CROSS JOIN 
    (VALUES 
        ('Calle 45 #23-67'), ('Carrera 12 #34-89'), ('Avenida 80 #56-12'), ('Calle 67 #78-34'), ('Carrera 25 #90-56'),
        ('Calle 123 #45-78'), ('Carrera 67 #89-01'), ('Avenida 45 #23-45'), ('Calle 89 #67-89'), ('Carrera 34 #12-34')
    ) AS addresses(address)
LIMIT 50;

-- Insert sample followups for the children
WITH children_sample AS (
    SELECT id, date_of_birth FROM children LIMIT 30
),
user_ids AS (
    SELECT id FROM users WHERE role IN ('nutritionist', 'health_worker')
)
INSERT INTO followups (id, child_id, evaluator_id, evaluation_date, age_months, weight, height, head_circumference, arm_circumference, hemoglobin, nutritional_status, clinical_observations, symptoms, physical_signs, recommendations, next_followup_date)
SELECT 
    uuid_generate_v4(),
    c.id,
    (SELECT id FROM user_ids ORDER BY random() LIMIT 1),
    CURRENT_DATE - (random() * 365)::int,
    EXTRACT(YEAR FROM age(CURRENT_DATE, c.date_of_birth)) * 12 + EXTRACT(MONTH FROM age(CURRENT_DATE, c.date_of_birth)),
    (random() * 8 + 8)::numeric(5,3), -- Weight between 8-16 kg
    (random() * 30 + 70)::numeric(5,2), -- Height between 70-100 cm
    (random() * 5 + 45)::numeric(5,2), -- Head circumference 45-50 cm
    (random() * 3 + 13)::numeric(5,2), -- Arm circumference 13-16 cm
    (random() * 3 + 11)::numeric(4,2), -- Hemoglobin 11-14 g/dL
    (ARRAY['normal', 'underweight', 'overweight'])[floor(random() * 3 + 1)]::nutritional_status,
    observations.text,
    symptoms_array.symptoms,
    signs_array.signs,
    recommendations.text,
    CURRENT_DATE + (random() * 90 + 30)::int
FROM children_sample c
CROSS JOIN (VALUES 
    ('Niño en buen estado general, desarrollo adecuado para la edad'),
    ('Se observa ligero retraso en el crecimiento, requiere seguimiento'),
    ('Excelente estado nutricional, continuar con alimentación actual'),
    ('Presenta signos leves de desnutrición, iniciar intervención nutricional'),
    ('Estado nutricional normal, mantener hábitos alimentarios saludables')
) AS observations(text)
CROSS JOIN (VALUES 
    (ARRAY['Buen apetito', 'Sueño reparador']),
    (ARRAY['Pérdida de apetito leve', 'Irritabilidad ocasional']),
    (ARRAY['Fatiga leve', 'Palidez']),
    (ARRAY[]::text[]),
    (ARRAY['Buen estado general'])
) AS symptoms_array(symptoms)
CROSS JOIN (VALUES 
    (ARRAY['Piel hidratada', 'Cabello brillante']),
    (ARRAY['Palidez leve en conjuntivas']),
    (ARRAY['Edema leve en extremidades']),
    (ARRAY[]::text[]),
    (ARRAY['Desarrollo normal'])
) AS signs_array(signs)
CROSS JOIN (VALUES 
    ('Continuar con alimentación balanceada rica en proteínas y vitaminas'),
    ('Aumentar consumo de alimentos ricos en hierro y vitamina C'),
    ('Incluir más frutas y verduras en la dieta diaria'),
    ('Suplementación con hierro según indicación médica'),
    ('Mantener lactancia materna exclusiva hasta los 6 meses')
) AS recommendations(text)
LIMIT 75;

-- Insert sample alerts
WITH children_with_issues AS (
    SELECT c.id as child_id, f.id as followup_id, f.nutritional_status
    FROM children c
    JOIN followups f ON c.id = f.child_id
    WHERE f.nutritional_status IN ('underweight', 'severe_malnutrition')
    LIMIT 15
)
INSERT INTO alerts (id, child_id, followup_id, alert_type, level, title, description, is_resolved)
SELECT 
    uuid_generate_v4(),
    cwi.child_id,
    cwi.followup_id,
    alert_types.type,
    alert_levels.level,
    alert_titles.title,
    alert_descriptions.description,
    (random() > 0.7)::boolean
FROM children_with_issues cwi
CROSS JOIN (VALUES 
    ('nutritional_risk'), ('growth_delay'), ('anemia_risk'), ('follow_up_overdue')
) AS alert_types(type)
CROSS JOIN (VALUES 
    ('high'::alert_level), ('medium'::alert_level), ('critical'::alert_level)
) AS alert_levels(level)
CROSS JOIN (VALUES 
    ('Riesgo nutricional detectado'), ('Retraso en el crecimiento'), ('Posible anemia'), ('Seguimiento vencido')
) AS alert_titles(title)
CROSS JOIN (VALUES 
    ('Se ha detectado un riesgo nutricional que requiere atención inmediata'),
    ('El niño presenta indicadores de retraso en el crecimiento'),
    ('Los niveles de hemoglobina sugieren posible anemia'),
    ('El seguimiento programado está vencido, programar nueva cita')
) AS alert_descriptions(description)
LIMIT 20;

-- Insert WHO growth standards sample data (simplified version)
-- This is a minimal sample - in production you would load the complete WHO tables
INSERT INTO who_standards (gender, age_months, measurement_type, l_value, m_value, s_value, p3, p15, p50, p85, p97) VALUES
-- Weight for age - Boys (sample data)
('male', 0, 'weight', 0.3487, 3.3464, 0.14602, 2.5, 2.9, 3.3, 3.9, 4.4),
('male', 1, 'weight', 0.2581, 4.4709, 0.13395, 3.4, 3.9, 4.5, 5.1, 5.8),
('male', 2, 'weight', 0.2297, 5.5675, 0.12385, 4.3, 4.9, 5.6, 6.3, 7.1),
('male', 6, 'weight', 0.0402, 7.9340, 0.11727, 6.4, 7.1, 7.9, 8.8, 9.8),
('male', 12, 'weight', -0.0718, 9.6479, 0.11316, 7.7, 8.4, 9.6, 10.8, 12.0),
-- Weight for age - Girls (sample data)
('female', 0, 'weight', 0.3809, 3.2322, 0.14171, 2.4, 2.8, 3.2, 3.7, 4.2),
('female', 1, 'weight', 0.1233, 4.1873, 0.13724, 3.2, 3.6, 4.2, 4.8, 5.5),
('female', 2, 'weight', 0.0962, 5.1282, 0.13000, 4.0, 4.5, 5.1, 5.8, 6.6),
('female', 6, 'weight', -0.0421, 7.3000, 0.12619, 5.7, 6.5, 7.3, 8.2, 9.3),
('female', 12, 'weight', -0.0881, 8.9481, 0.11986, 7.0, 7.8, 8.9, 10.1, 11.5);

-- Create some import logs
INSERT INTO import_logs (id, user_id, file_name, file_size, total_records, successful_records, failed_records, status, started_at, completed_at) VALUES
(uuid_generate_v4(), (SELECT id FROM users WHERE role = 'admin' LIMIT 1), 'children_import_2024_01.xlsx', 245760, 50, 48, 2, 'completed', CURRENT_TIMESTAMP - INTERVAL '2 days', CURRENT_TIMESTAMP - INTERVAL '2 days' + INTERVAL '5 minutes'),
(uuid_generate_v4(), (SELECT id FROM users WHERE role = 'nutritionist' LIMIT 1), 'followups_import_2024_01.xlsx', 189440, 75, 75, 0, 'completed', CURRENT_TIMESTAMP - INTERVAL '1 day', CURRENT_TIMESTAMP - INTERVAL '1 day' + INTERVAL '3 minutes');

-- Update sequences to ensure proper auto-increment behavior
SELECT setval(pg_get_serial_sequence('users', 'id'), (SELECT MAX(id) FROM users));
SELECT setval(pg_get_serial_sequence('communities', 'id'), (SELECT MAX(id) FROM communities));
SELECT setval(pg_get_serial_sequence('children', 'id'), (SELECT MAX(id) FROM children));
SELECT setval(pg_get_serial_sequence('followups', 'id'), (SELECT MAX(id) FROM followups));
SELECT setval(pg_get_serial_sequence('alerts', 'id'), (SELECT MAX(id) FROM alerts));

-- Create additional indexes for better performance with seed data
CREATE INDEX IF NOT EXISTS idx_followups_recent ON followups(evaluation_date DESC) WHERE evaluation_date >= CURRENT_DATE - INTERVAL '30 days';
CREATE INDEX IF NOT EXISTS idx_children_age ON children((EXTRACT(YEAR FROM age(CURRENT_DATE, date_of_birth))));
CREATE INDEX IF NOT EXISTS idx_alerts_recent ON alerts(created_at DESC) WHERE created_at >= CURRENT_DATE - INTERVAL '7 days';

-- Analyze tables for better query planning
ANALYZE users;
ANALYZE communities;
ANALYZE children;
ANALYZE followups;
ANALYZE alerts;
ANALYZE images;
ANALYZE who_standards;
ANALYZE import_logs;
