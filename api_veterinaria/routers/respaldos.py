from contextlib import closing
from datetime import datetime
from pathlib import Path
import sqlite3
import tempfile

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

import database

router = APIRouter(prefix="/respaldos", tags=["Respaldos"])


@router.post("/", response_class=StreamingResponse)
def descargar_respaldo() -> StreamingResponse:
    with tempfile.NamedTemporaryFile(prefix="zeus-vet-", suffix=".db", delete=False) as file:
        backup_path = Path(file.name)
    try:
        with closing(sqlite3.connect(database.DATABASE_PATH, timeout=10)) as source:
            with closing(sqlite3.connect(backup_path)) as destination:
                source.backup(destination)
    except (sqlite3.Error, OSError):
        backup_path.unlink(missing_ok=True)
        raise

    filename = f"zeus-vet-respaldo-{datetime.now():%Y-%m-%d-%H%M}.db"
    def transmitir_respaldo():
        try:
            with backup_path.open("rb") as backup_file:
                while chunk := backup_file.read(64 * 1024):
                    yield chunk
        finally:
            backup_path.unlink(missing_ok=True)

    return StreamingResponse(
        transmitir_respaldo(),
        media_type="application/vnd.sqlite3",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
