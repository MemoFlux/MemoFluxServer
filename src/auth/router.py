from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.db import get_db
from src.auth.service import (
    create_user,
    get_user,
    verify_password,
    create_access_token,
)

from src.auth.token_manager import verify_token

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        create_user(db, user.username, user.password)
        return {"message": "User created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    db_user = get_user(db, user.username)
    if not db_user or not verify_password(user.password, db_user.password_hash):  # type: ignore
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(user.username)
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(authorization: str = Header(None)):
    """获取当前用户"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return username


@router.get("/me")
def read_users_me(current_user: str = Depends(get_current_user)):
    """获取当前用户信息"""
    return {"username": current_user}
