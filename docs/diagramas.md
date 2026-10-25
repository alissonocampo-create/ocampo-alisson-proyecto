# Diseño de la clínica veterinaria

**Estudiante:** Alisson Daniela Ocampo Maldonado
**Proyecto:** Sistema de gestión para una clínica veterinaria
**Asignatura:** Programación III (IS-151)

## Diagrama entidad-relación

```mermaid
erDiagram
    DUENOS {
        INTEGER id PK
        TEXT nombre
        TEXT telefono UK
        TEXT direccion
    }

    MASCOTAS {
        INTEGER id PK
        TEXT nombre
        TEXT especie
        TEXT raza
        TEXT fecha_nacimiento
        INTEGER dueno_id FK
    }

    VETERINARIOS {
        INTEGER id PK
        TEXT nombre
        TEXT telefono UK
        TEXT correo UK
        TEXT numero_colegiacion UK
        INTEGER activo
    }

    CITAS {
        INTEGER id PK
        INTEGER mascota_id FK
        INTEGER veterinario_id FK
        TEXT fecha_hora
        TEXT motivo
        TEXT estado
    }

    VACUNAS_APLICADAS {
        INTEGER id PK
        INTEGER mascota_id FK
        TEXT vacuna
        TEXT fecha
        TEXT proxima_dosis
    }

    USUARIOS {
        INTEGER id PK
        TEXT nombre_usuario UK
        TEXT correo UK
        TEXT nombre_completo
        TEXT password_hash
        INTEGER activo
        TEXT creado_en
    }

    DUENOS ||--o{ MASCOTAS : "es responsable de"
    MASCOTAS ||--o{ CITAS : "tiene"
    VETERINARIOS ||--o{ CITAS : "atiende"
    MASCOTAS ||--o{ VACUNAS_APLICADAS : "recibe"
```

`PK` es llave primaria, `FK` es llave foránea y `UK` indica un valor único. Un dueño puede tener varias mascotas; cada mascota tiene un solo dueño. Las citas relacionan una mascota con un veterinario, y el historial de vacunas pertenece a una mascota. Los usuarios administran el acceso al sistema y no representan una relación de atención médica.

## Diagrama UML de clases

```mermaid
classDiagram
    class Dueno {
        +int id
        +str nombre
        +str telefono
        +str direccion
    }

    class Mascota {
        +int id
        +str nombre
        +str especie
        +str raza
        +date fecha_nacimiento
        +int dueno_id
    }

    class Veterinario {
        +int id
        +str nombre
        +str telefono
        +str correo
        +str numero_colegiacion
        +bool activo
    }

    class Cita {
        +int id
        +int mascota_id
        +int veterinario_id
        +datetime fecha_hora
        +str motivo
        +str estado
    }

    class VacunaAplicada {
        +int id
        +int mascota_id
        +str vacuna
        +date fecha
        +date proxima_dosis
    }

    class Usuario {
        +int id
        +str nombre_usuario
        +str correo
        +str nombre_completo
        +str password_hash
        +bool activo
        +verificar_contrasena(contrasena) bool
    }

    class RepositorioBase {
        <<abstract>>
        +obtener_por_id(id)
        +listar()
        +crear(entidad)
        +actualizar(id, entidad)
        +eliminar(id)
    }

    class RepositorioDuenos
    class RepositorioMascotas
    class RepositorioVeterinarios
    class RepositorioCitas {
        +buscar_por_fecha(fecha)
        +existe_conflicto(veterinario_id, fecha_hora) bool
    }
    class RepositorioVacunasAplicadas {
        +buscar_proximas_dosis(desde, hasta)
    }
    class RepositorioUsuarios {
        +buscar_por_nombre_usuario(nombre_usuario)
    }

    class ServicioClinica {
        +agendar_cita(mascota_id, veterinario_id, fecha_hora, motivo)
        +validar_cita_futura(fecha_hora)
        +validar_disponibilidad(veterinario_id, fecha_hora)
        +listar_vacunas_pendientes(dias)
    }

    Dueno "1" --> "0..*" Mascota : responsable
    Mascota "1" --> "0..*" Cita : citas
    Veterinario "1" --> "0..*" Cita : atiende
    Mascota "1" --> "0..*" VacunaAplicada : historial

    RepositorioDuenos --|> RepositorioBase
    RepositorioMascotas --|> RepositorioBase
    RepositorioVeterinarios --|> RepositorioBase
    RepositorioCitas --|> RepositorioBase
    RepositorioVacunasAplicadas --|> RepositorioBase
    RepositorioUsuarios --|> RepositorioBase

    ServicioClinica ..> RepositorioCitas : valida y agenda
    ServicioClinica ..> RepositorioVacunasAplicadas : consulta
```

## Reglas del diseño

- Un veterinario no puede tener dos citas con la misma fecha y hora.
- No se agenda una cita en una fecha pasada.
- No se puede eliminar un dueño que todavía tiene mascotas.
- Las vacunas pendientes son las dosis cuya fecha está entre hoy y los próximos siete días.
- Las contraseñas se guardan como hashes, nunca como texto plano.
- La base de datos se crea con [`crear_bd.sql`](../crear_bd.sql), que incluye registros de prueba.
