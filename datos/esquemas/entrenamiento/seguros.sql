CREATE TABLE ase (
  ase_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del asegurado',
  nom VARCHAR(60) NOT NULL COMMENT 'Nombres del asegurado',
  ape VARCHAR(60) NOT NULL COMMENT 'Apellidos del asegurado',
  dpi VARCHAR(15) NOT NULL COMMENT 'DPI del asegurado',
  fec_nac DATE NOT NULL COMMENT 'Fecha de nacimiento',
  tel VARCHAR(15) COMMENT 'Telefono de contacto',
  dep VARCHAR(40) COMMENT 'Departamento de residencia',
  fec_reg DATE NOT NULL COMMENT 'Fecha en que se registro como asegurado',
  PRIMARY KEY (ase_id)
) COMMENT='Asegurados';

CREATE TABLE ram (
  ram_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del ramo',
  nom_ram VARCHAR(30) NOT NULL COMMENT 'Ramo del seguro: vida, auto, salud o hogar',
  PRIMARY KEY (ram_id)
) COMMENT='Ramos de seguro';

CREATE TABLE agen (
  agen_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del agente de seguros',
  nom VARCHAR(80) NOT NULL COMMENT 'Nombre completo del agente',
  fec_ing DATE NOT NULL COMMENT 'Fecha de ingreso como agente',
  comis_pct DECIMAL(4,2) NOT NULL COMMENT 'Porcentaje de comision sobre la prima',
  PRIMARY KEY (agen_id)
) COMMENT='Agentes que venden polizas';

CREATE TABLE pol (
  pol_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la poliza',
  ase_id INT NOT NULL COMMENT 'Asegurado titular',
  ram_id INT NOT NULL COMMENT 'Ramo de la poliza',
  agen_id INT NOT NULL COMMENT 'Agente que la vendio',
  fec_ini DATE NOT NULL COMMENT 'Fecha de inicio de la vigencia',
  fec_fin DATE NOT NULL COMMENT 'Fecha de fin de la vigencia',
  mto_ase DECIMAL(12,2) NOT NULL COMMENT 'Monto asegurado en quetzales',
  prima_anual DECIMAL(10,2) NOT NULL COMMENT 'Prima anual en quetzales',
  est VARCHAR(10) NOT NULL COMMENT 'Estado: vigente, vencida o cancelada',
  PRIMARY KEY (pol_id),
  FOREIGN KEY (ase_id) REFERENCES ase (ase_id),
  FOREIGN KEY (ram_id) REFERENCES ram (ram_id),
  FOREIGN KEY (agen_id) REFERENCES agen (agen_id)
) COMMENT='Polizas emitidas';

CREATE TABLE sini (
  sini_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del siniestro',
  pol_id INT NOT NULL COMMENT 'Poliza afectada',
  fec_sini DATE NOT NULL COMMENT 'Fecha en que ocurrio el siniestro',
  fec_rep DATE NOT NULL COMMENT 'Fecha en que se reporto',
  mto_recl DECIMAL(12,2) NOT NULL COMMENT 'Monto reclamado en quetzales',
  mto_pag DECIMAL(12,2) COMMENT 'Monto pagado en quetzales, nulo si no se ha resuelto',
  est VARCHAR(12) NOT NULL COMMENT 'Estado: abierto, pagado o rechazado',
  descr VARCHAR(150) COMMENT 'Descripcion del siniestro',
  PRIMARY KEY (sini_id),
  FOREIGN KEY (pol_id) REFERENCES pol (pol_id)
) COMMENT='Siniestros reportados';

CREATE TABLE pag_prima (
  pag_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del pago de prima',
  pol_id INT NOT NULL COMMENT 'Poliza que se paga',
  fec_pag DATE NOT NULL COMMENT 'Fecha del pago',
  mto DECIMAL(10,2) NOT NULL COMMENT 'Monto pagado en quetzales',
  metodo VARCHAR(15) NOT NULL COMMENT 'Metodo: debito, tarjeta o efectivo',
  PRIMARY KEY (pag_id),
  FOREIGN KEY (pol_id) REFERENCES pol (pol_id)
) COMMENT='Pagos de primas';

CREATE TABLE benef (
  benef_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del beneficiario',
  pol_id INT NOT NULL COMMENT 'Poliza de vida a la que pertenece',
  nom VARCHAR(80) NOT NULL COMMENT 'Nombre del beneficiario',
  parent VARCHAR(20) NOT NULL COMMENT 'Parentesco con el asegurado',
  pct DECIMAL(5,2) NOT NULL COMMENT 'Porcentaje de la indemnizacion que recibe',
  PRIMARY KEY (benef_id),
  FOREIGN KEY (pol_id) REFERENCES pol (pol_id)
) COMMENT='Beneficiarios de polizas';

CREATE TABLE ajust (
  ajust_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la inspeccion',
  sini_id INT NOT NULL COMMENT 'Siniestro inspeccionado',
  nom_ajust VARCHAR(80) NOT NULL COMMENT 'Nombre del ajustador que inspecciono',
  fec_insp DATE NOT NULL COMMENT 'Fecha de la inspeccion',
  dictamen VARCHAR(12) NOT NULL COMMENT 'Dictamen: procede o no_procede',
  PRIMARY KEY (ajust_id),
  FOREIGN KEY (sini_id) REFERENCES sini (sini_id)
) COMMENT='Inspecciones de ajustadores';
