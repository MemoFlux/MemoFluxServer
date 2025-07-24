import hashlib
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.models.user import User
from src.auth.token_manager import generate_token, store_token


def hash_password(password: str) -> str:
    """对密码进行哈希处理"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(db: Session, username: str, password: str) -> User:
    """创建用户"""
    password_hash = hash_password(password)
    db_user = User(username=username, password_hash=password_hash)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ValueError("Username already exists")


def get_user(db: Session, username: str) -> Optional[User]:
    """获取用户"""
    return db.query(User).filter(User.username == username).first()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return hash_password(plain_password) == hashed_password


def create_access_token(username: str) -> str:
    """创建访问令牌"""
    token = generate_token()
    store_token(token, username)
    return token
