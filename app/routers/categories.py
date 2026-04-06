from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app import schemas, queries
from app.dependencies import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=List[schemas.CategoryResponse])
async def get_categories():
    return await queries.get_categories()

@router.get("/{category_id}", response_model=schemas.CategoryResponse)
async def get_category(category_id: int):
    category = await queries.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=schemas.CategoryResponse)
async def create_category(
    category: schemas.CategoryBase,
    current_user = Depends(get_current_user)
):
    return await queries.create_category(category.name, category.icon_name, category.description)
