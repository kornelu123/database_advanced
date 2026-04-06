from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app import schemas, queries

router = APIRouter(prefix="/locations", tags=["locations"])

@router.get("/voivodeships", response_model=List[schemas.VoivodeshipResponse])
async def get_voivodeships():
    return await queries.get_voivodeships()

@router.get("/voivodeships/{voivodeship_id}/cities", response_model=List[schemas.CityResponse])
async def get_cities_by_voivodeship(voivodeship_id: int):
    return await queries.get_cities_by_voivodeship(voivodeship_id)

@router.get("/cities/{city_id}", response_model=schemas.CityResponse)
async def get_city(city_id: int):
    city = await queries.get_city(city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city
