PRAGMA foreign_keys = OFF;
BEGIN IMMEDIATE;

CREATE TABLE mascotas_actualizadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
    especie TEXT NOT NULL CHECK (
        especie IN ('perro', 'gato', 'ave', 'gallina', 'caballo', 'vaca', 'otro')
    ),
    raza TEXT,
    fecha_nacimiento TEXT CHECK (
        fecha_nacimiento IS NULL OR date(fecha_nacimiento) IS NOT NULL
    ),
    dueno_id INTEGER NOT NULL,
    imagen_url TEXT,
    FOREIGN KEY (dueno_id) REFERENCES duenos(id) ON DELETE RESTRICT
);

INSERT INTO mascotas_actualizadas (
    id, nombre, especie, raza, fecha_nacimiento, dueno_id, imagen_url
)
SELECT id, nombre, especie, raza, fecha_nacimiento, dueno_id, imagen_url
FROM mascotas;

DROP TABLE mascotas;
ALTER TABLE mascotas_actualizadas RENAME TO mascotas;
CREATE INDEX idx_mascotas_dueno_id ON mascotas(dueno_id);

CREATE TABLE IF NOT EXISTS migraciones_datos_demo (
    version TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS migraciones_esquema (
    version TEXT PRIMARY KEY
);

WITH ejemplos(nombre, especie, raza, fecha_nacimiento, dueno_id) AS (
    VALUES
        ('Pepita', 'gallina', 'Criolla', '2024-03-15', 1),
        ('Relámpago', 'caballo', 'Cuarto de milla', '2021-08-20', 2),
        ('Gangster', 'vaca', 'Holstein', '2023-02-01', 3),
        ('Bandida', 'vaca', 'Brahman', '2022-10-12', 4)
)
INSERT INTO mascotas (nombre, especie, raza, fecha_nacimiento, dueno_id)
SELECT ejemplos.nombre, ejemplos.especie, ejemplos.raza,
       ejemplos.fecha_nacimiento, ejemplos.dueno_id
FROM ejemplos
JOIN duenos ON duenos.id = ejemplos.dueno_id
WHERE NOT EXISTS (
    SELECT 1 FROM migraciones_datos_demo WHERE version = '007_mascotas_granja'
)
AND NOT EXISTS (
    SELECT 1 FROM mascotas
    WHERE nombre = ejemplos.nombre AND especie = ejemplos.especie
);

INSERT OR IGNORE INTO migraciones_datos_demo (version)
VALUES ('007_mascotas_granja');

INSERT OR IGNORE INTO migraciones_esquema (version)
VALUES ('007_mascotas_granja');

COMMIT;
PRAGMA foreign_keys = ON;
