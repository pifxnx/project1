from typing import List
from datetime import datetime, timezone, timedelta
from ...data.repositories.batch_repository import BatchRepository
from ..exceptions.batch_exception import BatchNotFoundException
from ...data.models.product import Product


def calculate_production_stats(products: List[Product]) -> dict:
    total = len(products)
    aggregated = sum(1 for p in products if p.is_aggregated)
    remaining = total - aggregated
    aggregation_rate = round(aggregated / total * 100, 2) if total else 0.0

    return {
        "total_products": total,
        "aggregated": aggregated,
        "remaining": remaining,
        "aggregation_rate": aggregation_rate,
    }


class AnalyticsService:
    def __init__(self, repository: BatchRepository):
        self.repository = repository

    async def get_batch_statistics(self, batch_id: int) -> dict:
        batch = await self.repository.get_by_id(batch_id)
        if not batch:
            raise BatchNotFoundException(batch_id)

        production_stats = calculate_production_stats(batch.products)

        elapsed_hours = (batch.shift_end - batch.shift_start).total_seconds() / 3600

        products_per_hour = (
            round(production_stats["aggregated"] / elapsed_hours, 2)
            if elapsed_hours > 0
            else 0
        )

        estimated_completion = None
        if products_per_hour > 0 and production_stats["remaining"] > 0:
            hours_left = production_stats["remaining"] / products_per_hour
            estimated_completion = (
                datetime.now(timezone.utc) + timedelta(hours=hours_left)
            ).isoformat()

        return {
            "batch_info": {
                "id": batch.id,
                "batch_number": batch.batch_number,
                "batch_date": batch.batch_date.isoformat(),
                "is_closed": batch.is_closed,
            },
            "production_stats": production_stats,
            "timeline": {
                "elapsed_hours": round(elapsed_hours, 2),
                "products_per_hour": products_per_hour,
                "estimated_completion": estimated_completion,
            },
            "team_performance": {
                "team": batch.team,
                "avg_products_per_hour": products_per_hour,
            },
        }
