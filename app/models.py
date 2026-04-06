from sqlalchemy import Column, BigInteger, SmallInteger, Integer, String, Text, DECIMAL, Boolean, TIMESTAMP, ForeignKey, Index, CheckConstraint
from sqlalchemy import text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(60), nullable=False, unique=True)
    display_name = Column(String(100))
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255))
    phone = Column(String(20))
    city = Column(String(100))
    avatar_url = Column(String(500))
    bio = Column(Text)
    rating = Column(DECIMAL(3, 2), default=5.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_active_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    items = relationship("Item", back_populates="owner", foreign_keys="Item.user_id")
    taken_items = relationship("Item", back_populates="taken_by", foreign_keys="Item.taken_by_id")
    reservations = relationship("Reservation", back_populates="user")

class Voivodeship(Base):
    __tablename__ = "voivodeships"

    id = Column(SmallInteger, primary_key=True, index=True)
    name = Column(String(60), nullable=False, unique=True)

    cities = relationship("City", back_populates="voivodeship")

class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    voivodeship_id = Column(SmallInteger, ForeignKey("voivodeships.id"), nullable=False)
    name = Column(String(100), nullable=False)
    postal_code_prefix = Column(String(2))

    voivodeship = relationship("Voivodeship", back_populates="cities")
    items = relationship("Item", back_populates="city_obj")

    __table_args__ = (Index("idx_cities_voivodeship_id", "voivodeship_id"),)

class Category(Base):
    __tablename__ = "categories"

    id = Column(SmallInteger, primary_key=True, index=True)
    name = Column(String(60), nullable=False, unique=True)
    icon_name = Column(String(100))
    description = Column(Text)

    items = relationship("Item", secondary="item_categories", back_populates="categories")

class Item(Base):
    __tablename__ = "items"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    title = Column(String(120), nullable=False)
    description = Column(Text)
    condition = Column(String(30))
    quantity = Column(SmallInteger, default=1)
    city_id = Column(Integer, ForeignKey("cities.id"))
    street_hint = Column(String(120))
    status = Column(String(30), nullable=False, default="active")
    taken_at = Column(TIMESTAMP)
    taken_by_id = Column(BigInteger, ForeignKey("users.id"))
    views_count = Column(Integer, default=0)
    favorites_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    expires_at = Column(TIMESTAMP, server_default=func.now() + text("INTERVAL '30 days'"))

    owner = relationship("User", back_populates="items", foreign_keys=[user_id])
    taken_by = relationship("User", back_populates="taken_items", foreign_keys=[taken_by_id])
    city_obj = relationship("City", back_populates="items")
    photos = relationship("ItemPhoto", back_populates="item", cascade="all, delete-orphan")
    categories = relationship("Category", secondary="item_categories", back_populates="items")
    reservations = relationship("Reservation", back_populates="item")

    __table_args__ = (
        Index("idx_items_user_id", "user_id"),
        Index("idx_items_city_id", "city_id"),
        Index("idx_items_status", "status"),
        Index("idx_items_created_at", "created_at"),
    )

class ItemPhoto(Base):
    __tablename__ = "item_photos"

    id = Column(BigInteger, primary_key=True, index=True)
    item_id = Column(BigInteger, ForeignKey("items.id"), nullable=False)
    url = Column(String(500), nullable=False)
    storage_key = Column(String(200))
    is_main = Column(Boolean)
    position = Column(SmallInteger)
    width = Column(Integer)
    height = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())

    item = relationship("Item", back_populates="photos")

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(BigInteger, primary_key=True, index=True)
    item_id = Column(BigInteger, ForeignKey("items.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    reserved_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    expires_at = Column(TIMESTAMP, nullable=False)
    status = Column(String(30), nullable=False, default="active")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    item = relationship("Item", back_populates="reservations")
    user = relationship("User", back_populates="reservations")

    __table_args__ = (
        Index("idx_reservations_item_status", "item_id", "status"),
        Index("idx_reservations_user_status", "user_id", "status"),
        Index("idx_reservations_expires_at", "expires_at"),
    )

class ItemCategory(Base):
    __tablename__ = "item_categories"
    __table_args__ = {'extend_existing': True}

    item_id = Column(BigInteger, ForeignKey("items.id"), primary_key=True)
    category_id = Column(SmallInteger, ForeignKey("categories.id"), primary_key=True)
