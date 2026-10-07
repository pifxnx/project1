import os
from pathlib import Path
from uuid import uuid4
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from ..data.models.batch import Batch
from ..celery_app import celery_app, get_session
from ..core.storage import minio
from ..utils.excel_generator import generate_batch_report_excel
from ..utils.pdf_generator import generate_batch_report_pdf
from ..utils.email_sender import send_email


def get_batch_report_data(batch_id: int, session: Session):
    stmt = select(Batch).where(Batch.id == batch_id).options(joinedload(Batch.products))
    batch = session.execute(stmt).unique().scalar_one_or_none()

    if batch is None:
        raise ValueError(f"Batch {batch_id} not found")

    products = [
        {
            "id": p.id,
            "unique_code": p.unique_code,
            "is_aggregated": p.is_aggregated,
            "aggregated_at": (
                p.aggregated_at.replace(tzinfo=None) if p.aggregated_at else None
            ),
        }
        for p in batch.products
    ]
    total = len(products)
    aggregated = sum(1 for p in products if p["is_aggregated"])

    batch_info = {
        "Номер партии": batch.batch_number,
        "Дата партии": batch.batch_date.isoformat(),
        "Статус": batch.is_closed,
        "Рабочий центр": batch.work_center_id,
        "Смена": batch.shift,
        "Бригада": batch.team,
        "Номенклатура": batch.nomenclature,
        "Начало смены": batch.shift_start.replace(tzinfo=None),
        "Окончание смены": (
            batch.shift_end.replace(tzinfo=None) if batch.shift_end else None
        ),
    }

    stats = {
        "Всего продукции": total,
        "Аггрегировано": aggregated,
        "Осталось": total - aggregated,
        "Процент выполнения": f"{round(aggregated / total * 100, 2)}" if total else 0,
    }

    return batch_info, products, stats


@celery_app.task(bind=True, max_retries=3)
def generate_batch_report(
    self, batch_id: int, format: str = "excel", email: str | None = None
):
    generators = {
        "excel": (generate_batch_report_excel, "xlsx"),
        "pdf": (generate_batch_report_pdf, "pdf"),
    }
    if format not in generators:
        raise ValueError("форматы только 'excel' и 'pdf'")
    generator, ext = generators[format]
    with get_session() as session:
        data = get_batch_report_data(batch_id, session)

    batch_info, products, stats = data
    file_name = f"batch_{batch_info['Номер партии']}_{uuid4().hex}_report.{ext}"
    file_path = f"/tmp/{file_name}"
    try:
        generator(batch_info, products, stats, file_path)

        file_url = minio.upload_file("reports", file_path, file_name)
        file_size = os.path.getsize(file_path)
        if email is not None:
            send_email(
                to=email,
                subject=f"Отчет по партии {batch_info['Номер партии']}",
                body=f"Отчет по партии {batch_info['Номер партии']} в формате {format}",
                file_path=Path(file_path),
            )
    finally:
        os.remove(file_path)

    return {
        "success": True,
        "file_url": file_url,
        "file_name": file_name,
        "file_size": file_size,
    }
