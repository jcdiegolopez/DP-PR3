CREATE TABLE facultades (
  id_facultad INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la facultad',
  nombre VARCHAR(80) NOT NULL COMMENT 'Nombre de la facultad',
  PRIMARY KEY (id_facultad)
) COMMENT='Facultades de la universidad';

CREATE TABLE carreras (
  id_carrera INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la carrera',
  nombre VARCHAR(100) NOT NULL COMMENT 'Nombre de la carrera',
  id_facultad INT NOT NULL COMMENT 'Facultad a la que pertenece',
  duracion_semestres INT NOT NULL COMMENT 'Duracion de la carrera en semestres',
  PRIMARY KEY (id_carrera),
  FOREIGN KEY (id_facultad) REFERENCES facultades (id_facultad)
) COMMENT='Carreras que se ofrecen';

CREATE TABLE catedraticos (
  id_catedratico INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del catedratico',
  nombre VARCHAR(60) NOT NULL COMMENT 'Nombres del catedratico',
  apellido VARCHAR(60) NOT NULL COMMENT 'Apellidos del catedratico',
  id_facultad INT NOT NULL COMMENT 'Facultad a la que esta asignado',
  grado_academico VARCHAR(30) NOT NULL COMMENT 'Grado mas alto: licenciatura, maestria o doctorado',
  fecha_ingreso DATE NOT NULL COMMENT 'Fecha en que ingreso a la universidad',
  PRIMARY KEY (id_catedratico),
  FOREIGN KEY (id_facultad) REFERENCES facultades (id_facultad)
) COMMENT='Docentes de la universidad';

CREATE TABLE estudiantes (
  id_estudiante INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador interno del estudiante',
  carne VARCHAR(10) NOT NULL COMMENT 'Carne del estudiante',
  nombre VARCHAR(60) NOT NULL COMMENT 'Nombres del estudiante',
  apellido VARCHAR(60) NOT NULL COMMENT 'Apellidos del estudiante',
  id_carrera INT NOT NULL COMMENT 'Carrera que cursa',
  fecha_ingreso DATE NOT NULL COMMENT 'Fecha de ingreso a la universidad',
  genero CHAR(1) NOT NULL COMMENT 'M masculino o F femenino',
  departamento_origen VARCHAR(40) COMMENT 'Departamento de Guatemala de donde proviene',
  PRIMARY KEY (id_estudiante),
  FOREIGN KEY (id_carrera) REFERENCES carreras (id_carrera)
) COMMENT='Estudiantes inscritos en la universidad';

CREATE TABLE cursos (
  id_curso INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del curso',
  codigo VARCHAR(10) NOT NULL COMMENT 'Codigo del curso',
  nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del curso',
  creditos INT NOT NULL COMMENT 'Creditos que otorga el curso',
  id_carrera INT NOT NULL COMMENT 'Carrera a la que pertenece el curso',
  PRIMARY KEY (id_curso),
  FOREIGN KEY (id_carrera) REFERENCES carreras (id_carrera)
) COMMENT='Cursos del pensum';

CREATE TABLE ciclos (
  id_ciclo INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del ciclo academico',
  anio INT NOT NULL COMMENT 'Anio del ciclo',
  numero INT NOT NULL COMMENT 'Numero de ciclo dentro del anio: 1 o 2',
  fecha_inicio DATE NOT NULL COMMENT 'Fecha de inicio del ciclo',
  fecha_fin DATE NOT NULL COMMENT 'Fecha de fin del ciclo',
  PRIMARY KEY (id_ciclo)
) COMMENT='Ciclos academicos';

CREATE TABLE secciones (
  id_seccion INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la seccion',
  id_curso INT NOT NULL COMMENT 'Curso que se imparte',
  id_ciclo INT NOT NULL COMMENT 'Ciclo en que se imparte',
  id_catedratico INT NOT NULL COMMENT 'Catedratico que la imparte',
  cupo INT NOT NULL COMMENT 'Cupo maximo de estudiantes',
  aula VARCHAR(20) COMMENT 'Aula asignada',
  PRIMARY KEY (id_seccion),
  FOREIGN KEY (id_curso) REFERENCES cursos (id_curso),
  FOREIGN KEY (id_ciclo) REFERENCES ciclos (id_ciclo),
  FOREIGN KEY (id_catedratico) REFERENCES catedraticos (id_catedratico)
) COMMENT='Secciones abiertas de cada curso en cada ciclo';

CREATE TABLE inscripciones (
  id_inscripcion INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la inscripcion',
  id_estudiante INT NOT NULL COMMENT 'Estudiante inscrito',
  id_seccion INT NOT NULL COMMENT 'Seccion en la que se inscribio',
  fecha_inscripcion DATE NOT NULL COMMENT 'Fecha de la inscripcion',
  nota DECIMAL(5,2) COMMENT 'Nota final de 0 a 100, nula si el curso esta en progreso',
  estado VARCHAR(15) NOT NULL COMMENT 'Estado: aprobado, reprobado o en_curso',
  PRIMARY KEY (id_inscripcion),
  FOREIGN KEY (id_estudiante) REFERENCES estudiantes (id_estudiante),
  FOREIGN KEY (id_seccion) REFERENCES secciones (id_seccion)
) COMMENT='Inscripciones de estudiantes a secciones';
