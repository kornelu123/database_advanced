import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from app.database import get_connection

async def create_user(username: str, display_name: Optional[str], email: str, hashed_password: str,
                      phone: Optional[str], city: Optional[str], avatar_url: Optional[str], bio: Optional[str]) -> Dict:
    async with get_connection() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO users (username, display_name, email, password_hash, phone, city, avatar_url, bio)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id, username, display_name, email, phone, city, avatar_url, bio, rating, is_active, created_at, last_active_at
            """,
            username, display_name, email, hashed_password, phone, city, avatar_url, bio
        )
        return dict(row)

async def get_user_by_email(email: str) -> Optional[Dict]:
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
        return dict(row) if row else None

async def get_user_by_username(username: str) -> Optional[Dict]:
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE username = $1", username)
        return dict(row) if row else None

async def get_user_by_id(user_id: int) -> Optional[Dict]:
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        return dict(row) if row else None

async def create_item(user_id: int, title: str, description: Optional[str], condition: Optional[str],
                      quantity: int, city_id: Optional[int], street_hint: Optional[str], category_ids: List[int]) -> Dict:
    async with get_connection() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                """
                INSERT INTO items (user_id, title, description, condition, quantity, city_id, street_hint)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING *
                """,
                user_id, title, description, condition, quantity, city_id, street_hint
            )
            item = dict(row)
            if category_ids:
                await conn.executemany(
                    "INSERT INTO item_categories (item_id, category_id) VALUES ($1, $2)",
                    [(item["id"], cat_id) for cat_id in category_ids]
                )
            return item

async def get_item(item_id: int) -> Optional[Dict]:
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT * FROM items WHERE id = $1", item_id)
        if not row:
            return None
        item = dict(row)
        categories = await conn.fetch(
            """
            SELECT c.* FROM categories c
            JOIN item_categories ic ON c.id = ic.category_id
            WHERE ic.item_id = $1
            """, item_id
        )
        item["categories"] = [dict(cat) for cat in categories]
        photos = await conn.fetch("SELECT * FROM item_photos WHERE item_id = $1 ORDER BY position", item_id)
        item["photos"] = [dict(p) for p in photos]
        if item.get("city_id"):
            city_row = await conn.fetchrow("SELECT * FROM cities WHERE id = $1", item["city_id"])
            item["city_obj"] = dict(city_row) if city_row else None
        return item
async def increment_item_views(item_id: int) -> None:
    async with get_connection() as conn:
        await conn.execute(
            "UPDATE items SET views_count = views_count + 1 WHERE id = $1",
            item_id
        )
async def search_items(filters: Dict) -> List[Dict]:
    async with get_connection() as conn:
        conditions = []
        params = []
        i = 1
        if filters.get("status"):
            conditions.append(f"i.status = ${i}")
            params.append(filters["status"])
            i += 1
        if filters.get("city_id"):
            conditions.append(f"i.city_id = ${i}")
            params.append(filters["city_id"])
            i += 1
        if filters.get("voivodeship_id"):
            conditions.append(f"c.voivodeship_id = ${i}")
            params.append(filters["voivodeship_id"])
            i += 1
        if filters.get("category_ids"):
            conditions.append(f"i.id IN (SELECT item_id FROM item_categories WHERE category_id = ANY(${i}::smallint[]))")
            params.append(filters["category_ids"])
            i += 1
        if filters.get("min_rating"):
            conditions.append(f"u.rating >= ${i}")
            params.append(filters["min_rating"])
            i += 1
        if filters.get("query"):
            conditions.append(f"(i.title ILIKE ${i} OR i.description ILIKE ${i})")
            params.append(f"%{filters['query']}%")
            i += 1

        where_clause = " AND ".join(conditions) if conditions else "TRUE"
        query = f"""
            SELECT i.*,
                   json_agg(DISTINCT jsonb_build_object('id', c.id, 'name', c.name, 'icon_name', c.icon_name, 'description', c.description)) as categories,
                   row_to_json(u) as owner,
                   row_to_json(ct) as city_obj
            FROM items i
            LEFT JOIN item_categories ic ON i.id = ic.item_id
            LEFT JOIN categories c ON ic.category_id = c.id
            LEFT JOIN users u ON i.user_id = u.id
            LEFT JOIN cities ct ON i.city_id = ct.id
            WHERE {where_clause}
            GROUP BY i.id, u.id, ct.id
            ORDER BY i.created_at DESC
            LIMIT ${i} OFFSET ${i+1}
        """
        params.extend([filters.get("limit", 20), filters.get("skip", 0)])
        rows = await conn.fetch(query, *params)
        items = []
        for row in rows:
            item = dict(row)
            # Parsuj JSON dla kategorii
            if item.get("categories"):
                try:
                    cat_list = json.loads(item["categories"])
                    if cat_list and cat_list[0].get("id") is None:
                        item["categories"] = []
                    else:
                        item["categories"] = cat_list
                except:
                    item["categories"] = []
            else:
                item["categories"] = []
            # Parsuj JSON dla owner
            if item.get("owner"):
                try:
                    item["owner"] = json.loads(item["owner"])
                except:
                    item["owner"] = None
            else:
                item["owner"] = None
            # Parsuj JSON dla city_obj
            if item.get("city_obj"):
                try:
                    item["city_obj"] = json.loads(item["city_obj"])
                except:
                    item["city_obj"] = None
            else:
                item["city_obj"] = None
            items.append(item)
        return items

async def add_photo(item_id: int, url: str, storage_key: Optional[str], is_main: bool, position: int,
                    width: Optional[int], height: Optional[int]) -> Dict:
    async with get_connection() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO item_photos (item_id, url, storage_key, is_main, position, width, height)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
            """,
            item_id, url, storage_key, is_main, position, width, height
        )
        return dict(row)

async def create_reservation(item_id: int, user_id: int) -> Optional[Dict]:
    async with get_connection() as conn:
        async with conn.transaction():
            item = await conn.fetchrow("SELECT id, status FROM items WHERE id = $1 FOR UPDATE", item_id)
            if not item or item["status"] != "active":
                return None
            existing = await conn.fetchrow(
                "SELECT id FROM reservations WHERE item_id = $1 AND status IN ('active', 'confirmed')",
                item_id
            )
            if existing:
                return None
            expires_at = datetime.utcnow() + timedelta(hours=24)
            row = await conn.fetchrow(
                """
                INSERT INTO reservations (item_id, user_id, expires_at, status)
                VALUES ($1, $2, $3, 'active')
                RETURNING *
                """,
                item_id, user_id, expires_at
            )
            return dict(row)

async def get_reservation(reservation_id: int) -> Optional[Dict]:
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT * FROM reservations WHERE id = $1", reservation_id)
        return dict(row) if row else None

async def get_user_reservations(user_id: int, skip: int, limit: int) -> List[Dict]:
    async with get_connection() as conn:
        rows = await conn.fetch(
            """
            SELECT r.*, row_to_json(i) as item
            FROM reservations r
            JOIN items i ON r.item_id = i.id
            WHERE r.user_id = $1
            ORDER BY r.reserved_at DESC
            LIMIT $2 OFFSET $3
            """,
            user_id, limit, skip
        )
        return [dict(r) for r in rows]

async def get_categories() -> List[Dict]:
    async with get_connection() as conn:
        rows = await conn.fetch("SELECT * FROM categories ORDER BY id")
        return [dict(r) for r in rows]

async def get_category(category_id: int) -> Optional[Dict]:
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT * FROM categories WHERE id = $1", category_id)
        return dict(row) if row else None

async def create_category(name: str, icon_name: Optional[str], description: Optional[str]) -> Dict:
    async with get_connection() as conn:
        row = await conn.fetchrow(
            "INSERT INTO categories (name, icon_name, description) VALUES ($1, $2, $3) RETURNING *",
            name, icon_name, description
        )
        return dict(row)

async def get_voivodeships() -> List[Dict]:
    async with get_connection() as conn:
        rows = await conn.fetch("SELECT * FROM voivodeships ORDER BY id")
        return [dict(r) for r in rows]

async def get_cities_by_voivodeship(voivodeship_id: int) -> List[Dict]:
    async with get_connection() as conn:
        rows = await conn.fetch("SELECT * FROM cities WHERE voivodeship_id = $1 ORDER BY name", voivodeship_id)
        return [dict(r) for r in rows]

async def get_city(city_id: int) -> Optional[Dict]:
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT * FROM cities WHERE id = $1", city_id)
        return dict(row) if row else None

async def get_photo(photo_id: int) -> Optional[Dict]:
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT * FROM item_photos WHERE id = $1", photo_id)
        return dict(row) if row else None


