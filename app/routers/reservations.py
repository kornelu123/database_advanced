from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
from datetime import datetime
from app import schemas, queries
from app.dependencies import get_current_user
from app.database import get_connection

router = APIRouter(prefix="/reservations", tags=["reservations"])

@router.post("/", response_model=schemas.ReservationResponse)
async def create_reservation(
    reservation: schemas.ReservationCreate,
    current_user = Depends(get_current_user)
):
    item = await queries.get_item(reservation.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item["user_id"] == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot reserve your own item")
    db_reservation = await queries.create_reservation(reservation.item_id, current_user["id"])
    if not db_reservation:
        raise HTTPException(status_code=409, detail="Item not available or already reserved")
    return db_reservation

@router.get("/me", response_model=List[schemas.ReservationResponse])
async def get_my_reservations(
    skip: int = 0,
    limit: int = 50,
    current_user = Depends(get_current_user)
):
    reservations = await queries.get_user_reservations(current_user["id"], skip, limit)
    return reservations

@router.post("/{reservation_id}/confirm", response_model=schemas.ReservationResponse)
async def confirm_reservation(
    reservation_id: int,
    current_user = Depends(get_current_user)
):
    reservation = await queries.get_reservation(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    item = await queries.get_item(reservation["item_id"])
    if item["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only item owner can confirm")
    if reservation["status"] != "active":
        raise HTTPException(status_code=400, detail="Reservation not active")
    if reservation["expires_at"] < datetime.utcnow():
        await queries.update_reservation_status(reservation_id, "expired")
        raise HTTPException(status_code=400, detail="Reservation expired")
    updated = await queries.update_reservation_status(reservation_id, "confirmed")
    return updated

@router.post("/{reservation_id}/cancel", response_model=schemas.ReservationResponse)
async def cancel_reservation(
    reservation_id: int,
    current_user = Depends(get_current_user)
):
    reservation = await queries.get_reservation(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    item = await queries.get_item(reservation["item_id"])
    if reservation["user_id"] != current_user["id"] and item["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    if reservation["status"] not in ["active", "confirmed"]:
        raise HTTPException(status_code=400, detail="Cannot cancel this reservation")
    updated = await queries.update_reservation_status(reservation_id, "cancelled")
    return updated

@router.post("/{reservation_id}/take", response_model=schemas.ReservationResponse)
async def take_item(
    reservation_id: int,
    current_user = Depends(get_current_user)
):
    reservation = await queries.get_reservation(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    item = await queries.get_item(reservation["item_id"])
    if item["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only item owner can mark as taken")
    if reservation["status"] != "confirmed":
        raise HTTPException(status_code=400, detail="Reservation not confirmed")
    await queries.update_item(item["id"], {"status": "taken", "taken_at": datetime.utcnow(), "taken_by_id": reservation["user_id"]})
    updated = await queries.update_reservation_status(reservation_id, "taken")
    return updated

@router.post("/expire-old")
async def expire_old_reservations(background_tasks: BackgroundTasks):
    from datetime import datetime
    async def expire():
        async with get_connection() as conn:
            await conn.execute("UPDATE reservations SET status = 'expired' WHERE status = 'active' AND expires_at < NOW()")
    background_tasks.add_task(expire)
    return {"message": "Expiration task scheduled"}
