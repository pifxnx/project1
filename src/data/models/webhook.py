from sqlalchemy import ARRAY, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime, timezone
from ...core.database import Base 
import enum


class WebhookSubscription(Base):
    __tablename__ = "webhook_subsctriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str]
    events: Mapped[list[str]] = mapped_column(MutableList.as_mutable(ARRAY(String)))
    secret_key: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    retry_count: Mapped[int] = mapped_column(default=3)
    timeout: Mapped[int] = mapped_column(default=10)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
        )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
        )


class Status(enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"

class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("webhook_subscriptions.id"))
    event_type: Mapped[str]
    payload: Mapped[dict] = mapped_column(JSON)

    status: Mapped[str] = mapped_column(Enum(Status), default=Status.pending)
    attempts: Mapped[int] = mapped_column(default=0)
    response_status: Mapped[str | None]
    response_body: Mapped[str | None]
    error_message: Mapped[str | None]

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    subscription: Mapped["WebhookSubscription"] = relationship("WebhookSubscription")