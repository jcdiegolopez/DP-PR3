CREATE TABLE agencias (
  id_agencia INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la agencia',
  nombre VARCHAR(80) NOT NULL COMMENT 'Nombre de la agencia',
  departamento VARCHAR(40) NOT NULL COMMENT 'Departamento donde esta ubicada',
  municipio VARCHAR(60) NOT NULL COMMENT 'Municipio donde esta ubicada',
  fecha_apertura DATE NOT NULL COMMENT 'Fecha en que abrio la agencia',
  PRIMARY KEY (id_agencia)
) COMMENT='Agencias del banco';

CREATE TABLE clientes (
  id_cliente INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del cliente',
  dpi VARCHAR(15) NOT NULL COMMENT 'Documento personal de identificacion',
  nombre VARCHAR(60) NOT NULL COMMENT 'Nombres del cliente',
  apellido VARCHAR(60) NOT NULL COMMENT 'Apellidos del cliente',
  fecha_nacimiento DATE NOT NULL COMMENT 'Fecha de nacimiento',
  ocupacion VARCHAR(60) COMMENT 'Ocupacion declarada',
  id_agencia INT NOT NULL COMMENT 'Agencia donde abrio su relacion con el banco',
  fecha_alta DATE NOT NULL COMMENT 'Fecha en que se hizo cliente',
  PRIMARY KEY (id_cliente),
  FOREIGN KEY (id_agencia) REFERENCES agencias (id_agencia)
) COMMENT='Clientes del banco';

CREATE TABLE tipos_cuenta (
  id_tipo INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del tipo de cuenta',
  nombre VARCHAR(40) NOT NULL COMMENT 'Nombre: ahorro, monetaria o plazo fijo',
  tasa_interes_anual DECIMAL(5,2) NOT NULL COMMENT 'Tasa de interes anual en porcentaje',
  cuota_manejo DECIMAL(8,2) NOT NULL COMMENT 'Cuota mensual de manejo en quetzales',
  PRIMARY KEY (id_tipo)
) COMMENT='Tipos de cuenta que ofrece el banco';

CREATE TABLE cuentas (
  id_cuenta INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la cuenta',
  numero_cuenta VARCHAR(20) NOT NULL COMMENT 'Numero de cuenta visible para el cliente',
  id_cliente INT NOT NULL COMMENT 'Titular de la cuenta',
  id_tipo INT NOT NULL COMMENT 'Tipo de cuenta',
  saldo DECIMAL(14,2) NOT NULL COMMENT 'Saldo actual en quetzales',
  fecha_apertura DATE NOT NULL COMMENT 'Fecha de apertura de la cuenta',
  estado VARCHAR(15) NOT NULL COMMENT 'Estado: activa, inactiva o cerrada',
  PRIMARY KEY (id_cuenta),
  FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente),
  FOREIGN KEY (id_tipo) REFERENCES tipos_cuenta (id_tipo)
) COMMENT='Cuentas bancarias';

CREATE TABLE transacciones (
  id_transaccion INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la transaccion',
  id_cuenta INT NOT NULL COMMENT 'Cuenta afectada',
  tipo VARCHAR(20) NOT NULL COMMENT 'Tipo: deposito, retiro, transferencia o pago_servicio',
  monto DECIMAL(12,2) NOT NULL COMMENT 'Monto de la transaccion en quetzales, siempre positivo',
  fecha_hora DATETIME NOT NULL COMMENT 'Fecha y hora de la transaccion',
  descripcion VARCHAR(120) COMMENT 'Descripcion o referencia',
  PRIMARY KEY (id_transaccion),
  FOREIGN KEY (id_cuenta) REFERENCES cuentas (id_cuenta)
) COMMENT='Movimientos de las cuentas';

CREATE TABLE prestamos (
  id_prestamo INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del prestamo',
  id_cliente INT NOT NULL COMMENT 'Cliente que recibio el prestamo',
  monto_aprobado DECIMAL(12,2) NOT NULL COMMENT 'Monto aprobado en quetzales',
  tasa_anual DECIMAL(5,2) NOT NULL COMMENT 'Tasa de interes anual en porcentaje',
  plazo_meses INT NOT NULL COMMENT 'Plazo en meses',
  fecha_desembolso DATE NOT NULL COMMENT 'Fecha en que se entrego el dinero',
  estado VARCHAR(15) NOT NULL COMMENT 'Estado: vigente, cancelado o en_mora',
  PRIMARY KEY (id_prestamo),
  FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente)
) COMMENT='Prestamos otorgados';

CREATE TABLE pagos_prestamo (
  id_pago INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del pago',
  id_prestamo INT NOT NULL COMMENT 'Prestamo al que se abona',
  numero_cuota INT NOT NULL COMMENT 'Numero de la cuota pagada',
  fecha_pago DATE NOT NULL COMMENT 'Fecha en que se pago la cuota',
  monto_pagado DECIMAL(12,2) NOT NULL COMMENT 'Monto pagado en quetzales',
  PRIMARY KEY (id_pago),
  FOREIGN KEY (id_prestamo) REFERENCES prestamos (id_prestamo)
) COMMENT='Pagos de cuotas de prestamos';

CREATE TABLE tarjetas (
  id_tarjeta INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la tarjeta',
  id_cuenta INT NOT NULL COMMENT 'Cuenta a la que esta asociada',
  tipo VARCHAR(10) NOT NULL COMMENT 'Tipo: debito o credito',
  fecha_emision DATE NOT NULL COMMENT 'Fecha de emision',
  fecha_vencimiento DATE NOT NULL COMMENT 'Fecha de vencimiento',
  limite_credito DECIMAL(12,2) COMMENT 'Limite de credito en quetzales, nulo para tarjetas de debito',
  PRIMARY KEY (id_tarjeta),
  FOREIGN KEY (id_cuenta) REFERENCES cuentas (id_cuenta)
) COMMENT='Tarjetas emitidas';
