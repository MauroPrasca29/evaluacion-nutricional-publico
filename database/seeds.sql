-- Seed data for Nutritional Assessment System

-- Roles
INSERT INTO roles (nombre, descripcion) VALUES
('Administrador', 'Usuario con control total del sistema'),
('Nutricionista', 'Profesional encargado de los seguimientos y evaluaciones'),
('Asistente', 'Usuario de apoyo administrativo');

-- Usuarios (nutricionistas, administradores, etc.)
INSERT INTO usuarios (nombre, correo, telefono, rol_id, contrasena) VALUES
('Ana Pérez', 'ana.perez@fundacion.org', '3001112233', 2, 'hashed_password_1'),
('Carlos Gómez', 'carlos.gomez@fundacion.org', '3002223344', 2, 'hashed_password_2'),
('Laura Martínez', 'laura.martinez@fundacion.org', '3003334455', 1, 'hashed_password_admin');

-- Sedes
INSERT INTO sedes (nombre, municipio, departamento, telefono) VALUES
('Sede Centro', 'Cartagena', 'Bolívar', '6051234567'),
('Sede Norte', 'Turbaco', 'Bolívar', '6057654321');

-- Acudientes
INSERT INTO acudientes (nombre, telefono, correo, direccion) VALUES
('María López', '3014445566', 'maria.lopez@email.com', 'Barrio San Pedro, Cartagena'),
('José Ramírez', '3025556677', 'jose.ramirez@email.com', 'Barrio Manga, Cartagena');

-- Infantes
INSERT INTO infantes (nombre, fecha_nacimiento, genero, acudiente_id, sede_id) VALUES
('Juan Ramírez', '2018-03-15', 'Masculino', 2, 1),
('Sofía Pérez', '2020-07-10', 'Femenino', 1, 2);

-- Seguimientos
INSERT INTO seguimientos (infante_id, encargado_id, fecha, observacion) VALUES
(1, 1, '2025-06-01', 'Niño activo, leve palidez observada'),
(2, 2, '2025-06-02', 'Buen estado general, sin signos visibles');

-- Datos antropométricos
INSERT INTO datos_antropometricos (seguimiento_id, peso, estatura, circunferencia_braquial, perimetro_cefalico, pliegue_cutaneo, perimetro_abdominal) VALUES
(1, 18.5, 110, 14.2, 48.5, 6.0, 52.0),
(2, 12.0, 90, 13.0, 46.0, 5.5, 50.0);

-- Exámenes
INSERT INTO examenes (seguimiento_id, hemoglobina) VALUES
(1, 10.2),
(2, 12.5);

-- Síntomas
INSERT INTO sintomas (nombre) VALUES
('Palidez'),
('Fatiga'),
('Pérdida de apetito'),
('Irritabilidad');

-- Relación seguimiento - síntomas
INSERT INTO seguimiento_sintomas (sintoma_id, seguimiento_id) VALUES
(1, 1), -- Palidez en Juan
(2, 1); -- Fatiga en Juan

-- Diagnósticos
INSERT INTO diagnosticos (seguimiento_id, diagnostico, recomendaciones) VALUES
(1, 'Riesgo moderado de anemia', '{"alimentacion": "Incluir más legumbres y espinaca", "suplementos": "Hierro 2 veces por semana"}'),
(2, 'Estado nutricional normal', '{"alimentacion": "Continuar dieta balanceada", "actividad": "Mantener juegos activos"}');

-- Reportes individuales
INSERT INTO reportes_individuales (infante_id, seguimiento_id, nutricionista_id, archivo_url, observaciones) VALUES
(1, 1, 1, '/reportes/juan_ramirez_2025_06_01.pdf', 'Enviar al acudiente vía correo'),
(2, 2, 2, '/reportes/sofia_perez_2025_06_02.pdf', 'Buen estado, no requiere intervención');

-- Alertas
INSERT INTO alertas (infante_id, seguimiento_id, tipo_alerta, mensaje, estado_alerta) VALUES
(1, 1, 'Riesgo de desnutrición', 'Hemoglobina baja detectada', 'pendiente'),
(2, 2, 'Seguimiento próximo', 'Próximo control en 2 meses', 'pendiente');
