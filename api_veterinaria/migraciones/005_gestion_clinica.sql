CREATE TABLE IF NOT EXISTS sesiones (
    token_hash TEXT PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    creada_en TEXT NOT NULL,
    expira_en TEXT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sesiones_expira_en ON sesiones(expira_en);

CREATE TABLE IF NOT EXISTS lotes_farmacia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    numero_lote TEXT NOT NULL CHECK (length(trim(numero_lote)) > 0),
    proveedor TEXT CHECK (proveedor IS NULL OR length(trim(proveedor)) > 0),
    vencimiento TEXT NOT NULL CHECK (date(vencimiento) IS NOT NULL),
    stock INTEGER NOT NULL CHECK (stock >= 0),
    creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos_veterinarios(id) ON DELETE CASCADE,
    UNIQUE (producto_id, numero_lote)
);

CREATE INDEX IF NOT EXISTS idx_lotes_vencimiento
    ON lotes_farmacia(vencimiento);
CREATE INDEX IF NOT EXISTS idx_lotes_producto
    ON lotes_farmacia(producto_id);

CREATE TABLE IF NOT EXISTS intentos_acceso (
    direccion_ip TEXT PRIMARY KEY,
    intentos INTEGER NOT NULL DEFAULT 0,
    ultimo_intento TEXT NOT NULL
);
