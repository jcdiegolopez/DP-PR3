CREATE TABLE dep (
  dep_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del departamento de la empresa',
  nom_dep VARCHAR(60) NOT NULL COMMENT 'Nombre del departamento',
  ubic VARCHAR(60) NOT NULL COMMENT 'Ubicacion fisica del departamento',
  PRIMARY KEY (dep_id)
) COMMENT='Departamentos de la empresa';

CREATE TABLE pue (
  pue_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del puesto',
  nom_pue VARCHAR(60) NOT NULL COMMENT 'Nombre del puesto',
  sal_min DECIMAL(10,2) NOT NULL COMMENT 'Salario minimo del puesto en quetzales',
  sal_max DECIMAL(10,2) NOT NULL COMMENT 'Salario maximo del puesto en quetzales',
  PRIMARY KEY (pue_id)
) COMMENT='Puestos de trabajo';

CREATE TABLE emp (
  emp_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del empleado',
  nom VARCHAR(60) NOT NULL COMMENT 'Nombres del empleado',
  ape VARCHAR(60) NOT NULL COMMENT 'Apellidos del empleado',
  dpi VARCHAR(15) NOT NULL COMMENT 'DPI del empleado',
  fec_nac DATE NOT NULL COMMENT 'Fecha de nacimiento',
  fec_ing DATE NOT NULL COMMENT 'Fecha de ingreso a la empresa',
  dep_id INT NOT NULL COMMENT 'Departamento donde trabaja',
  pue_id INT NOT NULL COMMENT 'Puesto que ocupa',
  sal_base DECIMAL(10,2) NOT NULL COMMENT 'Salario base mensual en quetzales',
  jefe_id INT COMMENT 'Empleado que es su jefe directo, nulo si no tiene',
  est VARCHAR(10) NOT NULL COMMENT 'Estado: activo o retirado',
  PRIMARY KEY (emp_id),
  FOREIGN KEY (dep_id) REFERENCES dep (dep_id),
  FOREIGN KEY (pue_id) REFERENCES pue (pue_id),
  FOREIGN KEY (jefe_id) REFERENCES emp (emp_id)
) COMMENT='Empleados';

CREATE TABLE pla (
  pla_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del pago de planilla',
  emp_id INT NOT NULL COMMENT 'Empleado al que se paga',
  mes INT NOT NULL COMMENT 'Mes de la planilla, de 1 a 12',
  anio INT NOT NULL COMMENT 'Anio de la planilla',
  sal_dev DECIMAL(10,2) NOT NULL COMMENT 'Salario devengado en quetzales',
  igss DECIMAL(10,2) NOT NULL COMMENT 'Descuento de IGSS en quetzales',
  isr DECIMAL(10,2) NOT NULL COMMENT 'Descuento de impuesto sobre la renta en quetzales',
  bono DECIMAL(10,2) NOT NULL COMMENT 'Bonificaciones del mes en quetzales',
  sal_liq DECIMAL(10,2) NOT NULL COMMENT 'Salario liquido pagado en quetzales',
  PRIMARY KEY (pla_id),
  FOREIGN KEY (emp_id) REFERENCES emp (emp_id)
) COMMENT='Pagos mensuales de planilla';

CREATE TABLE vac (
  vac_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de las vacaciones',
  emp_id INT NOT NULL COMMENT 'Empleado que tomo vacaciones',
  fec_ini DATE NOT NULL COMMENT 'Primer dia de vacaciones',
  fec_fin DATE NOT NULL COMMENT 'Ultimo dia de vacaciones',
  dias INT NOT NULL COMMENT 'Dias habiles tomados',
  PRIMARY KEY (vac_id),
  FOREIGN KEY (emp_id) REFERENCES emp (emp_id)
) COMMENT='Periodos de vacaciones';

CREATE TABLE aus (
  aus_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la ausencia',
  emp_id INT NOT NULL COMMENT 'Empleado que falto',
  fec_aus DATE NOT NULL COMMENT 'Fecha de la ausencia',
  mot VARCHAR(40) NOT NULL COMMENT 'Motivo: enfermedad, personal o sin aviso',
  justif TINYINT(1) NOT NULL COMMENT '1 si la ausencia fue justificada, 0 si no',
  PRIMARY KEY (aus_id),
  FOREIGN KEY (emp_id) REFERENCES emp (emp_id)
) COMMENT='Ausencias de los empleados';

CREATE TABLE eva (
  eva_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la evaluacion',
  emp_id INT NOT NULL COMMENT 'Empleado evaluado',
  anio INT NOT NULL COMMENT 'Anio de la evaluacion',
  punt DECIMAL(4,1) NOT NULL COMMENT 'Puntaje de 0 a 100',
  PRIMARY KEY (eva_id),
  FOREIGN KEY (emp_id) REFERENCES emp (emp_id)
) COMMENT='Evaluaciones de desempeno anuales';

CREATE TABLE cap (
  cap_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la capacitacion',
  nom_cap VARCHAR(80) NOT NULL COMMENT 'Nombre de la capacitacion',
  fec_cap DATE NOT NULL COMMENT 'Fecha en que se imparte',
  hrs INT NOT NULL COMMENT 'Horas de duracion',
  PRIMARY KEY (cap_id)
) COMMENT='Capacitaciones internas';

CREATE TABLE emp_cap (
  emp_id INT NOT NULL COMMENT 'Empleado que asistio',
  cap_id INT NOT NULL COMMENT 'Capacitacion a la que asistio',
  PRIMARY KEY (emp_id, cap_id),
  FOREIGN KEY (emp_id) REFERENCES emp (emp_id),
  FOREIGN KEY (cap_id) REFERENCES cap (cap_id)
) COMMENT='Asistencia de empleados a capacitaciones';
