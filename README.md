# ICEFRIOHIELO - Sistema POS Premium v2.0

Sistema de Punto de Venta (POS) profesional para heladería desarrollado con Python, customtkinter y MySQL.

## Características

 **Funcionalidades Principales:**
-  **Punto de Venta**: Venta rápida con filtros por categoría y gestión de toppings
-  **Histórico de Ventas**: Vista maestro-detalle de todas las transacciones
-  **Registro de Mermas**: Gestión de pérdidas y productos dañados
-  **Gestión de Productos**: Administración completa del catálogo y precios
-  **Gestión de Personal**: Control de usuarios e información de roles
-  **Dashboard Ejecutivo**: Reportes, gráficos y análisis de inteligencia comercial
-  **Exportación**: Generación de reportes en Excel y PDF

## Requisitos

- Python 3.8+
- MySQL 5.7+ (con XAMPP o similar)
- pip (gestor de paquetes Python)

## Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/Shakaa2426/heladeria.git
cd heladeria
```

### 2. Crear entorno virtual
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos

#### Opción A: XAMPP (Recomendado)
1. Descargar e instalar [XAMPP](https://www.apachefriends.org/)
2. Iniciar Apache y MySQL desde el panel de control
3. Importar la base de datos `ice2` en PhpMyAdmin:
   - Crear base de datos: `ice2`
   - Importar el archivo SQL (si existe)
   - O crear tablas manualmente (ver estructura abajo)

#### Estructura de Base de Datos
```sql
-- Tabla Personal (Usuarios)
CREATE TABLE Personal (
    idPersonal INT AUTO_INCREMENT PRIMARY KEY,
    nombreCompleto VARCHAR(100),
    username VARCHAR(50),
    contrasena VARCHAR(100),
    rol ENUM('Vendedor', 'Administrador')
);

-- Tabla Categorías
CREATE TABLE Categorias (
    idCategoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100)
);

-- Tabla Productos
CREATE TABLE Productos (
    idProducto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    precio DECIMAL(10, 2),
    stock INT,
    stockMinimo INT DEFAULT 10,
    idCategoria INT,
    FOREIGN KEY (idCategoria) REFERENCES Categorias(idCategoria)
);

-- Tabla Ventas
CREATE TABLE Ventas (
    idVenta INT AUTO_INCREMENT PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    totalVenta DECIMAL(10, 2),
    idPersonal INT,
    FOREIGN KEY (idPersonal) REFERENCES Personal(idPersonal)
);

-- Tabla Detalles de Venta
CREATE TABLE DetalleVentas (
    idDetalle INT AUTO_INCREMENT PRIMARY KEY,
    idVenta INT,
    idProducto INT,
    cantidad INT,
    subtotal DECIMAL(10, 2),
    FOREIGN KEY (idVenta) REFERENCES Ventas(idVenta),
    FOREIGN KEY (idProducto) REFERENCES Productos(idProducto)
);

-- Tabla Mermas
CREATE TABLE Mermas (
    idMerma INT AUTO_INCREMENT PRIMARY KEY,
    idProducto INT,
    cantidad INT,
    motivo VARCHAR(255),
    idPersonal INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idProducto) REFERENCES Productos(idProducto),
    FOREIGN KEY (idPersonal) REFERENCES Personal(idPersonal)
);
```

### 5. Credenciales por defecto
- **Usuario**: admin
- **Contraseña**: admin123

## Uso

```bash
python main.py
```

La aplicación se abrirá en una ventana con interfaz gráfica. Login inicial con credenciales por defecto.

## Estructura del Proyecto

```
heladeria/
├── main.py                 # Aplicación principal
├── requirements.txt        # Dependencias Python
├── .gitignore             # Archivos a ignorar en git
├── ice.mwb                # Modelo de base de datos MySQL Workbench
└── README.md              # Este archivo
```

## Tecnologías Utilizadas

- **Interfaz**: CustomTkinter (versión moderna de Tkinter)
- **Base de Datos**: MySQL
- **Análisis de Datos**: Pandas, Matplotlib
- **Reportes**: FPDF
- **Lenguaje**: Python 3.8+

## Roles y Permisos

### Vendedor
- Acceso a Punto de Venta
- Visualizar Histórico de Ventas
- Registrar Mermas

### Administrador
- Todas las funciones de Vendedor +
- Gestión de Productos y Catálogo
- Gestión de Personal (crear usuarios)
- Dashboard ejecutivo y reportes
- Exportación a Excel y PDF

## Vistas SQL (Requeridas)

El sistema utiliza vistas SQL para reportes. Crear las siguientes en la BD:

```sql
-- Vista de Estadísticas por Vendedor
CREATE VIEW vw_estadisticas_vendedores AS
SELECT 
    p.nombreCompleto AS Vendedor,
    COUNT(v.idVenta) AS TotalTickets,
    SUM(v.totalVenta) AS IngresosGenerados
FROM Personal p
LEFT JOIN Ventas v ON p.idPersonal = v.idPersonal
GROUP BY p.idPersonal;

-- Vista de Detalles de Ticket
CREATE VIEW vw_detalle_ticket_app AS
SELECT 
    v.idVenta AS Folio,
    prod.nombre AS Producto,
    dv.cantidad,
    dv.subtotal,
    p.nombreCompleto AS Vendedor
FROM DetalleVentas dv
JOIN Ventas v ON dv.idVenta = v.idVenta
JOIN Productos prod ON dv.idProducto = prod.idProducto
JOIN Personal p ON v.idPersonal = p.idPersonal;

-- Vista de Reporte General de Ventas
CREATE VIEW VistaReporteVentas AS
SELECT 
    v.idVenta,
    v.fecha,
    v.totalVenta,
    p.nombreCompleto AS Vendedor
FROM Ventas v
JOIN Personal p ON v.idPersonal = p.idPersonal;
```

## Notas Importantes

- Asegurar que **XAMPP esté ejecutándose** antes de abrir la aplicación
- La base de datos `ice2` debe existir y estar accesible
- Las credenciales de BD están hardcodeadas en `DatabaseHelper` (user='root', password='')
- Puerto MySQL por defecto: 3306

## Posibles Mejoras Futuras

- [ ] Implementar autenticación con hash de contraseñas
- [ ] Agregar búsqueda avanzada de productos
- [ ] Historial de cambios de usuarios/productos
- [ ] Exportación a más formatos
- [ ] Sistema de permisos más granular

## Contribuciones

Las contribuciones son bienvenidas. Para cambios grandes, abrir un issue primero.

## Licencia

Este proyecto está bajo licencia MIT.

## Autor

Desarrollado para ICEFRIOHIELO - Sistema POS Premium

---

**Última actualización**: Marzo 2026
