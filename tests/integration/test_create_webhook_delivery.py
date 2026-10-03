import pytest
from sqlalchemy import select
from src.data.repositories.webhook_repository import WebhookDeliveryRepository
from src.tasks.webhooks import create_webhook_delivery_task
from src.data.models.webhook import WebhookDelivery


def test_create_webhook_delivery(
    get_test_db_sync,
    create_subscription,
    create_batch_sync,
    httpx_mock,
    patch_get_session,
):
    batch = create_batch_sync(1)
    payload = {
        "id": batch.id,
        "batch_number": batch.batch_number,
        "batch_date": batch.batch_date.isoformat(),
        "nomenclature": batch.nomenclature,
        "work_center": batch.work_center_id,
    }

    sub = create_subscription
    httpx_mock.add_response(
        url=sub.url, method="POST", status_code=200, json={"ok": True}
    )

    create_webhook_delivery_task("batch_created", payload)

    stmt = select(WebhookDelivery).where(WebhookDelivery.subscription_id == sub.id)
    hookdel = get_test_db_sync.execute(stmt).scalar_one()

    assert hookdel.status.value == "success"
    assert hookdel.event_type == "batch_created"
    assert hookdel.response_status == 200
