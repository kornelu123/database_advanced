from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from enum import Enum

class UserBase(BaseModel):
    username: str
    display_name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    city: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    rating: Optional[Decimal] = None
    is_active: bool
    created_at: datetime
    last_active_at: datetime
    model_config = ConfigDict(from_attributes=True)

class VoivodeshipBase(BaseModel):
    name: str

class VoivodeshipResponse(VoivodeshipBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CityBase(BaseModel):
    voivodeship_id: int
    name: str
    postal_code_prefix: Optional[str] = None

class CityResponse(CityBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CategoryBase(BaseModel):
    name: str
    icon_name: Optional[str] = None
    description: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ItemPhotoBase(BaseModel):
    url: str
    storage_key: Optional[str] = None
    is_main: Optional[bool] = None
    position: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None

class ItemPhotoResponse(ItemPhotoBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    condition: Optional[str] = None
    quantity: Optional[int] = 1
    city_id: Optional[int] = None
    street_hint: Optional[str] = None

class ItemCreate(ItemBase):
    category_ids: List[int] = []

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    condition: Optional[str] = None
    quantity: Optional[int] = None
    city_id: Optional[int] = None
    street_hint: Optional[str] = None
    status: Optional[str] = None

class ItemResponse(ItemBase):
    id: int
    user_id: int
    status: str
    views_count: int
    favorites_count: int
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    taken_at: Optional[datetime] = None
    taken_by_id: Optional[int] = None
    photos: List[ItemPhotoResponse] = []
    categories: List[CategoryResponse] = []
    city_obj: Optional[CityResponse] = None
    owner: Optional[UserResponse] = None
    model_config = ConfigDict(from_attributes=True)

class ReservationStatus(str, Enum):
    ACTIVE = "active"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TAKEN = "taken"

class ReservationBase(BaseModel):
    item_id: int

class ReservationCreate(ReservationBase):
    pass

class ReservationResponse(ReservationBase):
    id: int
    user_id: int
    reserved_at: datetime
    expires_at: datetime
    status: ReservationStatus
    created_at: datetime
    updated_at: datetime
    item: Optional[ItemResponse] = None
    user: Optional[UserResponse] = None
    model_config = ConfigDict(from_attributes=True)

class ItemSearchFilters(BaseModel):
    category_ids: Optional[List[int]] = None
    city_id: Optional[int] = None
    voivodeship_id: Optional[int] = None
    status: Optional[str] = "active"
    min_rating: Optional[Decimal] = None
    query: Optional[str] = None
    skip: int = 0
    limit: int = 20
