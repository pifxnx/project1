import pytest
from sqlalchemy import select
from src.data.repositories.webhook_repository import WebhookDeliveryRepository
from src.tasks.webhooks import create_webhook_delivery_task
from src.data.models.webhook import WebhookDelivery



def test_create_webhook_delivery(get_test_db_sync, create_subscription,
                                 create_batch, httpx_mock, patch_get_session):
    payload = {
        "id": create_batch.id,
        "batch_number": create_batch.batch_number,
        "batch_date": create_batch.batch_date.isoformat(),
        "nomenclature": create_batch.nomenclature,
        "work_center": create_batch.work_center_id
    }

    sub = create_subscription
    httpx_mock.add_response(
        url=sub.url,
        method="POST",
        status_code=200,
        json={"ok": True}
    )

    create_webhook_delivery_task("batch_created", payload)

    stmt = (select(WebhookDelivery)
            .where(WebhookDelivery.subscription_id == sub.id))
    hookdel = get_test_db_sync.execute(stmt).scalar_one()

    assert hookdel.status.value == "success"
    assert hookdel.event_type == "batch_created"
    assert hookdel.response_status == 200
