from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from decimal import Decimal
from app import schemas, queries
from app.dependencies import get_current_user

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/search", response_model=List[schemas.ItemResponse])
async def search_items(
    category_ids: Optional[List[int]] = Query(None),
    city_id: Optional[int] = None,
    voivodeship_id: Optional[int] = None,
    query: Optional[str] = None,
    min_rating: Optional[Decimal] = None,
    status: str = "active",
    skip: int = 0,
    limit: int = 20
):
    filters = {
        "category_ids": category_ids,
        "city_id": city_id,
        "voivodeship_id": voivodeship_id,
        "query": query,
        "min_rating": min_rating,
        "status": status,
        "skip": skip,
        "limit": limit
    }
    items = await queries.search_items(filters)
    return items

@router.get("/{item_id}", response_model=schemas.ItemResponse)
async def get_item(item_id: int):
    item = await queries.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    # Zwiększ licznik wyświetleń (dedykowana funkcja, brak ogólnego UPDATE)
    await queries.increment_item_views(item_id)
    # Pobierz ponownie, aby zwrócić zaktualizowany widok (opcjonalnie)
    item = await queries.get_item(item_id)
    return item

@router.post("/", response_model=schemas.ItemResponse)
async def create_item(
    item: schemas.ItemCreate,
    current_user = Depends(get_current_user)
):
    new_item = await queries.create_item(
        user_id=current_user["id"],
        title=item.title,
        description=item.description,
        condition=item.condition,
        quantity=item.quantity,
        city_id=item.city_id,
        street_hint=item.street_hint,
        category_ids=item.category_ids
    )
    return new_item

@router.put("/{item_id}", response_model=schemas.ItemResponse)
async def update_item(
    item_id: int,
    item_update: schemas.ItemUpdate,
    current_user = Depends(get_current_user)
):
    item = await queries.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    updated = await queries.update_item(item_id, item_update.model_dump(exclude_unset=True))
    return updated

@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    current_user = Depends(get_current_user)
):
    item = await queries.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    await queries.delete_item(item_id)
    return {"message": "Item deleted"}

@router.post("/{item_id}/photos", response_model=schemas.ItemPhotoResponse)
async def add_photo(
    item_id: int,
    photo: schemas.ItemPhotoBase,
    current_user = Depends(get_current_user)
):
    item = await queries.get_item(item_id)
    if not item or item["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    new_photo = await queries.add_photo(
        item_id=item_id,
        url=photo.url,
        storage_key=photo.storage_key,
        is_main=photo.is_main,
        position=photo.position,
        width=photo.width,
        height=photo.height
    )
    return new_photo

@router.delete("/photos/{photo_id}")
async def delete_photo(
    photo_id: int,
    current_user = Depends(get_current_user)
):
    photo = await queries.get_photo(photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    item = await queries.get_item(photo["item_id"])
    if item["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    await queries.delete_photo(photo_id)
    return {"message": "Photo deleted"}
