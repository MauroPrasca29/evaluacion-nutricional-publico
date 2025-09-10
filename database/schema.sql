-- Base de datos: Sistema de evaluación nutricional 

-- Elimina tablas si existen (para evitar errores al ejecutar varias veces)
DROP TABLE IF EXISTS reportes_individuales CASCADE;
DROP TABLE IF EXISTS diagnosticos CASCADE;
DROP TABLE IF EXISTS alertas CASCADE;
DROP TABLE IF EXISTS seguimiento_sintomas CASCADE;
DROP TABLE IF EXISTS examenes CASCADE;
DROP TABLE IF EXISTS datos_antropometricos CASCADE;
DROP TABLE IF EXISTS seguimientos CASCADE;
DROP TABLE IF EXISTS infantes CASCADE;
DROP TABLE IF EXISTS acudientes CASCADE;
DROP TABLE IF EXISTS sedes CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;
DROP TABLE IF EXISTS roles CASCADE;
DROP TABLE IF EXISTS sintomas CASCADE;

-- Tabla de roles
CREATE TABLE roles(
	id_rol SERIAL PRIMARY KEY,
	nombre VARCHAR(100) UNIQUE NOT NULL,
	descripcion TEXT
);

-- Tabla de usuarios
CREATE TABLE usuarios(
	id_usuario SERIAL PRIMARY KEY,
	nombre VARCHAR(150) NOT NULL ,
	correo VARCHAR(50) UNIQUE NOT NULL,
	telefono VARCHAR(20) UNIQUE NOT NULL,
	rol_id INT REFERENCES roles(id_rol),
	contrasena TEXT NOT NULL,
	fecha_creado TIMESTAMP DEFAULT Now(),
	fecha_actualizado TIMESTAMP DEFAULT Now() 	
);

-- Tabla de sedes
CREATE TABLE sedes (
    id_sede SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    municipio VARCHAR(100),
    departamento VARCHAR(100),
    telefono VARCHAR(20)
);

-- Tabla de acudientes
CREATE TABLE acudientes (
    id_acudiente SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(100),
    direccion TEXT,
    fecha_creado TIMESTAMP DEFAULT Now(),
    fecha_actualizado TIMESTAMP DEFAULT Now()
);

-- Tabla de infantes
CREATE TABLE infantes(
	id_infante SERIAL PRIMARY KEY,
	nombre VARCHAR(100) NOT NULL,
	fecha_nacimiento DATE NOT NULL CHECK(fecha_nacimiento <= CURRENT_DATE),
	genero VARCHAR(10) NOT NULL,
    acudiente_id INT REFERENCES acudientes(id_acudiente) ON DELETE SET NULL,
    sede_id INT REFERENCES sedes(id_sede) ON DELETE SET NULL,
	fecha_creado TIMESTAMP DEFAULT Now(),
	fecha_actualizado TIMESTAMP DEFAULT Now()
);

-- Tabla de seguimientos
CREATE TABLE seguimientos(
	id_seguimiento SERIAL PRIMARY KEY,
	infante_id INT REFERENCES infantes(id_infante) ON DELETE CASCADE,
	encargado_id INT REFERENCES usuarios(id_usuario),
	fecha DATE NOT NULL,
	observacion TEXT
);

-- Tabla de datos antropometricos
CREATE TABLE datos_antropometricos(
	id_dato SERIAL PRIMARY KEY,
	seguimiento_id INT REFERENCES seguimientos(id_seguimiento) ON DELETE CASCADE,
	peso DECIMAL(5,2) NOT NULL CHECK (peso > 0),
	estatura DECIMAL(5,2) NOT NULL CHECK (estatura > 0),
    imc DECIMAL(5,2),
	circunferencia_braquial DECIMAL (5,2) CHECK (circunferencia_braquial > 0),
	perimetro_cefalico DECIMAL (5,2) CHECK (perimetro_cefalico > 0),
	pliegue_cutaneo DECIMAL (5,2) CHECK (pliegue_cutaneo > 0),
	perimetro_abdominal DECIMAL (5,2) CHECK (perimetro_abdominal > 0)
);

-- Tabla de examenes
CREATE TABLE examenes(
	id_examenes SERIAL PRIMARY KEY,
	seguimiento_id INT REFERENCES seguimientos(id_seguimiento) ON DELETE CASCADE,
	hemoglobina DECIMAL (5,2)
);

-- Tabla de sintomas
CREATE TABLE sintomas(
	id_sintoma SERIAL PRIMARY KEY,
	nombre VARCHAR (100) UNIQUE NOT NULL
);

-- Tabla de relación entre seguimiento y sintomas
CREATE TABLE seguimiento_sintomas (
	sintoma_id INT REFERENCES sintomas(id_sintoma) ON DELETE CASCADE,
	seguimiento_id INT REFERENCES seguimientos(id_seguimiento) ON DELETE CASCADE,
	PRIMARY KEY(sintoma_id, seguimiento_id)
);

-- Tabla de diagnosticos
CREATE TABLE diagnosticos (
    id_diagnostico SERIAL PRIMARY KEY,
    seguimiento_id INT REFERENCES seguimientos(id_seguimiento) ON DELETE CASCADE,
    diagnostico TEXT NOT NULL,
    recomendaciones JSONB,
    fecha_generado TIMESTAMP DEFAULT NOW()
);

-- Tabla de reportes
CREATE TABLE reportes_individuales (
    id_reporte SERIAL PRIMARY KEY,
    infante_id INT REFERENCES infantes(id_infante) ON DELETE CASCADE,
    seguimiento_id INT REFERENCES seguimientos(id_seguimiento) ON DELETE CASCADE,
    nutricionista_id INT REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    fecha_reporte TIMESTAMP DEFAULT NOW(),
    archivo_url TEXT,    
    observaciones TEXT
);

-- Tabla de alertas
CREATE TABLE alertas (
    id_alerta SERIAL PRIMARY KEY,
    infante_id INT REFERENCES infantes(id_infante) ON DELETE CASCADE,
    seguimiento_id INT REFERENCES seguimientos(id_seguimiento),
    tipo_alerta VARCHAR(100) NOT NULL, -- Ej: Riesgo de desnutrición, Seguimiento vencido
    mensaje TEXT NOT NULL,
    estado_alerta VARCHAR(20) DEFAULT 'pendiente', -- pendiente, resuelta
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_resuelta TIMESTAMP
);

-- Indices
CREATE UNIQUE INDEX idx_usuarios_correo ON usuarios(correo);
CREATE UNIQUE INDEX idx_usuarios_telefono ON usuarios(telefono);
CREATE INDEX idx_infantes_nombre ON infantes(nombre);
CREATE INDEX idx_infantes_genero ON infantes(genero);
CREATE INDEX idx_infantes_acudiente ON infantes(acudiente_id);
CREATE INDEX idx_seguimientos_infante ON seguimientos(infante_id);
CREATE INDEX idx_seguimientos_encargado ON seguimientos(encargado_id);
CREATE INDEX idx_seguimientos_fecha ON seguimientos(fecha);
CREATE INDEX idx_datos_antropometricos_seguimiento ON datos_antropometricos(seguimiento_id);
CREATE INDEX idx_examenes_seguimiento ON examenes(seguimiento_id);
CREATE UNIQUE INDEX idx_sintomas_nombre ON sintomas(nombre);
CREATE INDEX idx_seguimiento_sintomas_seguimiento ON seguimiento_sintomas(seguimiento_id);
CREATE INDEX idx_seguimiento_sintomas_sintoma ON seguimiento_sintomas(sintoma_id);


-- Triggers
CREATE OR REPLACE FUNCTION calcular_imc()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.estatura > 0 THEN
    NEW.imc := NEW.peso / ((NEW.estatura/100) * (NEW.estatura/100));
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_calcular_imc BEFORE INSERT OR UPDATE ON datos_antropometricos FOR EACH ROW EXECUTE FUNCTION calcular_imc();

