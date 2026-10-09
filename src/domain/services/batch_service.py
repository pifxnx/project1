import os
from uuid import uuid4
from datetime import datetime, date, timezone
from asyncio import to_thread
from typing import List, Literal
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import UniqueViolationError, ForeignKeyViolationError
from ...data.repositories.batch_repository import BatchRepository
from ...api.v1.schemas.batch import (
    BatchCreate,
    BatchCreateRu,
    BatchResponse,
    BatchAlter,
)
from ...data.models.batch import Batch
from ..exceptions.batch_exception import (
    BatchNotFoundException,
    BatchAlreadyExistsException,
)
from ..exceptions.work_center_exception import WorkCenterNotFoundException
from ...tasks.webhooks import create_webhook_delivery_task
from ...tasks.reports import generate_batch_report
from ...tasks.imports import import_batches_task
from ...tasks.exports import export_batches_task
from ...core.storage import minio
from ...core.cache import invalidate_batch


class BatchService:
    def __init__(self, repository: BatchRepository):
        self.repository = repository

    async def create(self, data: BatchCreate) -> BatchResponse:
        batch = Batch(**data.model_dump())

        try:
            batch = await self.repository.create(batch)
        except IntegrityError as e:
            if isinstance(e.orig.__cause__, UniqueViolationError):
                raise BatchAlreadyExistsException() from e
            elif isinstance(e.orig.__cause__, ForeignKeyViolationError):
                raise WorkCenterNotFoundException(batch.work_center_id) from e
            raise

        create_webhook_delivery_task.delay(
            "batch_created",
            {
                "id": batch.id,
                "batch_number": batch.batch_number,
                "batch_date": batch.batch_date.isoformat(),
                "nomenclature": batch.nomenclature,
                "work_center": batch.work_center_id,
            },
        )
        await invalidate_batch(batch.id)

        return BatchResponse(
            id=batch.id,
            is_closed=batch.is_closed,
            batch_number=batch.batch_number,
            batch_date=batch.batch_date,
        )

    async def create_many(self, batches: List[BatchCreateRu]) -> dict:
        created, errors = await self.repository.create_many_batches(
            [batch.model_dump() for batch in batches]
        )
        for batch in created:
            create_webhook_delivery_task.delay(
                "batch_created",
                {
                    "id": batch.id,
                    "batch_number": batch.batch_number,
                    "batch_date": batch.batch_date.isoformat(),
                    "nomenclature": batch.nomenclature,
                    "work_center": batch.work_center_id,
                },
            )
        await invalidate_batch(0)
        return {
            "created": [BatchResponse.model_validate(batch) for batch in created],
            "errors": errors,
        }

    async def get_by_id(self, batch_id: int) -> BatchResponse:
        batch = await self.repository.get_by_id(batch_id)

        if not batch:
            raise BatchNotFoundException(batch_id)

        return BatchResponse.model_validate(batch)

    async def get_batches(
        self,
        is_closed: bool | None = None,
        batch_number: int | None = None,
        batch_date: date | None = None,
        work_center_id: int | None = None,
        shift: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> List[BatchResponse]:
        batches = await self.repository.get_with_filter(
            is_closed=is_closed,
            batch_number=batch_number,
            batch_date=batch_date,
            work_center_id=work_center_id,
            shift=shift,
            offset=offset,
            limit=limit,
        )

        return [BatchResponse.model_validate(batch) for batch in batches]

    async def update(self, id: int, data: BatchAlter) -> BatchResponse:
        batch, closed_now = await self.repository.update(id, data)
        if not batch:
            raise BatchNotFoundException(id)

        if closed_now:
            create_webhook_delivery_task.delay("batch_closed", {"id": batch.id})

        create_webhook_delivery_task.delay(
            "batch_updated",
            {
                "id": batch.id,
                "batch_number": batch.batch_number,
                "changes": data.model_dump(mode="json", exclude_unset=True),
            },
        )
        await invalidate_batch(batch.id)

        return BatchResponse.model_validate(batch)

    async def create_batch_report(
        self,
        batch_id: int,
        format: Literal["excel", "pdf"] = "excel",
        email: str | None = None,
    ):
        batch = await self.repository.get_by_id(batch_id)
        if not batch:
            raise BatchNotFoundException(batch_id)

        result = generate_batch_report.delay(batch_id, format, email)
        create_webhook_delivery_task.delay("report_generated", {"id": batch_id})

        return {"task_id": result.id, "status": result.status}


class ImportExportService:
    async def import_batch(self, data: bytes, filename: str):
        filename = os.path.basename(filename)
        object_name = f"{uuid4()}_{filename}"
        path = f"/tmp/{object_name}"

        with open(path, "wb") as f:
            f.write(data)

        try:
            await to_thread(minio.upload_file, "imports", path, object_name)
        finally:
            os.remove(path)

        result = import_batches_task.delay(object_name, path)

        return {"id": result.id, "status": result.status, "message": "Import started"}

    async def export_batches(self, data: dict):
        result = export_batches_task.delay(data["filters"], data["format"])

        return {"id": result.id, "status": result.status}
