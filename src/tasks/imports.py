from datetime import datetime, timezone
import os

from ..celery_app import celery_app, get_session
from ..utils.excel_parser import parse_batches_excel
from ..utils.csv_parser import parse_batches_csv
from ..core.storage import minio
from ..data.models.batch import Batch
from .webhooks import create_webhook_delivery_task
from ..api.v1.schemas.batch import BatchCreate
from ..data.models.work_center import WorkCenter
from ..core.cache import invalidate_batch_sync
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError


@celery_app.task
def import_batches_task(object_name: str, path: str):
    minio.download_file("imports", object_name, path)

    if object_name.endswith(".csv"):
        parser = parse_batches_csv
    elif object_name.endswith(".xlsx"):
        parser = parse_batches_excel
    else:
        raise ValueError("поддерживаются только файлы .csv и .xlsx")

    stats = {"total_rows": 0, "created": 0, "skipped": 0, "errors": []}
    try:
        with get_session() as session:
            rows = parser(path)
            for i, row in enumerate(rows, 1):
                stats["total_rows"] += 1
                try:
                    row = {k: (None if v == "" else v) for k, v in row.items()}
                    work_center_identifier = row.pop("work_center_identifier", None)
                    if work_center_identifier is not None:
                        work_center_identifier = str(work_center_identifier).strip()
                    work_center_name = row.pop("work_center_name", None)
                    if not work_center_identifier:
                        raise ValueError("work center identifier is empty")

                    work_center_id = session.execute(
                        select(WorkCenter.id).where(
                            WorkCenter.identifier == work_center_identifier
                        )
                    ).scalar_one_or_none()
                    if work_center_id is None:
                        work_center = WorkCenter(
                            identifier=work_center_identifier,
                            name=work_center_name or str(work_center_identifier),
                        )
                        session.add(work_center)
                        session.flush()
                        work_center_id = work_center.id

                    row["work_center_id"] = work_center_id
                    with session.begin_nested():
                        data = BatchCreate(**row)
                        obj = Batch(**data.model_dump())
                        if obj.is_closed and obj.closed_at is None:
                            obj.closed_at = datetime.now(timezone.utc)

                        session.add(obj)
                        session.flush()
                except ValidationError as e:
                    stats["errors"].append(
                        {
                            "row": i,
                            "error": "; ".join(
                                f"{err['loc'][0] if err['loc'] else ''}: {err['msg']}"
                                for err in e.errors()
                            ),
                        }
                    )
                    stats["skipped"] += 1
                except DBAPIError as e:
                    stats["errors"].append(
                        {"row": i, "error": type(e.orig).__name__}
                    )
                    stats["skipped"] += 1
                except ValueError as e:
                    stats["errors"].append({"row": i, "error": str(e)})
                    stats["skipped"] += 1
                else:
                    stats["created"] += 1

            session.commit()

            invalidate_batch_sync(0)
    finally:
        os.remove(path)

    create_webhook_delivery_task.delay("import_completed", stats)

    return stats
