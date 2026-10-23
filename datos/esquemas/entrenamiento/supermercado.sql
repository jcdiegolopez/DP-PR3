CREATE TABLE sucursales (
  id_sucursal INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la sucursal',
  nombre VARCHAR(80) NOT NULL COMMENT 'Nombre comercial de la sucursal',
  departamento VARCHAR(40) NOT NULL COMMENT 'Departamento de Guatemala donde esta ubicada',
  municipio VARCHAR(60) NOT NULL COMMENT 'Municipio donde esta ubicada',
  direccion VARCHAR(150) COMMENT 'Direccion de la sucursal',
  fecha_apertura DATE NOT NULL COMMENT 'Fecha en que abrio la sucursal',
  area_m2 INT COMMENT 'Area de la sala de ventas en metros cuadrados',
  PRIMARY KEY (id_sucursal)
) COMMENT='Sucursales del supermercado';

CREATE TABLE clientes (
  id_cliente INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del cliente',
  nit VARCHAR(15) COMMENT 'Numero de identificacion tributaria del cliente',
  nombre VARCHAR(60) NOT NULL COMMENT 'Nombres del cliente',
  apellido VARCHAR(60) NOT NULL COMMENT 'Apellidos del cliente',
  correo VARCHAR(100) COMMENT 'Correo electronico',
  telefono VARCHAR(15) COMMENT 'Telefono de contacto',
  departamento VARCHAR(40) COMMENT 'Departamento de residencia',
  fecha_registro DATE NOT NULL COMMENT 'Fecha en que se registro como cliente',
  PRIMARY KEY (id_cliente)
) COMMENT='Clientes registrados en el programa de lealtad';

CREATE TABLE categorias (
  id_categoria INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la categoria',
  nombre VARCHAR(60) NOT NULL COMMENT 'Nombre de la categoria, por ejemplo lacteos o abarrotes',
  descripcion VARCHAR(150) COMMENT 'Descripcion de la categoria',
  PRIMARY KEY (id_categoria)
) COMMENT='Categorias de productos';

CREATE TABLE proveedores (
  id_proveedor INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del proveedor',
  nombre VARCHAR(100) NOT NULL COMMENT 'Razon social del proveedor',
  nit VARCHAR(15) COMMENT 'NIT del proveedor',
  telefono VARCHAR(15) COMMENT 'Telefono del proveedor',
  ciudad VARCHAR(60) COMMENT 'Ciudad donde opera el proveedor',
  PRIMARY KEY (id_proveedor)
) COMMENT='Proveedores que abastecen al supermercado';

CREATE TABLE productos (
  id_producto INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del producto',
  nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del producto',
  id_categoria INT NOT NULL COMMENT 'Categoria a la que pertenece',
  id_proveedor INT NOT NULL COMMENT 'Proveedor que lo suministra',
  precio_unitario DECIMAL(10,2) NOT NULL COMMENT 'Precio de venta en quetzales',
  costo DECIMAL(10,2) NOT NULL COMMENT 'Costo de compra en quetzales',
  activo TINYINT(1) NOT NULL DEFAULT 1 COMMENT '1 si el producto se sigue vendiendo, 0 si fue descontinuado',
  PRIMARY KEY (id_producto),
  FOREIGN KEY (id_categoria) REFERENCES categorias (id_categoria),
  FOREIGN KEY (id_proveedor) REFERENCES proveedores (id_proveedor)
) COMMENT='Catalogo de productos';

CREATE TABLE empleados (
  id_empleado INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador del empleado',
  nombre VARCHAR(60) NOT NULL COMMENT 'Nombres del empleado',
  apellido VARCHAR(60) NOT NULL COMMENT 'Apellidos del empleado',
  puesto VARCHAR(40) NOT NULL COMMENT 'Puesto, por ejemplo cajero, bodeguero o gerente',
  id_sucursal INT NOT NULL COMMENT 'Sucursal donde trabaja',
  fecha_contratacion DATE NOT NULL COMMENT 'Fecha de contratacion',
  salario DECIMAL(10,2) NOT NULL COMMENT 'Salario mensual en quetzales',
  PRIMARY KEY (id_empleado),
  FOREIGN KEY (id_sucursal) REFERENCES sucursales (id_sucursal)
) COMMENT='Empleados del supermercado';

CREATE TABLE ventas (
  id_venta INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la venta',
  id_cliente INT COMMENT 'Cliente que compro, nulo si no uso tarjeta de lealtad',
  id_sucursal INT NOT NULL COMMENT 'Sucursal donde se hizo la venta',
  id_empleado INT NOT NULL COMMENT 'Cajero que atendio la venta',
  fecha_venta DATETIME NOT NULL COMMENT 'Fecha y hora de la venta',
  metodo_pago VARCHAR(20) NOT NULL COMMENT 'Metodo de pago: efectivo, tarjeta o transferencia',
  total DECIMAL(12,2) NOT NULL COMMENT 'Total de la venta en quetzales',
  PRIMARY KEY (id_venta),
  FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente),
  FOREIGN KEY (id_sucursal) REFERENCES sucursales (id_sucursal),
  FOREIGN KEY (id_empleado) REFERENCES empleados (id_empleado)
) COMMENT='Encabezado de cada venta';

CREATE TABLE detalle_ventas (
  id_detalle INT NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la linea de detalle',
  id_venta INT NOT NULL COMMENT 'Venta a la que pertenece',
  id_producto INT NOT NULL COMMENT 'Producto vendido',
  cantidad INT NOT NULL COMMENT 'Unidades vendidas',
  precio_unitario DECIMAL(10,2) NOT NULL COMMENT 'Precio cobrado por unidad en quetzales',
  descuento DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Descuento aplicado a la linea en quetzales',
  PRIMARY KEY (id_detalle),
  FOREIGN KEY (id_venta) REFERENCES ventas (id_venta),
  FOREIGN KEY (id_producto) REFERENCES productos (id_producto)
) COMMENT='Productos incluidos en cada venta';
