CREATE TABLE zona (
  zona_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la zona de reparto',
  nom_zona VARCHAR(40) NOT NULL COMMENT 'Nombre de la zona, por ejemplo zona 10',
  mun VARCHAR(60) NOT NULL COMMENT 'Municipio al que pertenece',
  PRIMARY KEY (zona_id)
) COMMENT='Zonas de reparto';

CREATE TABLE restau (
  rest_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del restaurante',
  nom_rest VARCHAR(80) NOT NULL COMMENT 'Nombre del restaurante',
  zona_id INT NOT NULL COMMENT 'Zona donde esta ubicado',
  tipo_coc VARCHAR(30) NOT NULL COMMENT 'Tipo de cocina, por ejemplo pizza o tipica',
  fec_afil DATE NOT NULL COMMENT 'Fecha en que se afilio a la plataforma',
  calif DECIMAL(2,1) NOT NULL COMMENT 'Calificacion promedio de 1.0 a 5.0',
  PRIMARY KEY (rest_id),
  FOREIGN KEY (zona_id) REFERENCES zona (zona_id)
) COMMENT='Restaurantes afiliados';

CREATE TABLE plat (
  plat_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del platillo',
  rest_id INT NOT NULL COMMENT 'Restaurante que lo ofrece',
  nom_plat VARCHAR(80) NOT NULL COMMENT 'Nombre del platillo',
  pre DECIMAL(8,2) NOT NULL COMMENT 'Precio en quetzales',
  disp TINYINT(1) NOT NULL COMMENT '1 si esta disponible, 0 si no',
  PRIMARY KEY (plat_id),
  FOREIGN KEY (rest_id) REFERENCES restau (rest_id)
) COMMENT='Menu de los restaurantes';

CREATE TABLE cli (
  cli_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del cliente',
  nom VARCHAR(80) NOT NULL COMMENT 'Nombre completo del cliente',
  tel VARCHAR(15) NOT NULL COMMENT 'Telefono del cliente',
  zona_id INT NOT NULL COMMENT 'Zona de entrega habitual',
  fec_reg DATE NOT NULL COMMENT 'Fecha de registro en la plataforma',
  PRIMARY KEY (cli_id),
  FOREIGN KEY (zona_id) REFERENCES zona (zona_id)
) COMMENT='Clientes de la plataforma';

CREATE TABLE repa (
  repa_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del repartidor',
  nom VARCHAR(80) NOT NULL COMMENT 'Nombre completo del repartidor',
  vehiculo VARCHAR(15) NOT NULL COMMENT 'Vehiculo: moto, bicicleta o carro',
  fec_ing DATE NOT NULL COMMENT 'Fecha de ingreso como repartidor',
  activo TINYINT(1) NOT NULL COMMENT '1 si sigue activo, 0 si se retiro',
  PRIMARY KEY (repa_id)
) COMMENT='Repartidores';

CREATE TABLE ped (
  ped_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del pedido',
  cli_id INT NOT NULL COMMENT 'Cliente que hizo el pedido',
  rest_id INT NOT NULL COMMENT 'Restaurante que lo prepara',
  repa_id INT COMMENT 'Repartidor asignado, nulo si el pedido se cancelo',
  fec_ped DATETIME NOT NULL COMMENT 'Fecha y hora en que se hizo el pedido',
  fec_ent DATETIME COMMENT 'Fecha y hora de entrega, nula si no se entrego',
  est VARCHAR(12) NOT NULL COMMENT 'Estado: entregado, cancelado o en_camino',
  mto_tot DECIMAL(10,2) NOT NULL COMMENT 'Monto total del pedido en quetzales',
  propina DECIMAL(8,2) NOT NULL COMMENT 'Propina para el repartidor en quetzales',
  PRIMARY KEY (ped_id),
  FOREIGN KEY (cli_id) REFERENCES cli (cli_id),
  FOREIGN KEY (rest_id) REFERENCES restau (rest_id),
  FOREIGN KEY (repa_id) REFERENCES repa (repa_id)
) COMMENT='Pedidos';

CREATE TABLE det_ped (
  det_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la linea del pedido',
  ped_id INT NOT NULL COMMENT 'Pedido al que pertenece',
  plat_id INT NOT NULL COMMENT 'Platillo pedido',
  cant INT NOT NULL COMMENT 'Cantidad pedida',
  pre_unit DECIMAL(8,2) NOT NULL COMMENT 'Precio unitario cobrado en quetzales',
  PRIMARY KEY (det_id),
  FOREIGN KEY (ped_id) REFERENCES ped (ped_id),
  FOREIGN KEY (plat_id) REFERENCES plat (plat_id)
) COMMENT='Detalle de los pedidos';

CREATE TABLE resena (
  res_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la resena',
  ped_id INT NOT NULL COMMENT 'Pedido calificado',
  punt INT NOT NULL COMMENT 'Puntaje de 1 a 5',
  coment VARCHAR(200) COMMENT 'Comentario del cliente',
  fec_res DATE NOT NULL COMMENT 'Fecha de la resena',
  PRIMARY KEY (res_id),
  FOREIGN KEY (ped_id) REFERENCES ped (ped_id)
) COMMENT='Resenas de pedidos entregados';
