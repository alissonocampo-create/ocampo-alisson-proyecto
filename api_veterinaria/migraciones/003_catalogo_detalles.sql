UPDATE accesorios
SET uso = CASE nombre
    WHEN 'Collar ajustable' THEN 'Identificar y sujetar con seguridad durante los paseos.'
    WHEN 'Correa clásica' THEN 'Guiar a la mascota durante los paseos.'
    WHEN 'Juguete de cuerda' THEN 'Ofrecer juego y enriquecimiento supervisado.'
    WHEN 'Cama pequeña' THEN 'Proporcionar un espacio acolchado para descansar.'
    ELSE 'Consulta las indicaciones del fabricante.'
END
WHERE uso IS NULL OR length(trim(uso)) = 0;

UPDATE productos_veterinarios
SET uso = CASE nombre
    WHEN 'Antiparasitario oral' THEN 'Uso únicamente según etiqueta y prescripción veterinaria.'
    WHEN 'Shampoo hipoalergénico' THEN 'Higiene del pelaje; seguir las instrucciones de la etiqueta.'
    WHEN 'Solución ótica veterinaria' THEN 'Uso únicamente según etiqueta y prescripción veterinaria.'
    WHEN 'Limpiador de oídos' THEN 'Higiene externa según las instrucciones del fabricante.'
    ELSE 'Consulta las indicaciones del fabricante o de un veterinario.'
END
WHERE uso IS NULL OR length(trim(uso)) = 0;

UPDATE alimentos
SET uso = CASE nombre
    WHEN 'Concentrado completo para perro' THEN 'Alimentación diaria de perros adultos según la ración del envase.'
    WHEN 'Alimento húmedo para gato' THEN 'Alimentación para gatos según la ración del envase.'
    WHEN 'Premios horneados para perro' THEN 'Premio complementario; ofrecer según las indicaciones del envase.'
    ELSE 'Alimentación según especie, etapa y ración indicada en el envase.'
END
WHERE uso IS NULL OR length(trim(uso)) = 0;

UPDATE accesorios
SET descripcion = 'Descripción pendiente de completar.'
WHERE descripcion IS NULL OR length(trim(descripcion)) = 0;

UPDATE productos_veterinarios
SET descripcion = 'Descripción pendiente de completar.'
WHERE descripcion IS NULL OR length(trim(descripcion)) = 0;

UPDATE alimentos
SET descripcion = 'Descripción pendiente de completar.'
WHERE descripcion IS NULL OR length(trim(descripcion)) = 0;
