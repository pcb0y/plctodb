from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import jwt
from passlib.context import CryptContext
import hashlib

from database import get_db
from models import User
from schemas import LoginRequest, LoginResponse, UserResponse, UserCreate
from config import settings
from dependencies import verify_token
from utils.logger import log_user_create, log_user_delete, log_password_change

router = APIRouter(prefix="/api")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        old_hash = hashlib.sha256(plain_password.encode()).hexdigest()
        return old_hash == hashed_password

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    from datetime import datetime
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@router.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    access_token = create_access_token(data={"sub": user.username, "user_id": user.id, "role": user.role})
    return LoginResponse(
        access_token=access_token,
        user=UserResponse(id=user.id, username=user.username, role=user.role, created_at=user.created_at)
    )

@router.get("/users")
def get_users(page: int = 1, limit: int = 10, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    total = db.query(User).count()
    offset = (page - 1) * limit
    users = db.query(User).offset(offset).limit(limit).all()
    return {"items": users, "total": total, "page": page, "limit": limit}

@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db), request: Request = None):
    token_payload = verify_token(request)
    user_id = token_payload.get("user_id")
    
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    log_user_create(db, user_id, db_user.id, db_user.username)
    return db_user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), request: Request = None):
    token_payload = verify_token(request)
    current_user_id = token_payload.get("user_id")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="不能删除管理员账号")
    
    username = user.username
    db.delete(user)
    db.commit()
    
    log_user_delete(db, current_user_id, user_id, username)
    return {"message": "用户删除成功"}

@router.post("/users/{user_id}/change-password")
def change_user_password(user_id: int, new_password: dict, db: Session = Depends(get_db), request: Request = None):
    token_payload = verify_token(request)
    current_user_id = token_payload.get("user_id")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if not new_password.get("new_password"):
        raise HTTPException(status_code=400, detail="新密码不能为空")
    if len(new_password.get("new_password")) < 6:
        raise HTTPException(status_code=400, detail="密码长度至少为6位")
    
    hashed_password = get_password_hash(new_password.get("new_password"))
    user.hashed_password = hashed_password
    db.commit()
    db.refresh(user)
    
    log_password_change(db, current_user_id, user_id)
    return {"message": "密码修改成功"}