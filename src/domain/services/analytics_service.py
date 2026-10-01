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

        if batch.shift_end is not None:
            elapsed_hours = (batch.shift_end - batch.shift_start).total_seconds() / 3600
        else:
            elapsed_hours = (
                datetime.now(timezone.utc) - batch.shift_start
            ).total_seconds() / 3600

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

    async def compare_batches(self, batch_ids: List[int]) -> dict:
        batches = await self.repository.get_by_ids(batch_ids)

        found = {batch.id for batch in batches}
        missing = set(batch_ids) - found

        comparison = []
        for b in batches:
            stats = calculate_production_stats(b.products)

            end = b.shift_end if b.shift_end else datetime.now(timezone.utc)
            duration_hours = (end - b.shift_start).total_seconds() / 3600
            products_per_hour = (
                round(stats["aggregated"] / duration_hours, 2)
                if duration_hours > 0
                else 0
            )

            comparison.append(
                {
                    "batch_id": b.id,
                    "batch_number": b.batch_number,
                    "total_products": stats["total_products"],
                    "aggregated": stats["aggregated"],
                    "rate": stats["aggregation_rate"],
                    "duration_hours": duration_hours,
                    "products_per_hour": products_per_hour,
                }
            )

        n = len(comparison)
        avg_rate = round(sum(c["rate"] for c in comparison) / n, 2) if n > 0 else 0
        avg_products_per_hour = (
            round(sum(c["products_per_hour"] for c in comparison) / n, 2)
            if n > 0
            else 0
        )

        return {
            "comparison": comparison,
            "summary": {
                "avg_rate": avg_rate,
                "avg_products_per_hour": avg_products_per_hour,
                "not_found": len(missing),
            },
        }
