from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
import json

from database import get_db
from models import OperationLog, User
from dependencies import verify_token

router = APIRouter(prefix="/api")

OPERATION_TYPE_MAP = {
    '读取PLC': ['读取PLC', 'PLC_READ'],
    '写入PLC': ['写入PLC', 'PLC_WRITE'],
    '创建': ['创建', 'CREATE'],
    '更新': ['更新', 'UPDATE'],
    '删除': ['删除', 'DELETE'],
    '保存': ['保存', 'SAVE'],
    '绑定': ['绑定', 'BIND'],
    '解绑': ['解绑', 'UNBIND']
}

TARGET_TYPE_MAP = {
    '机台': ['机台', 'MACHINE'],
    '产品': ['产品', 'PRODUCT'],
    '模板': ['模板', 'TEMPLATE'],
    '用户': ['用户', 'USER'],
    '参数': ['参数', 'PARAMETER'],
    '记录': ['记录', 'RECORD'],
    '密码': ['密码', 'USER_PASSWORD']
}

@router.get("/operation-logs")
def get_operation_logs(
    page: int = 1,
    limit: int = 10,
    operation_type: str = None,
    target_type: str = None,
    user_id: int = None,
    username: str = None,
    start_time: str = None,
    end_time: str = None,
    db: Session = Depends(get_db),
    request: Request = None
):
    verify_token(request)
    
    query = db.query(OperationLog).order_by(OperationLog.created_at.desc())
    
    if operation_type:
        types_to_match = OPERATION_TYPE_MAP.get(operation_type, [operation_type])
        query = query.filter(or_(*[OperationLog.operation_type == t for t in types_to_match]))
    if target_type:
        types_to_match = TARGET_TYPE_MAP.get(target_type, [target_type])
        query = query.filter(or_(*[OperationLog.target_type == t for t in types_to_match]))
    if user_id:
        query = query.filter(OperationLog.user_id == user_id)
    if username:
        user = db.query(User).filter(User.username == username).first()
        if user:
            query = query.filter(OperationLog.user_id == user.id)
    if start_time:
        try:
            start_datetime = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            query = query.filter(OperationLog.created_at >= start_datetime)
        except:
            pass
    if end_time:
        try:
            end_datetime = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            query = query.filter(OperationLog.created_at <= end_datetime)
        except:
            pass
    
    total = query.count()
    offset = (page - 1) * limit
    logs = query.offset(offset).limit(limit).all()
    
    log_list = []
    for log in logs:
        user = db.query(User).filter(User.id == log.user_id).first()
        request_params = json.loads(log.request_params) if log.request_params else None
        response_data = json.loads(log.response_data) if log.response_data else None
        log_list.append({
            "id": log.id,
            "user_id": log.user_id,
            "username": user.username if user else None,
            "operation_type": log.operation_type,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "details": log.details,
            "request_params": request_params,
            "response_data": response_data,
            "created_at": log.created_at
        })
    
    return {"items": log_list, "total": total, "page": page, "limit": limit}

@router.get("/operation-logs/{log_id}")
def get_operation_log(log_id: int, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    
    log = db.query(OperationLog).filter(OperationLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    
    user = db.query(User).filter(User.id == log.user_id).first()
    request_params = json.loads(log.request_params) if log.request_params else None
    response_data = json.loads(log.response_data) if log.response_data else None
    
    return {
        "id": log.id,
        "user_id": log.user_id,
        "username": user.username if user else None,
        "operation_type": log.operation_type,
        "target_type": log.target_type,
        "target_id": log.target_id,
        "details": log.details,
        "request_params": request_params,
        "response_data": response_data,
        "created_at": log.created_at
    }

@router.get("/operation-log-types")
def get_operation_types(db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    
    types = db.query(OperationLog.operation_type).distinct().all()
    return {"types": [t[0] for t in types]}

@router.get("/operation-target-types")
def get_target_types(db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    
    types = db.query(OperationLog.target_type).distinct().all()
    return {"target_types": [t[0] for t in types]}