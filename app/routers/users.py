from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from app import schemas, queries, dependencies

router = APIRouter(prefix="/users", tags=["users"])
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

@router.post("/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate):
    existing = await queries.get_user_by_email(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    existing = await queries.get_user_by_username(user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed = pwd_context.hash(user.password)
    new_user = await queries.create_user(
        username=user.username,
        display_name=user.display_name,
        email=user.email,
        hashed_password=hashed,
        phone=user.phone,
        city=user.city,
        avatar_url=user.avatar_url,
        bio=user.bio
    )
    return new_user

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await queries.get_user_by_username(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = dependencies.create_access_token(data={"sub": str(user["id"])})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user = Depends(dependencies.get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int):
    user = await queries.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
