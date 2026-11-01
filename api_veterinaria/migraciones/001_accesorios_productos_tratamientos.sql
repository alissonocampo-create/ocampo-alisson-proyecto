CREATE TABLE IF NOT EXISTS accesorios (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
    categoria   TEXT NOT NULL CHECK (
        categoria IN ('collar', 'correa', 'juguete', 'ropa', 'cama', 'transporte', 'otro')
    ),
    descripcion TEXT,
    precio      REAL NOT NULL CHECK (precio >= 0),
    stock       INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    activo      INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
);

CREATE TABLE IF NOT EXISTS productos_veterinarios (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
    categoria   TEXT NOT NULL CHECK (
        categoria IN ('medicamento', 'pastilla', 'shampoo', 'higiene', 'otro')
    ),
    descripcion TEXT,
    precio      REAL NOT NULL CHECK (precio >= 0),
    stock       INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    activo      INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
);

CREATE TABLE IF NOT EXISTS tratamientos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    mascota_id    INTEGER NOT NULL,
    producto_id   INTEGER,
    nombre        TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
    indicaciones  TEXT NOT NULL CHECK (length(trim(indicaciones)) > 0),
    dosis         TEXT,
    fecha_inicio  TEXT NOT NULL CHECK (date(fecha_inicio) IS NOT NULL),
    fecha_fin     TEXT CHECK (fecha_fin IS NULL OR date(fecha_fin) IS NOT NULL),
    estado        TEXT NOT NULL DEFAULT 'recetado'
                  CHECK (estado IN ('recetado', 'en_curso', 'completado', 'suspendido')),
    FOREIGN KEY (mascota_id) REFERENCES mascotas(id) ON DELETE RESTRICT,
    FOREIGN KEY (producto_id) REFERENCES productos_veterinarios(id) ON DELETE SET NULL,
    CHECK (fecha_fin IS NULL OR fecha_fin >= fecha_inicio)
);

CREATE INDEX IF NOT EXISTS idx_accesorios_categoria
    ON accesorios (categoria);
CREATE INDEX IF NOT EXISTS idx_productos_veterinarios_categoria
    ON productos_veterinarios (categoria);
CREATE INDEX IF NOT EXISTS idx_tratamientos_mascota_fecha
    ON tratamientos (mascota_id, fecha_inicio);

INSERT INTO accesorios (nombre, categoria, descripcion, precio, stock)
SELECT 'Collar ajustable', 'collar', 'Collar de nylon ajustable para perro.', 180.00, 12
WHERE NOT EXISTS (SELECT 1 FROM accesorios WHERE nombre = 'Collar ajustable');

INSERT INTO accesorios (nombre, categoria, descripcion, precio, stock)
SELECT 'Correa clásica', 'correa', 'Correa resistente de paseo.', 220.00, 8
WHERE NOT EXISTS (SELECT 1 FROM accesorios WHERE nombre = 'Correa clásica');

INSERT INTO accesorios (nombre, categoria, descripcion, precio, stock)
SELECT 'Juguete de cuerda', 'juguete', 'Juguete para morder y jugar.', 95.00, 15
WHERE NOT EXISTS (SELECT 1 FROM accesorios WHERE nombre = 'Juguete de cuerda');

INSERT INTO accesorios (nombre, categoria, descripcion, precio, stock)
SELECT 'Cama pequeña', 'cama', 'Cama acolchada para mascotas pequeñas.', 650.00, 3
WHERE NOT EXISTS (SELECT 1 FROM accesorios WHERE nombre = 'Cama pequeña');

INSERT INTO productos_veterinarios (nombre, categoria, descripcion, precio, stock)
SELECT 'Antiparasitario oral', 'pastilla', 'Producto de demostración; uso según indicación veterinaria.', 120.00, 20
WHERE NOT EXISTS (SELECT 1 FROM productos_veterinarios WHERE nombre = 'Antiparasitario oral');

INSERT INTO productos_veterinarios (nombre, categoria, descripcion, precio, stock)
SELECT 'Shampoo hipoalergénico', 'shampoo', 'Shampoo veterinario para piel sensible.', 245.00, 10
WHERE NOT EXISTS (SELECT 1 FROM productos_veterinarios WHERE nombre = 'Shampoo hipoalergénico');

INSERT INTO productos_veterinarios (nombre, categoria, descripcion, precio, stock)
SELECT 'Solución ótica veterinaria', 'medicamento', 'Producto de demostración; uso según indicación veterinaria.', 185.00, 7
WHERE NOT EXISTS (SELECT 1 FROM productos_veterinarios WHERE nombre = 'Solución ótica veterinaria');

INSERT INTO productos_veterinarios (nombre, categoria, descripcion, precio, stock)
SELECT 'Limpiador de oídos', 'higiene', 'Limpiador para higiene externa de oídos.', 160.00, 9
WHERE NOT EXISTS (SELECT 1 FROM productos_veterinarios WHERE nombre = 'Limpiador de oídos');
