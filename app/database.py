import asyncpg
from asyncpg.pool import Pool
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:@localhost/postgres")
_pool: Pool = None

async def init_db_pool():
    global _pool
    _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)

async def close_db_pool():
    await _pool.close()

@asynccontextmanager
async def get_connection():
    async with _pool.acquire() as conn:
        yield conn
