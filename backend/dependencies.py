from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.config import settings
from backend.database import get_db
from backend.models import User
from typing import Optional

def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.headers.get('Authorization')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未授权")
    
    if token.startswith('Bearer '):
        token = token[7:]
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效")
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
        
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效")

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无管理员权限")
    return current_user

def verify_token(request: Request):
    token = request.headers.get('Authorization')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未授权")
    
    if token.startswith('Bearer '):
        token = token[7:]
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效")