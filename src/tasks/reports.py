import os
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from ..data.models.batch import Batch
from ..celery_app import celery_app, get_session
from ..core.storage import minio
from ..utils.excel_generator import generate_batch_report_excel


def get_batch_report_data(batch_id: int, session: Session):
    stmt = (select(Batch)
            .where(Batch.id == batch_id)
            .options(joinedload(Batch.products)))
    batch = session.execute(stmt).unique().scalar_one_or_none()

    products = [
        {
            "id": p.id,
            "unique_code": p.unique_code,
            "is_aggregated": p.is_aggregated,
            "aggregated_at": p.aggregated_at
        }
        for p in batch.products
    ]
    total = len(products)
    aggregated = sum(1 for p in products if p["is_aggregated"])

    batch_info = {
        "Номер партии": batch.batch_number,
        "Дата партии": batch.batch_date,
        "Статус": batch.is_closed,
        "Рабочий центр": batch.work_center_id,
        "Смена": batch.shift,
        "Бригада": batch.team,
        "Номенклатура": batch.nomenclature,
        "Начало смены": batch.shift_start,
        "Окончание смены": batch.shift_end
    }

    stats = {
        "Всего продукции": total,
        "Аггрегировано": aggregated,
        "Осталось": total - aggregated,
        "Процент выполнения": f"{round(aggregated / total * 100, 2)}" if total else 0
    }

    return batch_info, products, stats
    


@celery_app.task(bind=True, max_retries=3)
def generate_batch_report(
    self,
    batch_id: int,
    format: str = "excel"
):
    with get_session() as session:
        data = get_batch_report_data(batch_id, session)

    batch_info, products, stats = data
    file_name = f"batch_{batch_info['Номер партии']}_report.xlsx"
    file_path = f"/tmp/{file_name}"
    try:
        generate_batch_report_excel(batch_info, products, stats, file_path)

        file_url = minio.upload_file("reports", file_path, file_name)
        file_size = os.path.getsize(file_path)
    finally:
        os.remove(file_path)

    return {
        "success": True,
        "file_url": file_url,
        "file_name": file_name,
        "file_size": file_size
    }