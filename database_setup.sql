-- ==========================================
-- BASE DE DATOS: ice2 - SISTEMA POS HELADERÍA
-- Archivo de inyección de datos y consultas de evaluación
-- ==========================================

DROP DATABASE IF EXISTS ice2;
CREATE DATABASE ice2;
USE ice2;

-- ==========================================
-- 1. CREACIÓN DE TABLAS
-- ==========================================
CREATE TABLE Personal (
    idPersonal INT AUTO_INCREMENT PRIMARY KEY,
    nombreCompleto VARCHAR(100) NOT NULL,
    rol VARCHAR(20) NOT NULL,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL
);

CREATE TABLE Categorias (
    idCategoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE Productos (
    idProducto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    stockMinimo INT NOT NULL DEFAULT 10,
    idCategoria INT,
    FOREIGN KEY (idCategoria) REFERENCES Categorias(idCategoria)
);

CREATE TABLE Ventas (
    idVenta INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    totalVenta DECIMAL(10,2) NOT NULL,
    idPersonal INT NOT NULL,
    FOREIGN KEY (idPersonal) REFERENCES Personal(idPersonal)
);

CREATE TABLE DetalleVentas (
    idDetalle INT AUTO_INCREMENT PRIMARY KEY,
    idVenta INT NOT NULL,
    idProducto INT NOT NULL,
    cantidad INT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (idVenta) REFERENCES Ventas(idVenta),
    FOREIGN KEY (idProducto) REFERENCES Productos(idProducto)
);

CREATE TABLE Mermas (
    idMerma INT AUTO_INCREMENT PRIMARY KEY,
    idProducto INT NOT NULL,
    cantidad INT NOT NULL,
    motivo VARCHAR(200) NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    idPersonal INT NOT NULL,
    FOREIGN KEY (idProducto) REFERENCES Productos(idProducto),
    FOREIGN KEY (idPersonal) REFERENCES Personal(idPersonal)
);

-- ==========================================
-- 2. VISTAS E ÍNDICES
-- ==========================================
CREATE VIEW VistaReporteVentas AS 
SELECT v.idVenta, v.fecha, v.totalVenta, p.nombreCompleto AS Vendedor 
FROM Ventas v JOIN Personal p ON v.idPersonal = p.idPersonal;

CREATE INDEX idx_ventas_fecha ON Ventas(fecha);
CREATE INDEX idx_productos_nombre ON Productos(nombre);

-- VISTAS PARA EL PROGRAMA EN PYTHON
CREATE VIEW vw_detalle_ticket_app AS
SELECT v.idVenta AS Folio, v.fecha, p.nombre AS Producto, 
       dv.cantidad, dv.subtotal, per.nombreCompleto AS Vendedor
FROM Ventas v
JOIN DetalleVentas dv ON v.idVenta = dv.idVenta
JOIN Productos p ON dv.idProducto = p.idProducto
JOIN Personal per ON v.idPersonal = per.idPersonal;

CREATE VIEW vw_estadisticas_vendedores AS
SELECT per.nombreCompleto AS Vendedor, COUNT(DISTINCT v.idVenta) AS TotalTickets, SUM(v.totalVenta) AS IngresosGenerados
FROM Ventas v
JOIN Personal per ON v.idPersonal = per.idPersonal
GROUP BY per.idPersonal;

-- ==========================================
-- 3. INYECCIÓN MASIVA DE DATOS
-- ==========================================

-- PERSONAL (5 Usuarios)
INSERT INTO Personal (idPersonal, nombreCompleto, rol, usuario, contrasena) VALUES 
(1, 'Administrador Principal', 'Administrador', 'admin', 'admin123'),
(2, 'Maria Ventas', 'Vendedor', 'ventas', 'ventas123'),
(3, 'Juan Carlos', 'Vendedor', 'juan', 'juan123'),
(4, 'Ana Sofia', 'Vendedor', 'ana', 'ana123'),
(5, 'Roberto (Gerente)', 'Administrador', 'roberto', 'admin123');

-- CATEGORÍAS (6 Categorías)
INSERT INTO Categorias (idCategoria, nombre) VALUES 
(1, 'Helado de Leche'), (2, 'Paletas de Agua'), (3, 'Toppings y Extras'),
(4, 'Bebidas Preparadas'), (5, 'Postres Especiales'), (6, 'Insumos (Uso Interno)');

-- PRODUCTOS (25 Productos)
INSERT INTO Productos (idProducto, nombre, precio, stock, stockMinimo, idCategoria) VALUES
(1, 'Helado Vainilla 1L', 120.00, 45, 10, 1),
(2, 'Paleta Limón', 25.00, 98, 20, 2),
(3, 'Paleta Fresa', 30.00, 75, 20, 2),
(4, 'Chispas Chocolate', 15.00, 195, 50, 3),
(5, 'Helado Chocolate 1L', 130.00, 8, 15, 1),  
(6, 'Helado Fresa 1L', 120.00, 12, 15, 1),    
(7, 'Cono Galleta Doble', 12.00, 150, 40, 3),
(8, 'Paleta Mango Chile', 35.00, 40, 15, 2),
(9, 'Helado Nuez 1L', 140.00, 20, 10, 1),
(10, 'Helado Pistache 1L', 150.00, 5, 10, 1), 
(11, 'Paleta Uva', 25.00, 60, 20, 2),
(12, 'Paleta Tamarindo', 25.00, 85, 20, 2),
(13, 'Jarabe de Chocolate', 10.00, 100, 30, 3),
(14, 'Chispas Colores', 15.00, 180, 50, 3),
(15, 'Malteada de Fresa', 65.00, 30, 10, 4),
(16, 'Malteada de Chocolate', 65.00, 25, 10, 4),
(17, 'Frappé Oreo', 75.00, 40, 15, 4),
(18, 'Banana Split', 95.00, 15, 5, 5),
(19, 'Brownie con Helado', 85.00, 2, 8, 5),   
(20, 'Helado Galleta 1L', 135.00, 35, 10, 1),
(21, 'Paleta de Coco', 30.00, 50, 15, 2),
(22, 'Helado Menta Choco', 125.00, 22, 10, 1),
(23, 'Cono Sencillo', 8.00, 300, 100, 3),
(24, 'Vaso Térmico', 5.00, 500, 100, 6),
(25, 'Cucharitas Biodegradables', 2.00, 1000, 200, 6);

-- VENTAS (15 Ventas)
INSERT INTO Ventas (idVenta, fecha, totalVenta, idPersonal) VALUES 
(1, NOW() - INTERVAL 8 HOUR, 265.00, 2),
(2, NOW() - INTERVAL 7 HOUR, 120.00, 3),
(3, NOW() - INTERVAL 6 HOUR, 400.00, 4),
(4, NOW() - INTERVAL 5 HOUR, 82.00, 2),
(5, NOW() - INTERVAL 4 HOUR, 150.00, 3),
(6, NOW() - INTERVAL 4 HOUR, 45.00, 4),
(7, NOW() - INTERVAL 3 HOUR, 380.00, 2),
(8, NOW() - INTERVAL 3 HOUR, 65.00, 3),
(9, NOW() - INTERVAL 2 HOUR, 290.00, 4),
(10, NOW() - INTERVAL 2 HOUR, 95.00, 2),
(11, NOW() - INTERVAL 1 HOUR, 175.00, 3),
(12, NOW() - INTERVAL 45 MINUTE, 35.00, 4),
(13, NOW() - INTERVAL 30 MINUTE, 260.00, 2),
(14, NOW() - INTERVAL 15 MINUTE, 85.00, 3),
(15, NOW() - INTERVAL 5 MINUTE, 130.00, 4);

-- DETALLE DE VENTAS
INSERT INTO DetalleVentas (idVenta, idProducto, cantidad, subtotal) VALUES
(1, 1, 2, 240.00), (1, 2, 1, 25.00),
(2, 1, 1, 120.00),
(3, 5, 2, 260.00), (3, 8, 4, 140.00),
(4, 7, 1, 12.00), (4, 8, 2, 70.00),
(5, 10, 1, 150.00),
(6, 4, 3, 45.00),
(7, 17, 2, 150.00), (7, 1, 1, 120.00), (7, 13, 1, 10.00), (7, 14, 1, 15.00),
(8, 15, 1, 65.00),
(9, 18, 2, 190.00), (9, 23, 5, 40.00), (9, 11, 2, 50.00),
(10, 19, 1, 85.00), (10, 13, 1, 10.00),
(11, 20, 1, 135.00), (11, 23, 5, 40.00),
(12, 8, 1, 35.00),
(13, 5, 2, 260.00),
(14, 19, 1, 85.00),
(15, 16, 2, 130.00);

-- MERMAS
INSERT INTO Mermas (idMerma, idProducto, cantidad, motivo, fecha, idPersonal) VALUES
(1, 2, 5, 'Paletas descongeladas por falla en refri 2', NOW() - INTERVAL 7 HOUR, 1),
(2, 7, 12, 'Conos rotos al sacar de la caja nueva', NOW() - INTERVAL 6 HOUR, 2),
(3, 15, 1, 'Malteada derramada en mostrador', NOW() - INTERVAL 4 HOUR, 3),
(4, 10, 2, 'Helado con cristalización (mal estado)', NOW() - INTERVAL 3 HOUR, 5),
(5, 18, 1, 'Cliente canceló después de preparado', NOW() - INTERVAL 1 HOUR, 4),
(6, 24, 8, 'Vasos térmicos perforados de fábrica', NOW() - INTERVAL 30 MINUTE, 1);

-- ==============================================================================
-- BLOQUE 1: 5 CONSULTAS NORMALES (Reportes en Workbench)
-- ==============================================================================

-- 1. Ver todos los productos que están por agotarse (Alerta de Stock)
-- SELECT nombre, stock, stockMinimo 
-- FROM Productos 
-- WHERE stock <= stockMinimo;

-- 2. Ver el catálogo completo de productos con el nombre de su categoría
-- SELECT p.idProducto, p.nombre, p.precio, c.nombre AS Categoria
-- FROM Productos p
-- JOIN Categorias c ON p.idCategoria = c.idCategoria;

-- 3. Ver el total de dinero ingresado por todas las ventas
-- SELECT SUM(totalVenta) AS IngresosTotales, COUNT(idVenta) AS TotalTickets 
-- FROM Ventas;

-- 4. Ver el registro de todas las mermas (pérdidas) con el responsable
-- SELECT m.fecha, p.nombre AS Producto, m.cantidad, m.motivo, per.nombreCompleto AS ReportadoPor
-- FROM Mermas m
-- JOIN Productos p ON m.idProducto = p.idProducto
-- JOIN Personal per ON m.idPersonal = per.idPersonal;

-- 5. Ver el ranking de los 3 productos más vendidos históricamente
-- SELECT p.nombre, SUM(dv.cantidad) AS total_vendido 
-- FROM DetalleVentas dv 
-- JOIN Productos p ON dv.idProducto = p.idProducto 
-- GROUP BY p.idProducto 
-- ORDER BY total_vendido DESC 
-- LIMIT 3;

-- ==============================================================================
-- BLOQUE 2: 5 CONSULTAS EMBEBIDAS (Las que usa Python con parametrizadas)
-- ==============================================================================

-- 1. Filtrar productos por categoría en el POS
-- SELECT idProducto, nombre, precio, stock 
-- FROM Productos 
-- WHERE stock > 0 AND idCategoria = %s;

-- 2. Consultar detalle exacto al darle clic a un ticket
-- SELECT Producto, cantidad, subtotal, Vendedor 
-- FROM vw_detalle_ticket_app 
-- WHERE Folio = %s;

-- 3. Registrar la cabecera de una nueva venta
-- INSERT INTO Ventas (totalVenta, idPersonal) 
-- VALUES (%s, %s);

-- 4. Registrar el detalle de cada producto en el ticket
-- INSERT INTO DetalleVentas (idVenta, idProducto, cantidad, subtotal) 
-- VALUES (%s, %s, %s, %s);

-- 5. Descontar el stock automáticamente al cobrar
-- UPDATE Productos 
-- SET stock = stock - %s 
-- WHERE idProducto = %s;

-- ==============================================================================
-- BLOQUE 3: 5 CONSULTAS PARA EL ROL "VENDEDOR" (Operativas de Ventas)
-- ==============================================================================

-- 1. Consultar el stock y precio de un producto específico (Buscador)
-- SELECT nombre, precio, stock 
-- FROM Productos 
-- WHERE nombre LIKE '%Paleta%';

-- 2. Ver el historial de tickets cobrados por el vendedor actual
-- SELECT idVenta, fecha, totalVenta 
-- FROM Ventas 
-- WHERE idPersonal = 2 
-- ORDER BY fecha DESC;

-- 3. Consultar cuánto dinero en total ha cobrado el vendedor en su turno
-- SELECT SUM(totalVenta) AS MiCorteDeCaja, COUNT(idVenta) AS MisTicketsEmitidos
-- FROM Ventas 
-- WHERE idPersonal = 2;

-- 4. Ver qué productos de una categoría tienen stock disponible
-- SELECT nombre, precio 
-- FROM Productos 
-- WHERE idCategoria = 3 AND stock > 0;

-- 5. Consultar los detalles exactos de un ticket recién cobrado
-- SELECT p.nombre AS Producto, d.cantidad, d.subtotal
-- FROM DetalleVentas d
-- JOIN Productos p ON d.idProducto = p.idProducto
-- WHERE d.idVenta = 15;

-- ==============================================================================
-- BLOQUE 4: 5 CONSULTAS PARA EL ROL "ADMINISTRADOR" (Auditoría y Gestión)
-- ==============================================================================

-- 1. Ver la lista completa de empleados y sus roles
-- SELECT idPersonal, nombreCompleto, rol, usuario 
-- FROM Personal 
-- ORDER BY rol ASC;

-- 2. Ver cuánto dinero ingresó cada empleado (Ranking de vendedores)
-- SELECT per.nombreCompleto AS Vendedor, SUM(v.totalVenta) AS TotalIngresado, COUNT(v.idVenta) AS TicketsCobrados
-- FROM Ventas v
-- JOIN Personal per ON v.idPersonal = per.idPersonal
-- GROUP BY per.idPersonal
-- ORDER BY TotalIngresado DESC;

-- 3. Auditoría de Mermas: Qué empleado ha reportado más pérdidas
-- SELECT per.nombreCompleto AS Empleado, SUM(m.cantidad) AS TotalProductosDañados
-- FROM Mermas m
-- JOIN Personal per ON m.idPersonal = per.idPersonal
-- GROUP BY per.idPersonal
-- ORDER BY TotalProductosDañados DESC;

-- 4. Actualizar la contraseña o el rol de un vendedor
-- UPDATE Personal 
-- SET rol = 'Administrador', contrasena = 'nueva_clave456' 
-- WHERE usuario = 'ana';

-- 5. Rastrear ventas sospechosas (montos inusuales mayores a $300)
-- SELECT v.idVenta, v.fecha, v.totalVenta, per.nombreCompleto AS Responsable
-- FROM Ventas v
-- JOIN Personal per ON v.idPersonal = per.idPersonal
-- WHERE v.totalVenta > 300.00
-- ORDER BY v.fecha DESC;
