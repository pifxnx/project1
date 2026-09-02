from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UniqueConstraint, Index, DateTime, ForeignKey
from datetime import datetime, date
from typing import List


class Batch(Base):
    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    is_closed: Mapped[bool] = mapped_column(default=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    task_description: Mapped[str] = mapped_column(nullable=False)
    work_center_id: Mapped[int] = mapped_column(ForeignKey("work_centers.id"))
    shift: Mapped[str] = mapped_column(nullable=False)
    team: Mapped[str]

    batch_number: Mapped[int] = mapped_column(nullable=False)
    batch_date: Mapped[date]

    nomenclature: Mapped[str]
    ekn_code: Mapped[str]

    shift_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    shift_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)

    products: Mapped[List["Product"]] = relationship("Product", back_populates="batch")
    work_center: Mapped["WorkCenter"] = relationship("WorkCenter")

    __table_args__ = (
        UniqueConstraint("batch_number", "batch_date", name="uq_batch_number_date"),
        Index("idx_batch_closed", "is_closed"),
        Index("idx_batch_shift_times", "shift_start", "shift_end")
    )