from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UniqueConstraint, Index
from datetime import datetime, date


class Batch(Base):
    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    is_closed: Mapped[bool] = mapped_column(default=False)
    closed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    task_description: Mapped[str] = mapped_column(nullable=False)
    # work_center_id вместе с таблицей WorkCenter FK
    shift: Mapped[str] = mapped_column(nullable=False)
    team: Mapped[str]

    batch_number: Mapped[int] = mapped_column(nullable=False)
    batch_date: Mapped[date]

    nomenclature: Mapped[str]
    ekn_code: Mapped[str]

    shift_start: Mapped[datetime] = mapped_column(default=datetime.now)
    shift_end: Mapped[datetime] = mapped_column(default=datetime.now)

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)

    # products: Mapped[list[Product]] = relationship(back_populates="batch")
    # work_center: relationship -> WorkCenter

    __table_args__ = (
        UniqueConstraint("batch_number", "batch_date", name="uq_batch_number_date"),
        Index("idx_batch_closed", "is_closed"),
        Index("idx_batch_shift_times", "shift_start", "shift_end")
    )