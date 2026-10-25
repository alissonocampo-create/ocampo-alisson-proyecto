PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS vacunas_aplicadas;
DROP TABLE IF EXISTS citas;
DROP TABLE IF EXISTS mascotas;
DROP TABLE IF EXISTS veterinarios;
DROP TABLE IF EXISTS duenos;
DROP TABLE IF EXISTS usuarios;

BEGIN TRANSACTION;

CREATE TABLE duenos (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre    TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
    telefono  TEXT NOT NULL UNIQUE CHECK (length(trim(telefono)) >= 8),
    direccion TEXT
);

CREATE TABLE mascotas (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre           TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
    especie          TEXT NOT NULL CHECK (especie IN ('perro', 'gato', 'ave', 'otro')),
    raza             TEXT,
    fecha_nacimiento TEXT CHECK (
        fecha_nacimiento IS NULL OR date(fecha_nacimiento) IS NOT NULL
    ),
    dueno_id         INTEGER NOT NULL,
    FOREIGN KEY (dueno_id) REFERENCES duenos(id) ON DELETE RESTRICT
);

CREATE TABLE veterinarios (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre            TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
    telefono          TEXT NOT NULL UNIQUE,
    correo            TEXT NOT NULL UNIQUE,
    numero_colegiacion TEXT NOT NULL UNIQUE,
    activo            INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
);

CREATE TABLE citas (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    mascota_id     INTEGER NOT NULL,
    veterinario_id INTEGER NOT NULL,
    fecha_hora     TEXT NOT NULL CHECK (datetime(fecha_hora) IS NOT NULL),
    motivo         TEXT NOT NULL CHECK (length(trim(motivo)) > 0),
    estado         TEXT NOT NULL DEFAULT 'programada'
                   CHECK (estado IN ('programada', 'atendida', 'cancelada')),
    FOREIGN KEY (mascota_id) REFERENCES mascotas(id) ON DELETE RESTRICT,
    FOREIGN KEY (veterinario_id) REFERENCES veterinarios(id) ON DELETE RESTRICT,
    UNIQUE (veterinario_id, fecha_hora)
);

CREATE TABLE vacunas_aplicadas (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    mascota_id     INTEGER NOT NULL,
    vacuna         TEXT NOT NULL CHECK (length(trim(vacuna)) > 0),
    fecha          TEXT NOT NULL CHECK (date(fecha) IS NOT NULL),
    proxima_dosis  TEXT CHECK (
        proxima_dosis IS NULL OR date(proxima_dosis) IS NOT NULL
    ),
    FOREIGN KEY (mascota_id) REFERENCES mascotas(id) ON DELETE RESTRICT,
    CHECK (proxima_dosis IS NULL OR proxima_dosis > fecha),
    UNIQUE (mascota_id, vacuna, fecha)
);

CREATE TABLE usuarios (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_usuario  TEXT NOT NULL UNIQUE CHECK (length(trim(nombre_usuario)) >= 3),
    correo          TEXT NOT NULL UNIQUE,
    nombre_completo TEXT NOT NULL CHECK (length(trim(nombre_completo)) > 0),
    password_hash   TEXT NOT NULL CHECK (length(password_hash) >= 32),
    activo          INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1)),
    creado_en       TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mascotas_dueno_id
    ON mascotas (dueno_id);
CREATE INDEX idx_citas_mascota_fecha
    ON citas (mascota_id, fecha_hora);
CREATE INDEX idx_vacunas_mascota_fecha
    ON vacunas_aplicadas (mascota_id, fecha);
CREATE INDEX idx_vacunas_proxima_dosis
    ON vacunas_aplicadas (proxima_dosis);

INSERT INTO duenos (nombre, telefono, direccion) VALUES
    ('Ana Lucía Rivera', '+504 9876-1001', 'Barrio Cabañas, Comayagua'),
    ('Carlos Mejía', '+504 9876-1002', 'Colonia Fiallos, Comayagua'),
    ('Daniela Flores', '+504 9876-1003', 'Barrio Torondón, Comayagua'),
    ('Eduardo Pineda', '+504 9876-1004', 'Colonia 21 de Abril, Comayagua'),
    ('Fernanda López', '+504 9876-1005', 'Barrio San Sebastián, Comayagua'),
    ('Gabriel Cruz', '+504 9876-1006', 'Colonia Iván Betancourth, Comayagua'),
    ('Hilda Santos', '+504 9876-1007', 'Barrio Arriba, Comayagua'),
    ('Iván García', '+504 9876-1008', 'Colonia Primero de Mayo, Comayagua'),
    ('Julia Mendoza', '+504 9876-1009', 'Barrio Abajo, Comayagua'),
    ('Kevin Reyes', '+504 9876-1010', 'Colonia Lomas del Río, Comayagua');

INSERT INTO mascotas (nombre, especie, raza, fecha_nacimiento, dueno_id) VALUES
    ('Luna', 'perro', 'Labrador', '2022-04-12', 1),
    ('Milo', 'gato', 'Criollo', '2023-09-03', 2),
    ('Nala', 'perro', 'Beagle', '2021-11-20', 3),
    ('Coco', 'ave', 'Periquito australiano', '2024-02-15', 4),
    ('Rocky', 'perro', 'Schnauzer', '2020-06-08', 5),
    ('Misha', 'gato', 'Siamés', '2022-12-01', 6),
    ('Toby', 'perro', 'Criollo', '2023-05-17', 7),
    ('Kiwi', 'ave', 'Cacatúa ninfa', '2021-08-24', 8),
    ('Simba', 'gato', 'Persa', '2020-03-30', 9),
    ('Daisy', 'perro', 'Golden retriever', '2024-01-09', 10);

INSERT INTO veterinarios (nombre, telefono, correo, numero_colegiacion) VALUES
    ('Dra. Sofía Martínez', '+504 9876-2001', 'sofia.martinez@vetdemo.hn', 'CMV-1001'),
    ('Dr. Andrés Castillo', '+504 9876-2002', 'andres.castillo@vetdemo.hn', 'CMV-1002'),
    ('Dra. Laura Aguilar', '+504 9876-2003', 'laura.aguilar@vetdemo.hn', 'CMV-1003'),
    ('Dr. Miguel Romero', '+504 9876-2004', 'miguel.romero@vetdemo.hn', 'CMV-1004'),
    ('Dra. Paula Hernández', '+504 9876-2005', 'paula.hernandez@vetdemo.hn', 'CMV-1005'),
    ('Dr. Diego Navarro', '+504 9876-2006', 'diego.navarro@vetdemo.hn', 'CMV-1006'),
    ('Dra. Valeria Ortiz', '+504 9876-2007', 'valeria.ortiz@vetdemo.hn', 'CMV-1007'),
    ('Dr. Samuel Reyes', '+504 9876-2008', 'samuel.reyes@vetdemo.hn', 'CMV-1008'),
    ('Dra. Camila Fuentes', '+504 9876-2009', 'camila.fuentes@vetdemo.hn', 'CMV-1009'),
    ('Dr. José Alvarado', '+504 9876-2010', 'jose.alvarado@vetdemo.hn', 'CMV-1010');

INSERT INTO citas (mascota_id, veterinario_id, fecha_hora, motivo, estado) VALUES
    (1, 1, '2026-10-15 08:00:00', 'Revisión general', 'atendida'),
    (2, 2, '2026-10-16 09:00:00', 'Control de peso', 'atendida'),
    (3, 3, '2026-10-17 10:00:00', 'Vacunación anual', 'atendida'),
    (4, 4, '2026-10-18 11:00:00', 'Revisión de plumaje', 'atendida'),
    (5, 5, '2026-10-19 08:00:00', 'Limpieza dental', 'atendida'),
    (6, 6, '2026-10-20 09:00:00', 'Consulta de seguimiento', 'cancelada'),
    (7, 7, '2026-10-26 10:00:00', 'Desparasitación', 'programada'),
    (8, 8, '2026-10-27 11:00:00', 'Control veterinario', 'programada'),
    (9, 9, '2026-10-28 08:30:00', 'Evaluación preventiva', 'programada'),
    (10, 10, '2026-10-29 09:30:00', 'Primera consulta', 'programada');

INSERT INTO vacunas_aplicadas (mascota_id, vacuna, fecha, proxima_dosis) VALUES
    (1, 'Rabia', '2026-10-01', '2026-10-28'),
    (2, 'Triple felina', '2026-09-15', '2026-10-30'),
    (3, 'Parvovirus', '2026-08-20', '2026-11-15'),
    (4, 'Poliomavirus aviar', '2026-07-05', NULL),
    (5, 'Rabia', '2026-10-02', '2026-10-29'),
    (6, 'Triple felina', '2026-06-12', '2026-12-12'),
    (7, 'Moquillo', '2026-09-01', '2026-10-31'),
    (8, 'Poliomavirus aviar', '2026-05-14', NULL),
    (9, 'Leucemia felina', '2026-09-25', '2026-11-25'),
    (10, 'Parvovirus', '2026-10-03', '2026-10-27');

-- Usuario de demostración. Contraseña: VetDemo2026!
-- Hash PBKDF2-HMAC-SHA256 (260 000 iteraciones); nunca guardar la contraseña en texto plano.
INSERT INTO usuarios (
    nombre_usuario, correo, nombre_completo, password_hash
) VALUES (
    'admin',
    'admin@vetdemo.hn',
    'Administración de demostración',
    'pbkdf2_sha256:260000:dmV0LWRlbW8tYWRtaW4:g-ekEVsU43D5Ygi8ZhLv8yaeUuBTmx0YTjhS_v0m-QA'
);

COMMIT;
