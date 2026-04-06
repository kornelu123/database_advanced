from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db_pool, close_db_pool
from app.routers import items, reservations, categories, users, locations

app = FastAPI(title="Item Exchange API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router)
app.include_router(reservations.router)
app.include_router(categories.router)
app.include_router(users.router)
app.include_router(locations.router)

@app.on_event("startup")
async def startup():
    await init_db_pool()

@app.on_event("shutdown")
async def shutdown():
    await close_db_pool()

@app.get("/")
async def root():
    return {"message": "Item Exchange API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
