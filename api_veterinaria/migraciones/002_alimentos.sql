CREATE TABLE IF NOT EXISTS alimentos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
    categoria   TEXT NOT NULL CHECK (
        categoria IN ('concentrado', 'humedo', 'premio', 'suplemento', 'dieta_especial')
    ),
    especie     TEXT NOT NULL DEFAULT 'universal'
                CHECK (especie IN ('perro', 'gato', 'ave', 'universal')),
    etapa       TEXT NOT NULL DEFAULT 'todas'
                CHECK (etapa IN ('cachorro', 'adulto', 'senior', 'todas')),
    descripcion TEXT,
    precio      REAL NOT NULL CHECK (precio >= 0),
    stock       INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    activo      INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_alimentos_categoria_especie
    ON alimentos (categoria, especie);

INSERT INTO alimentos (nombre, categoria, especie, etapa, descripcion, precio, stock)
SELECT 'Concentrado completo para perro', 'concentrado', 'perro', 'adulto',
       'Alimento balanceado para perros adultos.', 780.00, 12
WHERE NOT EXISTS (
    SELECT 1 FROM alimentos WHERE nombre = 'Concentrado completo para perro'
);

INSERT INTO alimentos (nombre, categoria, especie, etapa, descripcion, precio, stock)
SELECT 'Alimento húmedo para gato', 'humedo', 'gato', 'todas',
       'Alimento húmedo para gatos.', 65.00, 18
WHERE NOT EXISTS (
    SELECT 1 FROM alimentos WHERE nombre = 'Alimento húmedo para gato'
);

INSERT INTO alimentos (nombre, categoria, especie, etapa, descripcion, precio, stock)
SELECT 'Premios horneados para perro', 'premio', 'perro', 'todas',
       'Premios para mascotas; ofrecer como complemento.', 110.00, 2
WHERE NOT EXISTS (
    SELECT 1 FROM alimentos WHERE nombre = 'Premios horneados para perro'
);
