import sqlite3
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from database import get_db
from esquemas import CitaEntrada, LoteFarmaciaEntrada, VacunaEntrada

router = APIRouter(tags=["Agenda y farmacia"])


@router.get("/veterinarios/")
def listar_veterinarios(
    connection: sqlite3.Connection = Depends(get_db),
) -> list[dict[str, object]]:
    rows = connection.execute(
        "SELECT id, nombre FROM veterinarios WHERE activo = 1 ORDER BY nombre"
    ).fetchall()
    return [dict(row) for row in rows]


def _cita_por_id(connection: sqlite3.Connection, cita_id: int) -> dict[str, object] | None:
    row = connection.execute(
        """
        SELECT c.*, m.nombre AS mascota, v.nombre AS veterinario
        FROM citas c
        JOIN mascotas m ON m.id = c.mascota_id
        JOIN veterinarios v ON v.id = c.veterinario_id
        WHERE c.id = ?
        """,
        (cita_id,),
    ).fetchone()
    return dict(row) if row is not None else None


@router.get("/citas/")
def listar_citas(
    desde: date | None = None,
    hasta: date | None = None,
    connection: sqlite3.Connection = Depends(get_db),
) -> list[dict[str, object]]:
    conditions: list[str] = []
    values: list[str] = []
    if desde is not None:
        conditions.append("date(c.fecha_hora) >= ?")
        values.append(desde.isoformat())
    if hasta is not None:
        conditions.append("date(c.fecha_hora) <= ?")
        values.append(hasta.isoformat())
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    rows = connection.execute(
        f"""
        SELECT c.*, m.nombre AS mascota, v.nombre AS veterinario
        FROM citas c
        JOIN mascotas m ON m.id = c.mascota_id
        JOIN veterinarios v ON v.id = c.veterinario_id
        {where}
        ORDER BY c.fecha_hora DESC
        """,
        values,
    ).fetchall()
    return [dict(row) for row in rows]


@router.post("/citas/", status_code=status.HTTP_201_CREATED)
def crear_cita(
    datos: CitaEntrada,
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, object]:
    if connection.execute(
        "SELECT 1 FROM mascotas WHERE id = ?", (datos.mascota_id,)
    ).fetchone() is None:
        raise HTTPException(status_code=404, detail="No se encontró la mascota.")
    if connection.execute(
        "SELECT 1 FROM veterinarios WHERE id = ? AND activo = 1",
        (datos.veterinario_id,),
    ).fetchone() is None:
        raise HTTPException(status_code=404, detail="No se encontró el veterinario.")
    cursor = connection.execute(
        """
        INSERT INTO citas (mascota_id, veterinario_id, fecha_hora, motivo, estado)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            datos.mascota_id,
            datos.veterinario_id,
            datos.fecha_hora.isoformat(sep=" ", timespec="minutes"),
            datos.motivo,
            datos.estado,
        ),
    )
    connection.commit()
    return _cita_por_id(connection, cursor.lastrowid) or {}


@router.put("/citas/{cita_id}")
def actualizar_cita(
    cita_id: int,
    datos: CitaEntrada,
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, object]:
    if connection.execute(
        "SELECT 1 FROM mascotas WHERE id = ?", (datos.mascota_id,)
    ).fetchone() is None:
        raise HTTPException(status_code=404, detail="No se encontró la mascota.")
    if connection.execute(
        "SELECT 1 FROM veterinarios WHERE id = ? AND activo = 1",
        (datos.veterinario_id,),
    ).fetchone() is None:
        raise HTTPException(status_code=404, detail="No se encontró el veterinario.")
    cursor = connection.execute(
        """
        UPDATE citas
        SET mascota_id = ?, veterinario_id = ?, fecha_hora = ?, motivo = ?, estado = ?
        WHERE id = ?
        """,
        (
            datos.mascota_id,
            datos.veterinario_id,
            datos.fecha_hora.isoformat(sep=" ", timespec="minutes"),
            datos.motivo,
            datos.estado,
            cita_id,
        ),
    )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="No se encontró la cita.")
    connection.commit()
    return _cita_por_id(connection, cita_id) or {}


@router.delete("/citas/{cita_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cita(
    cita_id: int,
    connection: sqlite3.Connection = Depends(get_db),
) -> Response:
    cursor = connection.execute("DELETE FROM citas WHERE id = ?", (cita_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="No se encontró la cita.")
    connection.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/vacunas/")
def listar_vacunas(
    mascota_id: int | None = None,
    connection: sqlite3.Connection = Depends(get_db),
) -> list[dict[str, object]]:
    where = "WHERE va.mascota_id = ?" if mascota_id is not None else ""
    params = (mascota_id,) if mascota_id is not None else ()
    rows = connection.execute(
        f"""
        SELECT va.*, m.nombre AS mascota
        FROM vacunas_aplicadas va
        JOIN mascotas m ON m.id = va.mascota_id
        {where}
        ORDER BY va.fecha DESC
        """,
        params,
    ).fetchall()
    return [dict(row) for row in rows]


@router.get("/vacunas/proximas")
def listar_vacunas_proximas(
    dias: int = Query(default=30, ge=1, le=365),
    connection: sqlite3.Connection = Depends(get_db),
) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT va.*, m.nombre AS mascota
        FROM vacunas_aplicadas va
        JOIN mascotas m ON m.id = va.mascota_id
        WHERE va.proxima_dosis BETWEEN date('now') AND date('now', ?)
        ORDER BY va.proxima_dosis
        """,
        (f"+{dias} days",),
    ).fetchall()
    return [dict(row) for row in rows]


@router.post("/vacunas/", status_code=status.HTTP_201_CREATED)
def crear_vacuna(
    datos: VacunaEntrada,
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, object]:
    if connection.execute(
        "SELECT 1 FROM mascotas WHERE id = ?", (datos.mascota_id,)
    ).fetchone() is None:
        raise HTTPException(status_code=404, detail="No se encontró la mascota.")
    cursor = connection.execute(
        """
        INSERT INTO vacunas_aplicadas (mascota_id, vacuna, fecha, proxima_dosis)
        VALUES (?, ?, ?, ?)
        """,
        (
            datos.mascota_id,
            datos.vacuna,
            datos.fecha.isoformat(),
            datos.proxima_dosis.isoformat() if datos.proxima_dosis else None,
        ),
    )
    connection.commit()
    row = connection.execute(
        """
        SELECT va.*, m.nombre AS mascota FROM vacunas_aplicadas va
        JOIN mascotas m ON m.id = va.mascota_id WHERE va.id = ?
        """,
        (cursor.lastrowid,),
    ).fetchone()
    return dict(row)


@router.put("/vacunas/{vacuna_id}")
def actualizar_vacuna(
    vacuna_id: int,
    datos: VacunaEntrada,
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, object]:
    if connection.execute(
        "SELECT 1 FROM mascotas WHERE id = ?", (datos.mascota_id,)
    ).fetchone() is None:
        raise HTTPException(status_code=404, detail="No se encontró la mascota.")
    cursor = connection.execute(
        """
        UPDATE vacunas_aplicadas
        SET mascota_id = ?, vacuna = ?, fecha = ?, proxima_dosis = ?
        WHERE id = ?
        """,
        (
            datos.mascota_id,
            datos.vacuna,
            datos.fecha.isoformat(),
            datos.proxima_dosis.isoformat() if datos.proxima_dosis else None,
            vacuna_id,
        ),
    )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="No se encontró el registro de vacuna.")
    connection.commit()
    row = connection.execute(
        """
        SELECT va.*, m.nombre AS mascota FROM vacunas_aplicadas va
        JOIN mascotas m ON m.id = va.mascota_id WHERE va.id = ?
        """,
        (vacuna_id,),
    ).fetchone()
    return dict(row)


@router.delete("/vacunas/{vacuna_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_vacuna(
    vacuna_id: int,
    connection: sqlite3.Connection = Depends(get_db),
) -> Response:
    cursor = connection.execute(
        "DELETE FROM vacunas_aplicadas WHERE id = ?", (vacuna_id,)
    )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="No se encontró el registro de vacuna.")
    connection.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/lotes-farmacia/")
def listar_lotes_farmacia(
    connection: sqlite3.Connection = Depends(get_db),
) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT l.*, p.nombre AS producto
        FROM lotes_farmacia l
        JOIN productos_veterinarios p ON p.id = l.producto_id
        ORDER BY l.vencimiento, p.nombre COLLATE NOCASE
        """
    ).fetchall()
    return [dict(row) for row in rows]


@router.get("/lotes-farmacia/alertas")
def alertas_lotes_farmacia(
    dias: int = Query(default=90, ge=1, le=365),
    connection: sqlite3.Connection = Depends(get_db),
) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT l.*, p.nombre AS producto
        FROM lotes_farmacia l
        JOIN productos_veterinarios p ON p.id = l.producto_id
        WHERE l.vencimiento <= date('now', ?)
        ORDER BY l.vencimiento, p.nombre COLLATE NOCASE
        """,
        (f"+{dias} days",),
    ).fetchall()
    return [dict(row) for row in rows]


@router.post(
    "/lotes-farmacia/",
    status_code=status.HTTP_201_CREATED,
)
def crear_lote_farmacia(
    datos: LoteFarmaciaEntrada,
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, object]:
    if connection.execute(
        "SELECT 1 FROM productos_veterinarios WHERE id = ?", (datos.producto_id,)
    ).fetchone() is None:
        raise HTTPException(status_code=404, detail="No se encontró el producto.")
    cursor = connection.execute(
        """
        INSERT INTO lotes_farmacia
            (producto_id, numero_lote, proveedor, vencimiento, stock)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            datos.producto_id,
            datos.numero_lote,
            datos.proveedor,
            datos.vencimiento.isoformat(),
            datos.stock,
        ),
    )
    connection.commit()
    row = connection.execute(
        """
        SELECT l.*, p.nombre AS producto FROM lotes_farmacia l
        JOIN productos_veterinarios p ON p.id = l.producto_id WHERE l.id = ?
        """,
        (cursor.lastrowid,),
    ).fetchone()
    return dict(row)


@router.put("/lotes-farmacia/{lote_id}")
def actualizar_lote_farmacia(
    lote_id: int,
    datos: LoteFarmaciaEntrada,
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, object]:
    if connection.execute(
        "SELECT 1 FROM productos_veterinarios WHERE id = ?", (datos.producto_id,)
    ).fetchone() is None:
        raise HTTPException(status_code=404, detail="No se encontró el producto.")
    cursor = connection.execute(
        """
        UPDATE lotes_farmacia
        SET producto_id = ?, numero_lote = ?, proveedor = ?, vencimiento = ?, stock = ?
        WHERE id = ?
        """,
        (
            datos.producto_id,
            datos.numero_lote,
            datos.proveedor,
            datos.vencimiento.isoformat(),
            datos.stock,
            lote_id,
        ),
    )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="No se encontró el lote.")
    connection.commit()
    row = connection.execute(
        """
        SELECT l.*, p.nombre AS producto FROM lotes_farmacia l
        JOIN productos_veterinarios p ON p.id = l.producto_id WHERE l.id = ?
        """,
        (lote_id,),
    ).fetchone()
    return dict(row)


@router.delete("/lotes-farmacia/{lote_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_lote_farmacia(
    lote_id: int,
    connection: sqlite3.Connection = Depends(get_db),
) -> Response:
    cursor = connection.execute("DELETE FROM lotes_farmacia WHERE id = ?", (lote_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="No se encontró el lote.")
    connection.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
