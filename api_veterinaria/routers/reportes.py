import csv
from datetime import date
from io import StringIO
import sqlite3
from typing import Literal

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from database import get_db

router = APIRouter(prefix="/reportes", tags=["Informes"])


@router.get("/resumen")
def resumen(
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, int | float]:
    appointments = connection.execute(
        """
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN estado = 'programada' THEN 1 ELSE 0 END) AS programadas,
            SUM(CASE WHEN estado = 'atendida' THEN 1 ELSE 0 END) AS atendidas,
            SUM(CASE WHEN estado = 'cancelada' THEN 1 ELSE 0 END) AS canceladas
        FROM citas
        """
    ).fetchone()
    inventory = connection.execute(
        """
        SELECT
            SUM(CASE WHEN activo = 1 AND stock <= 3 THEN 1 ELSE 0 END) AS stock_bajo,
            COALESCE(SUM(precio * stock), 0) AS valor_inventario
        FROM productos_veterinarios
        """
    ).fetchone()
    return {
        "citas_total": appointments["total"] or 0,
        "citas_programadas": appointments["programadas"] or 0,
        "citas_atendidas": appointments["atendidas"] or 0,
        "citas_canceladas": appointments["canceladas"] or 0,
        "vacunas_proximas": connection.execute(
            """
            SELECT COUNT(*) FROM vacunas_aplicadas
            WHERE proxima_dosis BETWEEN date('now') AND date('now', '+30 days')
            """
        ).fetchone()[0],
        "productos_stock_bajo": inventory["stock_bajo"] or 0,
        "lotes_por_vencer": connection.execute(
            """
            SELECT COUNT(*) FROM lotes_farmacia
            WHERE vencimiento <= date('now', '+90 days')
            """
        ).fetchone()[0],
        "valor_inventario": inventory["valor_inventario"],
    }


@router.get("/descargar")
def descargar_informe(
    tipo: Literal["citas", "vacunas", "inventario"],
    connection: sqlite3.Connection = Depends(get_db),
) -> Response:
    queries = {
        "citas": (
            "Citas",
            """
            SELECT c.fecha_hora, m.nombre, v.nombre, c.motivo, c.estado
            FROM citas c
            JOIN mascotas m ON m.id = c.mascota_id
            JOIN veterinarios v ON v.id = c.veterinario_id
            ORDER BY c.fecha_hora DESC
            """,
        ),
        "vacunas": (
            "Vacunas",
            """
            SELECT m.nombre, va.vacuna, va.fecha, va.proxima_dosis
            FROM vacunas_aplicadas va
            JOIN mascotas m ON m.id = va.mascota_id
            ORDER BY va.fecha DESC
            """,
        ),
        "inventario": (
            "Inventario de farmacia",
            """
            SELECT p.nombre, p.categoria, p.stock, p.precio, l.numero_lote,
                   l.proveedor, l.vencimiento, l.stock
            FROM productos_veterinarios p
            LEFT JOIN lotes_farmacia l ON l.producto_id = p.id
            ORDER BY p.nombre COLLATE NOCASE, l.vencimiento
            """,
        ),
    }
    _, query = queries[tipo]
    output = StringIO()
    writer = csv.writer(output)
    if tipo == "citas":
        writer.writerow(("Fecha y hora", "Mascota", "Veterinario", "Motivo", "Estado"))
    elif tipo == "vacunas":
        writer.writerow(("Mascota", "Vacuna", "Fecha aplicada", "Próxima dosis"))
    else:
        writer.writerow(
            (
                "Producto",
                "Categoría",
                "Existencias",
                "Precio",
                "Lote",
                "Proveedor",
                "Vencimiento",
                "Existencias del lote",
            )
        )
    writer.writerows(connection.execute(query).fetchall())
    filename = f"zeus-vet-{tipo}-{date.today().isoformat()}.csv"
    return Response(
        content="\ufeff" + output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
