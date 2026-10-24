-- Base de datos de validacion: va_biblioteca
-- Sistema de gestion de biblioteca publica y prestamos
-- 8 tablas con COMMENT explicativos, dialecto MySQL 8.4

CREATE DATABASE IF NOT EXISTS `va_biblioteca` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `va_biblioteca`;

DROP TABLE IF EXISTS `sanciones`;
DROP TABLE IF EXISTS `prestamos`;
DROP TABLE IF EXISTS `ejemplares`;
DROP TABLE IF EXISTS `libros`;
DROP TABLE IF EXISTS `autores`;
DROP TABLE IF EXISTS `categorias`;
DROP TABLE IF EXISTS `usuarios`;
DROP TABLE IF EXISTS `empleados`;

CREATE TABLE `categorias` (
  `id_categoria` INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador unico de la categoria',
  `nombre` VARCHAR(50) NOT NULL COMMENT 'Nombre tematico de la categoria',
  `descripcion` VARCHAR(150) DEFAULT NULL COMMENT 'Breve descripcion del area del conocimiento',
  PRIMARY KEY (`id_categoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Categorias tematicas de libros';

CREATE TABLE `autores` (
  `id_autor` INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del autor',
  `nombre` VARCHAR(60) NOT NULL COMMENT 'Nombres del autor',
  `apellido` VARCHAR(60) NOT NULL COMMENT 'Apellidos del autor',
  `nacionalidad` VARCHAR(40) NOT NULL COMMENT 'Pais de origen del autor',
  `anio_nacimiento` INT DEFAULT NULL COMMENT 'Anio de nacimiento del autor',
  PRIMARY KEY (`id_autor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Autores de las obras registradas';

CREATE TABLE `libros` (
  `id_libro` INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del libro',
  `titulo` VARCHAR(120) NOT NULL COMMENT 'Titulo de la obra',
  `isbn` VARCHAR(20) NOT NULL COMMENT 'Codigo ISBN unico',
  `id_autor` INT NOT NULL COMMENT 'Autor principal de la obra',
  `id_categoria` INT NOT NULL COMMENT 'Categoria tematica',
  `anio_publicacion` INT NOT NULL COMMENT 'Anio en que fue publicado',
  `paginas` INT NOT NULL COMMENT 'Numero de paginas',
  `precio_reposicion` DECIMAL(8,2) NOT NULL COMMENT 'Costo en quetzales en caso de extravio',
  PRIMARY KEY (`id_libro`),
  KEY `id_autor` (`id_autor`),
  KEY `id_categoria` (`id_categoria`),
  CONSTRAINT `fk_libros_autor` FOREIGN KEY (`id_autor`) REFERENCES `autores` (`id_autor`),
  CONSTRAINT `fk_libros_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `categorias` (`id_categoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catalogo general de libros';

CREATE TABLE `ejemplares` (
  `id_ejemplar` INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador fisico de la copia',
  `id_libro` INT NOT NULL COMMENT 'Libro al que pertenece esta copia',
  `ubicacion_estante` VARCHAR(20) NOT NULL COMMENT 'Codigo de estante y pasillo',
  `estado_conservacion` VARCHAR(20) NOT NULL COMMENT 'Estado: excelente, bueno, regular o daniado',
  `disponible` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '1 si esta en sala disponible para prestamo, 0 si no',
  PRIMARY KEY (`id_ejemplar`),
  KEY `id_libro` (`id_libro`),
  CONSTRAINT `fk_ejemplares_libro` FOREIGN KEY (`id_libro`) REFERENCES `libros` (`id_libro`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Copias fisicas existentes de cada libro';

CREATE TABLE `usuarios` (
  `id_usuario` INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del lector registrado',
  `nombre` VARCHAR(60) NOT NULL COMMENT 'Nombres del usuario',
  `apellido` VARCHAR(60) NOT NULL COMMENT 'Apellidos del usuario',
  `tipo_usuario` VARCHAR(20) NOT NULL COMMENT 'Tipo: estudiante, docente o general',
  `fecha_registro` DATE NOT NULL COMMENT 'Fecha de afiliacion a la biblioteca',
  `departamento` VARCHAR(40) NOT NULL COMMENT 'Departamento de residencia',
  `activo` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '1 si su carnet esta activo, 0 si suspendido',
  PRIMARY KEY (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Lectores afiliados a la biblioteca';

CREATE TABLE `empleados` (
  `id_empleado` INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del empleado de biblioteca',
  `nombre` VARCHAR(60) NOT NULL COMMENT 'Nombres del empleado',
  `apellido` VARCHAR(60) NOT NULL COMMENT 'Apellidos del empleado',
  `puesto` VARCHAR(40) NOT NULL COMMENT 'Cargo que desempenia',
  `turno` VARCHAR(15) NOT NULL COMMENT 'Turno: matutino, vespertino o nocturno',
  `salario` DECIMAL(10,2) NOT NULL COMMENT 'Sueldo mensual en quetzales',
  PRIMARY KEY (`id_empleado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Personal de atencion de la biblioteca';

CREATE TABLE `prestamos` (
  `id_prestamo` INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del prestamo',
  `id_ejemplar` INT NOT NULL COMMENT 'Copia prestada',
  `id_usuario` INT NOT NULL COMMENT 'Usuario que solicita el libro',
  `id_empleado` INT NOT NULL COMMENT 'Empleado que registro el prestamo',
  `fecha_salida` DATE NOT NULL COMMENT 'Fecha en que se entrego el libro',
  `fecha_limite` DATE NOT NULL COMMENT 'Fecha pactada para devolucion',
  `fecha_devolucion` DATE DEFAULT NULL COMMENT 'Fecha real de retorno, nulo si sigue prestado',
  `estado` VARCHAR(20) NOT NULL COMMENT 'Estado: devuelto, en_curso o retrasado',
  PRIMARY KEY (`id_prestamo`),
  KEY `id_ejemplar` (`id_ejemplar`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_empleado` (`id_empleado`),
  CONSTRAINT `fk_prestamos_ejemplar` FOREIGN KEY (`id_ejemplar`) REFERENCES `ejemplares` (`id_ejemplar`),
  CONSTRAINT `fk_prestamos_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `fk_prestamos_empleado` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Registro de prestamos de libros';

CREATE TABLE `sanciones` (
  `id_sancion` INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la multa o sancion',
  `id_prestamo` INT NOT NULL COMMENT 'Prestamo que origino la infraccion',
  `id_usuario` INT NOT NULL COMMENT 'Usuario sancionado',
  `dias_retraso` INT NOT NULL COMMENT 'Cantidad de dias tarde',
  `monto` DECIMAL(8,2) NOT NULL COMMENT 'Monto de la penalizacion en quetzales',
  `pagada` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '1 si fue cancelada, 0 si tiene deuda pendiente',
  PRIMARY KEY (`id_sancion`),
  KEY `id_prestamo` (`id_prestamo`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `fk_sanciones_prestamo` FOREIGN KEY (`id_prestamo`) REFERENCES `prestamos` (`id_prestamo`),
  CONSTRAINT `fk_sanciones_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Sanciones por atraso o desperfectos';

-- Datos ficticios de prueba (semilla fija y consistente)
INSERT INTO `categorias` (`id_categoria`, `nombre`, `descripcion`) VALUES
(1, 'Literatura', 'Obras clasicas, narrativa, poesia y teatro universal'),
(2, 'Ciencia y Tecnologia', 'Fisica, quimica, computacion, matematicas y biologia'),
(3, 'Historia y Geografia', 'Historia universal y de Guatemala, atlas y geopolitica'),
(4, 'Ciencias Sociales', 'Sociologia, derecho, economia, politica y educacion'),
(5, 'Arte y Filosofia', 'Pintura, musica, arquitectura, estetica y pensamiento filosofico');

INSERT INTO `autores` (`id_autor`, `nombre`, `apellido`, `nacionalidad`, `anio_nacimiento`) VALUES
(1, 'Miguel Angel', 'Asturias', 'Guatemala', 1899),
(2, 'Gabriel', 'Garcia Marquez', 'Colombia', 1927),
(3, 'Mario', 'Vargas Llosa', 'Peru', 1936),
(4, 'Carl', 'Sagan', 'Estados Unidos', 1934),
(5, 'Stephen', 'Hawking', 'Reino Unido', 1942),
(6, 'Yuval Noah', 'Harari', 'Israel', 1976),
(7, 'Severo', 'Martinez Pelaez', 'Guatemala', 1925),
(8, 'Augusto', 'Monterroso', 'Guatemala', 1921);

INSERT INTO `libros` (`id_libro`, `titulo`, `isbn`, `id_autor`, `id_categoria`, `anio_publicacion`, `paginas`, `precio_reposicion`) VALUES
(1, 'El Senor Presidente', '978-8420658421', 1, 1, 1946, 320, 185.50),
(2, 'Hombres de Maiz', '978-8491050728', 1, 1, 1949, 410, 210.00),
(3, 'Cien Anios de Soledad', '978-0307474728', 2, 1, 1967, 471, 230.00),
(4, 'La Fiesta del Chivo', '978-8466333467', 3, 1, 2000, 520, 245.00),
(5, 'Cosmos', '978-0345539434', 4, 2, 1980, 384, 290.00),
(6, 'Breve Historia del Tiempo', '978-8498920444', 5, 2, 1988, 256, 215.00),
(7, 'Sapiens de Animales a Dioses', '978-8499926223', 6, 3, 2014, 496, 260.00),
(8, 'La Patria del Criollo', '978-9992253014', 7, 3, 1970, 780, 310.00),
(9, 'La Oveja Negra y Demas Fabulas', '978-8426402325', 8, 1, 1969, 112, 140.00);

INSERT INTO `ejemplares` (`id_ejemplar`, `id_libro`, `ubicacion_estante`, `estado_conservacion`, `disponible`) VALUES
(1, 1, 'EST-A-01', 'bueno', 1),
(2, 1, 'EST-A-02', 'regular', 0),
(3, 2, 'EST-A-03', 'excelente', 1),
(4, 3, 'EST-A-04', 'bueno', 0),
(5, 3, 'EST-A-05', 'excelente', 1),
(6, 4, 'EST-A-06', 'bueno', 1),
(7, 5, 'EST-B-01', 'excelente', 0),
(8, 5, 'EST-B-02', 'regular', 1),
(9, 6, 'EST-B-03', 'bueno', 1),
(10, 7, 'EST-C-01', 'excelente', 0),
(11, 8, 'EST-C-02', 'bueno', 1),
(12, 9, 'EST-A-07', 'bueno', 1);

INSERT INTO `usuarios` (`id_usuario`, `nombre`, `apellido`, `tipo_usuario`, `fecha_registro`, `departamento`, `activo`) VALUES
(1, 'Carlos', 'Gomez', 'estudiante', '2023-02-10', 'Guatemala', 1),
(2, 'Maria', 'Rodriguez', 'docente', '2023-01-15', 'Sacatepequez', 1),
(3, 'Juan', 'Perez', 'general', '2023-03-22', 'Guatemala', 1),
(4, 'Ana', 'Morales', 'estudiante', '2023-05-18', 'Quetzaltenango', 0),
(5, 'Luis', 'Castillo', 'estudiante', '2023-08-04', 'Escuintla', 1),
(6, 'Sofia', 'Hernandez', 'docente', '2023-09-12', 'Guatemala', 1),
(7, 'David', 'Lopez', 'general', '2024-01-20', 'Chimaltenango', 1),
(8, 'Elena', 'Velasquez', 'estudiante', '2024-02-01', 'Guatemala', 1);

INSERT INTO `empleados` (`id_empleado`, `nombre`, `apellido`, `puesto`, `turno`, `salario`) VALUES
(1, 'Ramiro', 'Alvarez', 'Bibliotecario Jefe', 'matutino', 7500.00),
(2, 'Lucia', 'Fuentes', 'Asistente de Prestamos', 'matutino', 4200.00),
(3, 'Esteban', 'Paz', 'Asistente de Prestamos', 'vespertino', 4200.00),
(4, 'Marta', 'Solorzano', 'Catalogadora', 'matutino', 5600.00);

INSERT INTO `prestamos` (`id_prestamo`, `id_ejemplar`, `id_usuario`, `id_empleado`, `fecha_salida`, `fecha_limite`, `fecha_devolucion`, `estado`) VALUES
(1, 1, 1, 2, '2024-01-10', '2024-01-24', '2024-01-22', 'devuelto'),
(2, 2, 1, 2, '2024-02-01', '2024-02-15', '2024-02-20', 'devuelto'),
(3, 4, 2, 2, '2024-02-10', '2024-02-24', NULL, 'retrasado'),
(4, 7, 3, 3, '2024-02-15', '2024-03-01', NULL, 'en_curso'),
(5, 10, 4, 3, '2024-01-05', '2024-01-19', '2024-01-28', 'devuelto'),
(6, 3, 5, 2, '2024-02-18', '2024-03-03', '2024-03-02', 'devuelto'),
(7, 6, 6, 3, '2024-02-20', '2024-03-05', '2024-03-04', 'devuelto'),
(8, 2, 7, 2, '2024-03-01', '2024-03-15', NULL, 'en_curso'),
(9, 8, 8, 3, '2024-01-12', '2024-01-26', '2024-01-25', 'devuelto'),
(10, 11, 1, 2, '2024-02-25', '2024-03-10', '2024-03-08', 'devuelto');

INSERT INTO `sanciones` (`id_sancion`, `id_prestamo`, `id_usuario`, `dias_retraso`, `monto`, `pagada`) VALUES
(1, 2, 1, 5, 25.00, 1),
(2, 3, 2, 12, 60.00, 0),
(3, 5, 4, 9, 45.00, 0);
