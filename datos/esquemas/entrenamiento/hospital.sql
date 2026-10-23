CREATE TABLE especialidades (
  id_especialidad INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la especialidad',
  nombre VARCHAR(60) NOT NULL COMMENT 'Nombre de la especialidad medica',
  PRIMARY KEY (id_especialidad)
) COMMENT='Especialidades medicas del hospital';

CREATE TABLE medicos (
  id_medico INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del medico',
  nombre VARCHAR(60) NOT NULL COMMENT 'Nombres del medico',
  apellido VARCHAR(60) NOT NULL COMMENT 'Apellidos del medico',
  id_especialidad INT NOT NULL COMMENT 'Especialidad del medico',
  colegiado VARCHAR(10) NOT NULL COMMENT 'Numero de colegiado activo',
  fecha_contratacion DATE NOT NULL COMMENT 'Fecha de contratacion',
  salario DECIMAL(10,2) NOT NULL COMMENT 'Salario mensual en quetzales',
  PRIMARY KEY (id_medico),
  FOREIGN KEY (id_especialidad) REFERENCES especialidades (id_especialidad)
) COMMENT='Medicos del hospital';

CREATE TABLE pacientes (
  id_paciente INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del paciente',
  nombre VARCHAR(60) NOT NULL COMMENT 'Nombres del paciente',
  apellido VARCHAR(60) NOT NULL COMMENT 'Apellidos del paciente',
  fecha_nacimiento DATE NOT NULL COMMENT 'Fecha de nacimiento',
  genero CHAR(1) NOT NULL COMMENT 'M masculino o F femenino',
  departamento VARCHAR(40) COMMENT 'Departamento de residencia',
  telefono VARCHAR(15) COMMENT 'Telefono de contacto',
  tipo_sangre VARCHAR(3) COMMENT 'Tipo de sangre, por ejemplo O+ o AB-',
  afiliado_seguro TINYINT(1) NOT NULL DEFAULT 0 COMMENT '1 si esta afiliado al seguro social, 0 si no',
  PRIMARY KEY (id_paciente)
) COMMENT='Pacientes registrados';

CREATE TABLE consultorios (
  id_consultorio INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del consultorio',
  nombre VARCHAR(40) NOT NULL COMMENT 'Nombre o numero del consultorio',
  piso INT NOT NULL COMMENT 'Piso del edificio donde esta',
  PRIMARY KEY (id_consultorio)
) COMMENT='Consultorios disponibles';

CREATE TABLE citas (
  id_cita INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la cita',
  id_paciente INT NOT NULL COMMENT 'Paciente atendido',
  id_medico INT NOT NULL COMMENT 'Medico que atiende',
  id_consultorio INT NOT NULL COMMENT 'Consultorio asignado',
  fecha_hora DATETIME NOT NULL COMMENT 'Fecha y hora de la cita',
  motivo VARCHAR(120) COMMENT 'Motivo de la consulta',
  estado VARCHAR(15) NOT NULL COMMENT 'Estado: atendida, cancelada o pendiente',
  costo DECIMAL(8,2) NOT NULL COMMENT 'Costo de la consulta en quetzales',
  PRIMARY KEY (id_cita),
  FOREIGN KEY (id_paciente) REFERENCES pacientes (id_paciente),
  FOREIGN KEY (id_medico) REFERENCES medicos (id_medico),
  FOREIGN KEY (id_consultorio) REFERENCES consultorios (id_consultorio)
) COMMENT='Citas medicas';

CREATE TABLE diagnosticos (
  id_diagnostico INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del diagnostico',
  id_cita INT NOT NULL COMMENT 'Cita en la que se emitio',
  codigo_cie10 VARCHAR(8) NOT NULL COMMENT 'Codigo CIE-10 del diagnostico',
  descripcion VARCHAR(150) NOT NULL COMMENT 'Descripcion del diagnostico',
  gravedad VARCHAR(10) NOT NULL COMMENT 'Gravedad: leve, moderada o grave',
  PRIMARY KEY (id_diagnostico),
  FOREIGN KEY (id_cita) REFERENCES citas (id_cita)
) COMMENT='Diagnosticos emitidos en las citas';

CREATE TABLE medicamentos (
  id_medicamento INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del medicamento',
  nombre VARCHAR(80) NOT NULL COMMENT 'Nombre del medicamento',
  laboratorio VARCHAR(80) COMMENT 'Laboratorio que lo fabrica',
  precio DECIMAL(8,2) NOT NULL COMMENT 'Precio por unidad en quetzales',
  PRIMARY KEY (id_medicamento)
) COMMENT='Medicamentos disponibles';

CREATE TABLE recetas (
  id_receta INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la receta',
  id_cita INT NOT NULL COMMENT 'Cita en la que se receto',
  id_medicamento INT NOT NULL COMMENT 'Medicamento recetado',
  dosis VARCHAR(60) NOT NULL COMMENT 'Indicacion de dosis',
  dias_tratamiento INT NOT NULL COMMENT 'Dias que dura el tratamiento',
  PRIMARY KEY (id_receta),
  FOREIGN KEY (id_cita) REFERENCES citas (id_cita),
  FOREIGN KEY (id_medicamento) REFERENCES medicamentos (id_medicamento)
) COMMENT='Medicamentos recetados en cada cita';

CREATE TABLE hospitalizaciones (
  id_hospitalizacion INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la hospitalizacion',
  id_paciente INT NOT NULL COMMENT 'Paciente hospitalizado',
  id_medico INT NOT NULL COMMENT 'Medico responsable',
  fecha_ingreso DATE NOT NULL COMMENT 'Fecha de ingreso',
  fecha_egreso DATE COMMENT 'Fecha de egreso, nula si sigue hospitalizado',
  habitacion VARCHAR(10) NOT NULL COMMENT 'Habitacion asignada',
  costo_total DECIMAL(12,2) COMMENT 'Costo total en quetzales, nulo mientras no se de egreso',
  PRIMARY KEY (id_hospitalizacion),
  FOREIGN KEY (id_paciente) REFERENCES pacientes (id_paciente),
  FOREIGN KEY (id_medico) REFERENCES medicos (id_medico)
) COMMENT='Hospitalizaciones';
