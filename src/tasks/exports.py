import os
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from datetime import date
from ..data.models.batch import Batch
from ..celery_app import celery_app, get_session
from ..utils.excel_generator import generate_export_batches_excel
from ..core.storage import minio
from .webhooks import create_webhook_delivery_task



def get_batches_filters(
    session: Session,
    is_closed: bool | None = None,
    batch_number: int | None = None,
    batch_date_from: date | None = None,
    batch_date_to: date | None = None,
    work_center_id: int | None = None,
    shift: str | None = None,
) -> list[Batch]:
    stmt = select(Batch).options(selectinload(Batch.products))

    if is_closed is not None:
        stmt = stmt.where(Batch.is_closed == is_closed)
    if batch_number is not None:
        stmt = stmt.where(Batch.batch_number == batch_number)
    if batch_date_from is not None:
        stmt = stmt.where(Batch.batch_date >= batch_date_from)
    if batch_date_to is not None:
        stmt = stmt.where(Batch.batch_date <= batch_date_to)
    if work_center_id is not None:
        stmt = stmt.where(Batch.work_center_id == work_center_id)
    if shift is not None:
        stmt = stmt.where(Batch.shift == shift)

    result = session.execute(stmt)
    return list(result.scalars().unique().all())

@celery_app.task
def export_batches_task(object_name: str, path: str, filters: dict):
    with get_session() as session:
        batches = get_batches_filters(session, **filters)

        rows = [
            {
                "batch_number": b.batch_number,
                "batch_date": b.batch_date,
                "is_closed": b.is_closed,
                "work_center_id": b.work_center_id,
                "shift": b.shift,
                "team": b.team,
                "nomenclature": b.nomenclature,
                "ekn_code": b.ekn_code,
                "total_products": len(b.products),
                "aggregated_products": sum(1 for p in b.products if p.is_aggregated)
            }
            for b in batches
        ]

        object_name = f"{uuid4()}_batch_export.xlsx"
        path = f"/tmp/{uuid4()}.xlsx"

        try:
            generate_export_batches_excel(rows, path)
            file_url = minio.upload_file("exports", path, object_name)
        finally:
            os.remove(path)

        create_webhook_delivery_task.delay(
            "batches_exported",
            {"file_url": file_url, "total": len(rows)}
        )

        return {"file_url": file_url, "total": len(rows)}