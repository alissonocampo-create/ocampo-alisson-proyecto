CREATE TABLE IF NOT EXISTS migraciones_datos_demo (
    version TEXT PRIMARY KEY
);

WITH ejemplos(mascota_id, nombre) AS (
    VALUES
        (1, 'Revisión general (DEMO)'),
        (2, 'Seguimiento de bienestar (DEMO)'),
        (3, 'Cuidados preventivos (DEMO)')
)
INSERT INTO tratamientos (
    mascota_id, producto_id, nombre, indicaciones, dosis,
    fecha_inicio, fecha_fin, estado
)
SELECT
    ejemplos.mascota_id,
    NULL,
    ejemplos.nombre,
    'Ejemplo de demostración, no es una receta real. Sustituir por el plan emitido por el médico veterinario.',
    NULL,
    date('now'),
    NULL,
    'recetado'
FROM ejemplos
JOIN mascotas ON mascotas.id = ejemplos.mascota_id
WHERE NOT EXISTS (
    SELECT 1 FROM migraciones_datos_demo WHERE version = '006_tratamientos_demo'
)
AND NOT EXISTS (SELECT 1 FROM tratamientos)
AND (SELECT COUNT(*) FROM mascotas WHERE id IN (1, 2, 3)) = 3;

INSERT OR IGNORE INTO migraciones_datos_demo (version)
VALUES ('006_tratamientos_demo');
