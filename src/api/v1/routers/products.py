from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List
from ....core.database import get_db 
from ..schemas.product import ProductCreate, ProductResponse
from ....data.repositories.product_repository import ProductRepository
from ....domain.services.product_service import ProductService


router = APIRouter(prefix="/products", tags=["products"])


@router.get("/{id}", response_model=ProductResponse)
async def get_product_by_id(
    product_id: int,
    session: Annotated[AsyncSession, Depends(get_db)]
):
    repository = ProductRepository(session)
    service = ProductService(repository)
    return await service.get_by_id(product_id)

@router.get("/batch/{batch_id}", response_model=List[ProductResponse])
async def get_product_by_batch_id(
    batch_id: int,
    session: Annotated[AsyncSession, Depends(get_db)]
):
    repository = ProductRepository(session)
    service = ProductService(repository)
    return await service.get_by_batch_id(batch_id)

@router.post("/", response_model=ProductResponse)
async def create_product(
    data: ProductCreate,
    session: Annotated[AsyncSession, Depends(get_db)]
):
    repository = ProductRepository(session)
    service = ProductService(repository)
    return await service.create(data)