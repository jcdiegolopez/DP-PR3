-- Base de datos de validacion: va_gimnasio
-- Sistema de gestion de centro deportivo, entrenamientos, clases y membresias
-- 8 tablas con COMMENT explicativos, dialecto MySQL 8.4

CREATE DATABASE IF NOT EXISTS `va_gimnasio` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `va_gimnasio`;

DROP TABLE IF EXISTS `medidas_corporales`;
DROP TABLE IF EXISTS `asistencias`;
DROP TABLE IF EXISTS `inscripciones_clases`;
DROP TABLE IF EXISTS `pagos`;
DROP TABLE IF EXISTS `clases`;
DROP TABLE IF EXISTS `miembros`;
DROP TABLE IF EXISTS `planes`;
DROP TABLE IF EXISTS `instructores`;

CREATE TABLE `planes` (
  `id_plan` INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del plan de membresia',
  `nombre` VARCHAR(50) NOT NULL COMMENT 'Nombre comercial del plan',
  `duracion_meses` INT NOT NULL COMMENT 'Periodo de vigencia en meses',
  `precio_mensual` DECIMAL(8,2) NOT NULL COMMENT 'Cuota mensual en quetzales',
  `incluye_pesas` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '1 si permite acceso al area de pesas, 0 si no',
  `incluye_piscina` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '1 si incluye acceso al area humeda y piscina, 0 si no',
  PRIMARY KEY (`id_plan`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Planes y suscripciones ofrecidas';

CREATE TABLE `instructores` (
  `id_instructor` INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del entrenador',
  `nombre` VARCHAR(60) NOT NULL COMMENT 'Nombres del entrenador',
  `apellido` VARCHAR(60) NOT NULL COMMENT 'Apellidos del entrenador',
  `especialidad` VARCHAR(50) NOT NULL COMMENT 'Disciplina principal: crossfit, spinning, pesas o yoga',
  `fecha_contratacion` DATE NOT NULL COMMENT 'Fecha de ingreso al staff',
  `salario_base` DECIMAL(10,2) NOT NULL COMMENT 'Salario fijo mensual en quetzales',
  PRIMARY KEY (`id_instructor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Instructores y entrenadores del gimnasio';

CREATE TABLE `miembros` (
  `id_miembro` INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador unico del cliente o socio',
  `nombre` VARCHAR(60) NOT NULL COMMENT 'Nombres del socio',
  `apellido` VARCHAR(60) NOT NULL COMMENT 'Apellidos del socio',
  `fecha_nacimiento` DATE NOT NULL COMMENT 'Fecha de natalicio',
  `genero` CHAR(1) NOT NULL COMMENT 'M masculino o F femenino',
  `id_plan` INT NOT NULL COMMENT 'Plan contratado actualmente',
  `fecha_inscripcion` DATE NOT NULL COMMENT 'Fecha de alta como miembro',
  `estado_membresia` VARCHAR(15) NOT NULL COMMENT 'Estado: activo, vencido o cancelado',
  PRIMARY KEY (`id_miembro`),
  KEY `id_plan` (`id_plan`),
  CONSTRAINT `fk_miembros_plan` FOREIGN KEY (`id_plan`) REFERENCES `planes` (`id_plan`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Socios afiliados al centro deportivo';

CREATE TABLE `clases` (
  `id_clase` INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la sesion grupal',
  `nombre_clase` VARCHAR(60) NOT NULL COMMENT 'Nombre de la clase grupal',
  `id_instructor` INT NOT NULL COMMENT 'Instructor responsable',
  `dia_semana` VARCHAR(15) NOT NULL COMMENT 'Dia en que se imparte: lunes a sabado',
  `hora_inicio` TIME NOT NULL COMMENT 'Horario de inicio',
  `capacidad_maxima` INT NOT NULL COMMENT 'Cupo maximo de participantes',
  PRIMARY KEY (`id_clase`),
  KEY `id_instructor` (`id_instructor`),
  CONSTRAINT `fk_clases_instructor` FOREIGN KEY (`id_instructor`) REFERENCES `instructores` (`id_instructor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Clases grupales programadas';

CREATE TABLE `pagos` (
  `id_pago` INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la transaccion de pago',
  `id_miembro` INT NOT NULL COMMENT 'Socio que realiza el desembolso',
  `fecha_pago` DATE NOT NULL COMMENT 'Fecha en que se liquido la cuota',
  `monto` DECIMAL(8,2) NOT NULL COMMENT 'Monto abonado en quetzales',
  `metodo_pago` VARCHAR(25) NOT NULL COMMENT 'Metodo: tarjeta, efectivo o transferencia',
  `mes_cubierto` VARCHAR(20) NOT NULL COMMENT 'Periodo mensual facturado por ejemplo 2024-02',
  PRIMARY KEY (`id_pago`),
  KEY `id_miembro` (`id_miembro`),
  CONSTRAINT `fk_pagos_miembro` FOREIGN KEY (`id_miembro`) REFERENCES `miembros` (`id_miembro`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Pagos de cuotas y mensualidades';

CREATE TABLE `inscripciones_clases` (
  `id_inscripcion` INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del registro de asistencia a clase',
  `id_clase` INT NOT NULL COMMENT 'Clase reservada',
  `id_miembro` INT NOT NULL COMMENT 'Socio que reserva lugar',
  `fecha_reserva` DATE NOT NULL COMMENT 'Fecha en que solicito su cupo',
  `asistio` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '1 si acudio a la sesion, 0 si falto',
  PRIMARY KEY (`id_inscripcion`),
  KEY `id_clase` (`id_clase`),
  KEY `id_miembro` (`id_miembro`),
  CONSTRAINT `fk_insc_clase` FOREIGN KEY (`id_clase`) REFERENCES `clases` (`id_clase`),
  CONSTRAINT `fk_insc_miembro` FOREIGN KEY (`id_miembro`) REFERENCES `miembros` (`id_miembro`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Reservas de cupos para clases grupales';

CREATE TABLE `asistencias` (
  `id_asistencia` INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del registro de entrada por molinete',
  `id_miembro` INT NOT NULL COMMENT 'Socio que ingreso a la sede',
  `fecha_hora_ingreso` DATETIME NOT NULL COMMENT 'Marca temporal de entrada al edificio',
  PRIMARY KEY (`id_asistencia`),
  KEY `id_miembro` (`id_miembro`),
  CONSTRAINT `fk_asistencias_miembro` FOREIGN KEY (`id_miembro`) REFERENCES `miembros` (`id_miembro`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Bitacora de accesos fisicos al gimnasio';

CREATE TABLE `medidas_corporales` (
  `id_medida` INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la evaluacion fisica',
  `id_miembro` INT NOT NULL COMMENT 'Socio evaluado',
  `fecha_evaluacion` DATE NOT NULL COMMENT 'Fecha de la medicion antropometrica',
  `peso_kg` DECIMAL(5,2) NOT NULL COMMENT 'Peso corporal en kilogramos',
  `estatura_cm` DECIMAL(5,2) NOT NULL COMMENT 'Estatura en centimetros',
  `porcentaje_grasa` DECIMAL(4,1) DEFAULT NULL COMMENT 'Porcentaje de tejido adiposo',
  `masa_muscular_kg` DECIMAL(4,1) DEFAULT NULL COMMENT 'Masa muscular estimada en kilogramos',
  PRIMARY KEY (`id_medida`),
  KEY `id_miembro` (`id_miembro`),
  CONSTRAINT `fk_medidas_miembro` FOREIGN KEY (`id_miembro`) REFERENCES `miembros` (`id_miembro`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Evaluaciones de composicion corporal';

-- Datos ficticios de prueba (semilla fija y consistente)
INSERT INTO `planes` (`id_plan`, `nombre`, `duracion_meses`, `precio_mensual`, `incluye_pesas`, `incluye_piscina`) VALUES
(1, 'Basico Fit', 1, 250.00, 1, 0),
(2, 'Pro Cardio y Pesas', 6, 320.00, 1, 0),
(3, 'Elite Total', 12, 450.00, 1, 1),
(4, 'Estudiante', 1, 190.00, 1, 0);

INSERT INTO `instructores` (`id_instructor`, `nombre`, `apellido`, `especialidad`, `fecha_contratacion`, `salario_base`) VALUES
(1, 'Alejandro', 'Mendez', 'crossfit', '2022-03-01', 5200.00),
(2, 'Valeria', 'Castillo', 'spinning', '2022-07-15', 4800.00),
(3, 'Ricardo', 'Navarro', 'pesas', '2021-11-10', 5500.00),
(4, 'Camila', 'Rios', 'yoga', '2023-01-20', 4600.00);

INSERT INTO `miembros` (`id_miembro`, `nombre`, `apellido`, `fecha_nacimiento`, `genero`, `id_plan`, `fecha_inscripcion`, `estado_membresia`) VALUES
(1, 'Fernando', 'Guzman', '1995-04-12', 'M', 2, '2023-01-10', 'activo'),
(2, 'Gabriela', 'Pineda', '1998-09-25', 'F', 3, '2023-02-14', 'activo'),
(3, 'Jorge', 'Estrada', '1987-11-03', 'M', 1, '2023-03-05', 'vencido'),
(4, 'Daniela', 'Barrios', '2002-06-18', 'F', 4, '2023-04-22', 'activo'),
(5, 'Manuel', 'Salazar', '1991-01-30', 'M', 2, '2023-06-11', 'activo'),
(6, 'Paola', 'Cruz', '1996-08-14', 'F', 3, '2023-08-01', 'activo'),
(7, 'Andres', 'Fuentes', '1984-12-05', 'M', 1, '2023-10-15', 'cancelado'),
(8, 'Mariana', 'Ortiz', '2001-03-29', 'F', 4, '2024-01-08', 'activo');

INSERT INTO `clases` (`id_clase`, `nombre_clase`, `id_instructor`, `dia_semana`, `hora_inicio`, `capacidad_maxima`) VALUES
(1, 'Spinning Matutino', 2, 'lunes', '06:30:00', 20),
(2, 'Crossfit WOD', 1, 'martes', '07:00:00', 15),
(3, 'Yoga Flow', 4, 'miercoles', '08:00:00', 18),
(4, 'Spinning Nocturno', 2, 'jueves', '18:30:00', 20),
(5, 'Powerlifting Tecnico', 3, 'viernes', '17:00:00', 12);

INSERT INTO `pagos` (`id_pago`, `id_miembro`, `fecha_pago`, `monto`, `metodo_pago`, `mes_cubierto`) VALUES
(1, 1, '2024-01-05', 320.00, 'tarjeta', '2024-01'),
(2, 2, '2024-01-06', 450.00, 'transferencia', '2024-01'),
(3, 4, '2024-01-10', 190.00, 'efectivo', '2024-01'),
(4, 5, '2024-01-12', 320.00, 'tarjeta', '2024-01'),
(5, 6, '2024-01-15', 450.00, 'tarjeta', '2024-01'),
(6, 1, '2024-02-04', 320.00, 'tarjeta', '2024-02'),
(7, 2, '2024-02-06', 450.00, 'transferencia', '2024-02'),
(8, 4, '2024-02-09', 190.00, 'efectivo', '2024-02'),
(9, 6, '2024-02-14', 450.00, 'tarjeta', '2024-02'),
(10, 8, '2024-01-08', 190.00, 'efectivo', '2024-01');

INSERT INTO `inscripciones_clases` (`id_inscripcion`, `id_clase`, `id_miembro`, `fecha_reserva`, `asistio`) VALUES
(1, 1, 1, '2024-01-14', 1),
(2, 1, 2, '2024-01-14', 1),
(3, 2, 1, '2024-01-15', 1),
(4, 2, 5, '2024-01-15', 0),
(5, 3, 2, '2024-01-16', 1),
(6, 3, 6, '2024-01-16', 1),
(7, 4, 1, '2024-01-17', 1),
(8, 5, 5, '2024-01-18', 1),
(9, 1, 6, '2024-01-21', 1),
(10, 3, 4, '2024-01-23', 0);

INSERT INTO `asistencias` (`id_asistencia`, `id_miembro`, `fecha_hora_ingreso`) VALUES
(1, 1, '2024-01-15 06:20:00'),
(2, 2, '2024-01-15 06:25:00'),
(3, 5, '2024-01-15 17:30:00'),
(4, 1, '2024-01-16 06:55:00'),
(5, 4, '2024-01-16 16:10:00'),
(6, 6, '2024-01-17 07:50:00'),
(7, 1, '2024-01-18 18:20:00'),
(8, 2, '2024-01-19 08:00:00'),
(9, 5, '2024-01-19 16:45:00'),
(10, 8, '2024-01-20 09:30:00');

INSERT INTO `medidas_corporales` (`id_medida`, `id_miembro`, `fecha_evaluacion`, `peso_kg`, `estatura_cm`, `porcentaje_grasa`, `masa_muscular_kg`) VALUES
(1, 1, '2023-01-10', 78.50, 175.00, 22.4, 34.2),
(2, 1, '2023-07-12', 75.20, 175.00, 18.6, 36.5),
(3, 2, '2023-02-14', 62.00, 163.00, 26.5, 23.8),
(4, 2, '2023-08-16', 59.40, 163.00, 23.1, 25.0),
(5, 5, '2023-06-11', 88.00, 180.00, 24.8, 38.0),
(6, 6, '2023-08-01', 65.50, 168.00, 27.2, 24.5);
