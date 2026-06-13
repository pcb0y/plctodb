"""
参数历史数据查询API
提供按机台、时间范围、参数名查询历史采集数据，用于前端折线图展示
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel

from database import get_db
from models import ParameterCollection, Machine
from dependencies import verify_token

router = APIRouter(prefix="/api")


class HistoryQueryParams(BaseModel):
    machine_id: int
    parameter_names: Optional[List[str]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = 1000


@router.get("/parameter-history")
def get_parameter_history(
    machine_id: int = Query(..., description="机台ID"),
    parameter_name: Optional[str] = Query(None, description="参数名（逗号分隔多个）"),
    start_time: Optional[str] = Query(None, description="开始时间 ISO格式"),
    end_time: Optional[str] = Query(None, description="结束时间 ISO格式"),
    hours: Optional[float] = Query(None, description="最近N小时（与start_time/end_time互斥，支持小数如0.083=5分钟）"),
    limit: int = Query(1000, ge=1, le=10000, description="最大返回条数"),
    db: Session = Depends(get_db),
    request: Request = None
):
    """查询参数历史数据，返回适合折线图的结构"""
    verify_token(request)

    # 验证机台存在
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="机台不存在")

    # 构建查询
    query = db.query(ParameterCollection).filter(ParameterCollection.machine_id == machine_id)

    # 时间范围过滤
    if hours:
        start_dt = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(ParameterCollection.collected_at >= start_dt)
    else:
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                query = query.filter(ParameterCollection.collected_at >= start_dt)
            except ValueError:
                pass
        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                query = query.filter(ParameterCollection.collected_at <= end_dt)
            except ValueError:
                pass

    # 参数名过滤
    if parameter_name:
        names = [n.strip() for n in parameter_name.split(",") if n.strip()]
        if names:
            query = query.filter(ParameterCollection.parameter_name.in_(names))

    # 按时间排序
    query = query.order_by(ParameterCollection.collected_at.asc())

    # 限制条数
    records = query.limit(limit).all()

    if not records:
        return {"machine_name": machine.machine_name, "machine_id": machine_id, "series": []}

    # 按参数名分组，构建折线图series数据
    series_map = {}
    for r in records:
        name = r.parameter_name
        if name not in series_map:
            series_map[name] = {
                "parameter_name": name,
                "parameter_unit": r.parameter_unit,
                "parameter_type": r.parameter_type,
                "data": []
            }
        series_map[name]["data"].append({
            "time": r.collected_at.isoformat() if r.collected_at else None,
            "value": r.parameter_value
        })

    return {
        "machine_name": machine.machine_name,
        "machine_id": machine_id,
        "total": len(records),
        "series": list(series_map.values())
    }


@router.get("/parameter-history/machines")
def get_history_machines(db: Session = Depends(get_db), request: Request = None):
    """获取有历史数据的机台列表"""
    verify_token(request)
    
    # 查询有历史记录的machine_id
    machine_ids = db.query(ParameterCollection.machine_id).distinct().all()
    machine_ids = [m[0] for m in machine_ids]
    
    if not machine_ids:
        return []
    
    machines = db.query(Machine).filter(Machine.id.in_(machine_ids)).all()
    return [
        {
            "id": m.id,
            "machine_code": m.machine_code,
            "machine_name": m.machine_name,
            "ip_address": m.ip_address
        }
        for m in machines
    ]


@router.get("/parameter-history/parameters")
def get_history_parameters(
    machine_id: int = Query(..., description="机台ID"),
    db: Session = Depends(get_db),
    request: Request = None
):
    """获取指定机台有历史记录的参数名列表"""
    verify_token(request)
    
    params = db.query(
        ParameterCollection.parameter_name,
        ParameterCollection.parameter_unit,
        ParameterCollection.parameter_type
    ).filter(
        ParameterCollection.machine_id == machine_id
    ).group_by(
        ParameterCollection.parameter_name,
        ParameterCollection.parameter_unit,
        ParameterCollection.parameter_type
    ).all()
    
    return [
        {
            "parameter_name": p[0],
            "parameter_unit": p[1],
            "parameter_type": p[2]
        }
        for p in params
    ]


@router.delete("/parameter-history/cleanup")
def cleanup_history(
    days: int = Query(30, ge=1, description="保留最近N天的数据"),
    db: Session = Depends(get_db),
    request: Request = None
):
    """清理历史数据，只保留最近N天"""
    token_payload = verify_token(request)
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    deleted = db.query(ParameterCollection).filter(
        ParameterCollection.collected_at < cutoff
    ).delete()
    db.commit()
    
    return {"message": f"已清理 {deleted} 条历史数据，保留最近 {days} 天"}
