import os
from ..celery_app import celery_app, get_session
from ..utils.excel_parser import parse_batches_excel
from ..core.storage import minio
from ..data.models.batch import Batch
from .webhooks import create_webhook_delivery_task
from ..api.v1.schemas.batch import BatchCreate
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation, NotNullViolation


@celery_app.task
def import_batches_task(
    object_name: str,
    path: str
):
    minio.download_file("imports", object_name, path)

    stats = {"total_rows": 0, "created": 0,
             "skipped": 0, "errors": []}
    try:
        with get_session() as session:
            for i, row in enumerate(parse_batches_excel(path), 1):
                stats["total_rows"] += 1
                try:
                    with session.begin_nested():
                        data = BatchCreate(**row)
                        session.add(Batch(**data.model_dump()))
                        session.flush()
                except ValidationError as e:
                    session.rollback()
                    stats["errors"].append({"row": i, "error": "validation error"})
                    stats["skipped"] += 1
                except IntegrityError as e:
                    session.rollback()
                    error = e.orig
                    if isinstance(error, UniqueViolation):
                        reason = "duplicate batch number and date"
                    elif isinstance(error, NotNullViolation):
                        reason = "not null violation"
                    else:
                        reason = str(error)
                    stats["errors"].append({"row": i, "error": reason})
                    stats["skipped"] += 1
                else:
                    stats["created"] += 1

            session.commit()

    finally:
        os.remove(path)

    create_webhook_delivery_task.delay(
        "batch_imported",
        stats
    )