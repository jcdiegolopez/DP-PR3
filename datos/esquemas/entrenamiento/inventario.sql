CREATE TABLE bod (
  bod_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la bodega',
  nom_bod VARCHAR(60) NOT NULL COMMENT 'Nombre de la bodega',
  ubic VARCHAR(80) NOT NULL COMMENT 'Ubicacion de la bodega',
  cap_max INT NOT NULL COMMENT 'Capacidad maxima en unidades',
  PRIMARY KEY (bod_id)
) COMMENT='Bodegas de la empresa';

CREATE TABLE prov (
  prov_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del proveedor',
  nom_prov VARCHAR(100) NOT NULL COMMENT 'Nombre o razon social del proveedor',
  nit VARCHAR(15) COMMENT 'NIT del proveedor',
  tel VARCHAR(15) COMMENT 'Telefono del proveedor',
  pais VARCHAR(40) NOT NULL COMMENT 'Pais de origen del proveedor',
  PRIMARY KEY (prov_id)
) COMMENT='Proveedores';

CREATE TABLE cat_prod (
  cat_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la categoria',
  nom_cat VARCHAR(60) NOT NULL COMMENT 'Nombre de la categoria de producto',
  PRIMARY KEY (cat_id)
) COMMENT='Categorias de productos';

CREATE TABLE prod (
  prod_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del producto',
  cod VARCHAR(12) NOT NULL COMMENT 'Codigo interno del producto',
  nom_prod VARCHAR(100) NOT NULL COMMENT 'Nombre del producto',
  cat_id INT NOT NULL COMMENT 'Categoria del producto',
  prov_id INT NOT NULL COMMENT 'Proveedor habitual',
  pre_cmp DECIMAL(10,2) NOT NULL COMMENT 'Precio de compra en quetzales',
  pre_vta DECIMAL(10,2) NOT NULL COMMENT 'Precio de venta en quetzales',
  stk_min INT NOT NULL COMMENT 'Stock minimo antes de pedir reposicion',
  PRIMARY KEY (prod_id),
  FOREIGN KEY (cat_id) REFERENCES cat_prod (cat_id),
  FOREIGN KEY (prov_id) REFERENCES prov (prov_id)
) COMMENT='Productos del inventario';

CREATE TABLE exis (
  exis_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del registro de existencia',
  bod_id INT NOT NULL COMMENT 'Bodega donde esta el producto',
  prod_id INT NOT NULL COMMENT 'Producto almacenado',
  cant_exis INT NOT NULL COMMENT 'Cantidad en existencia',
  fec_act DATE NOT NULL COMMENT 'Fecha de la ultima actualizacion',
  PRIMARY KEY (exis_id),
  FOREIGN KEY (bod_id) REFERENCES bod (bod_id),
  FOREIGN KEY (prod_id) REFERENCES prod (prod_id)
) COMMENT='Existencias actuales por bodega y producto';

CREATE TABLE mov_inv (
  mov_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del movimiento',
  prod_id INT NOT NULL COMMENT 'Producto movido',
  bod_id INT NOT NULL COMMENT 'Bodega afectada',
  tip_mov VARCHAR(3) NOT NULL COMMENT 'Tipo de movimiento: ent entrada, sal salida o aju ajuste',
  cant INT NOT NULL COMMENT 'Cantidad movida',
  fec_mov DATETIME NOT NULL COMMENT 'Fecha y hora del movimiento',
  usr VARCHAR(30) NOT NULL COMMENT 'Usuario que registro el movimiento',
  PRIMARY KEY (mov_id),
  FOREIGN KEY (prod_id) REFERENCES prod (prod_id),
  FOREIGN KEY (bod_id) REFERENCES bod (bod_id)
) COMMENT='Movimientos de inventario';

CREATE TABLE ord_cmp (
  ord_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la orden de compra',
  prov_id INT NOT NULL COMMENT 'Proveedor al que se compra',
  fec_ord DATE NOT NULL COMMENT 'Fecha en que se hizo la orden',
  fec_ent DATE COMMENT 'Fecha de entrega real, nula si aun no llega',
  mto_tot DECIMAL(12,2) NOT NULL COMMENT 'Monto total de la orden en quetzales',
  est VARCHAR(12) NOT NULL COMMENT 'Estado: pendiente, recibida o anulada',
  PRIMARY KEY (ord_id),
  FOREIGN KEY (prov_id) REFERENCES prov (prov_id)
) COMMENT='Ordenes de compra a proveedores';

CREATE TABLE det_ord_cmp (
  det_id INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la linea de la orden',
  ord_id INT NOT NULL COMMENT 'Orden de compra a la que pertenece',
  prod_id INT NOT NULL COMMENT 'Producto solicitado',
  cant INT NOT NULL COMMENT 'Cantidad solicitada',
  pre_unit DECIMAL(10,2) NOT NULL COMMENT 'Precio unitario pactado en quetzales',
  PRIMARY KEY (det_id),
  FOREIGN KEY (ord_id) REFERENCES ord_cmp (ord_id),
  FOREIGN KEY (prod_id) REFERENCES prod (prod_id)
) COMMENT='Detalle de las ordenes de compra';
