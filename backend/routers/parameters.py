from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import ProcessRecord, ProcessParameterValue, Machine, Product, Template, TemplateParameter
from schemas import ParameterSaveRequest, ProcessRecordCreate
from plc_client import PLCClient
from dependencies import verify_token
from utils.logger import log_parameter_save, log_record_write_to_plc

router = APIRouter(prefix="/api")

@router.get("/process-parameters")
def get_process_parameters(
    machine_id: Optional[int] = None,
    product_id: Optional[int] = None,
    db: Session = Depends(get_db),
    request: Request = None
):
    verify_token(request)
    
    if machine_id:
        machine = db.query(Machine).filter(Machine.id == machine_id).first()
        if machine and machine.template_id:
            params = db.query(TemplateParameter).filter(
                TemplateParameter.template_id == machine.template_id
            ).all()
            return [
                {
                    "id": p.id,
                    "machine_id": machine_id,
                    "product_id": product_id,
                    "parameter_name": p.parameter_name,
                    "parameter_address": p.parameter_address,
                    "parameter_value": p.parameter_value,
                    "parameter_unit": p.parameter_unit,
                    "parameter_type": p.parameter_type,
                    "is_active": True,
                    "is_readonly": p.is_readonly,
                    "slot": p.slot,
                    "machine_name": machine.machine_name,
                    "product_name": None
                }
                for p in params
            ]
    
    return []

@router.post("/process-parameters")
def save_process_parameters(request: ParameterSaveRequest, db: Session = Depends(get_db), req: Request = None):
    verify_token(req)
    token_payload = verify_token(req)
    user_id = token_payload.get("user_id")
    
    last_record = db.query(ProcessRecord).filter(
        ProcessRecord.machine_id == request.machine_id,
        ProcessRecord.product_id == request.product_id
    ).order_by(ProcessRecord.version.desc()).first()
    
    version = 1
    if last_record:
        version = last_record.version + 1
    
    record = ProcessRecord(
        machine_id=request.machine_id,
        product_id=request.product_id,
        operator_id=user_id,
        notes=request.notes,
        version=version
    )
    db.add(record)
    db.flush()
    
    template_params = {}
    machine = db.query(Machine).filter(Machine.id == request.machine_id).first()
    if machine and machine.template_id:
        template_parameters = db.query(TemplateParameter).filter(TemplateParameter.template_id == machine.template_id).all()
        for tp in template_parameters:
            template_params[tp.parameter_name] = tp.slot if tp.slot is not None else 1
    
    for param in request.parameters:
        is_readonly_val = param.is_readonly
        if isinstance(is_readonly_val, str):
            is_readonly_val = is_readonly_val.lower() == "true"
        
        param_value = ProcessParameterValue(
            process_record_id=record.id,
            parameter_name=param.parameter_name,
            parameter_address=param.parameter_address,
            parameter_value=str(param.parameter_value),
            parameter_unit=param.parameter_unit,
            parameter_type=param.parameter_type,
            is_readonly=is_readonly_val,
            slot=template_params.get(param.parameter_name, 1)
        )
        db.add(param_value)
    
    db.commit()
    
    log_parameter_save(db, user_id, request.machine_id, request.product_id)
    return {"message": "工艺参数保存成功"}

@router.get("/process-records")
def get_process_records(
    machine_id: Optional[int] = None,
    product_id: Optional[int] = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    request: Request = None
):
    verify_token(request)
    query = db.query(ProcessRecord)
    
    if machine_id:
        query = query.filter(ProcessRecord.machine_id == machine_id)
    if product_id:
        query = query.filter(ProcessRecord.product_id == product_id)
    
    total = query.count()
    offset = (page - 1) * limit
    records = query.order_by(ProcessRecord.record_time.desc()).offset(offset).limit(limit).all()
    record_list = [
        {
            "id": r.id,
            "machine_id": r.machine_id,
            "product_id": r.product_id,
            "operator_id": r.operator_id,
            "record_time": r.record_time,
            "created_at": r.record_time,
            "notes": r.notes,
            "version": r.version,
            "parameters_snapshot": {
                param.parameter_name: {
                    "address": param.parameter_address,
                    "value": param.parameter_value,
                    "unit": param.parameter_unit,
                    "type": param.parameter_type
                }
                for param in r.parameter_values
            },
            "machine_name": r.machine.machine_name if r.machine else None,
            "product_name": r.product.product_name if r.product else None,
            "operator_name": r.operator.username if r.operator else None
        }
        for r in records
    ]
    return {"items": record_list, "total": total, "page": page, "limit": limit}

@router.post("/process-records")
def create_process_record(request: ProcessRecordCreate, db: Session = Depends(get_db), req: Request = None):
    verify_token(req)
    
    last_record = db.query(ProcessRecord).filter(
        ProcessRecord.machine_id == request.machine_id,
        ProcessRecord.product_id == request.product_id
    ).order_by(ProcessRecord.version.desc()).first()
    
    version = 1
    if last_record:
        version = last_record.version + 1
    
    record = ProcessRecord(
        machine_id=request.machine_id,
        product_id=request.product_id,
        operator_id=request.operator_id,
        notes=request.notes,
        version=version
    )
    db.add(record)
    db.flush()
    
    template_params = {}
    if request.machine_id:
        machine = db.query(Machine).filter(Machine.id == request.machine_id).first()
        if machine and machine.template_id:
            template_parameters = db.query(TemplateParameter).filter(TemplateParameter.template_id == machine.template_id).all()
            for tp in template_parameters:
                template_params[tp.parameter_name] = tp.slot if tp.slot is not None else 1
    
    if request.parameters_snapshot:
        for param_name, param_info in request.parameters_snapshot.items():
            if isinstance(param_info, dict):
                param_value = ProcessParameterValue(
                    process_record_id=record.id,
                    parameter_name=param_name,
                    parameter_address=param_info.get("address", ""),
                    parameter_value=str(param_info.get("value", "")),
                    parameter_unit=param_info.get("unit", ""),
                    parameter_type=param_info.get("type", "Int"),
                    is_readonly=param_info.get("readonly", False),
                    slot=template_params.get(param_name, 1)
                )
                db.add(param_value)
    
    db.commit()
    db.refresh(record)
    return {"id": record.id, "message": "工艺记录保存成功", "version": record.version}

@router.post("/process-records/{record_id}/write-to-plc")
def write_record_to_plc(record_id: int, db: Session = Depends(get_db), request: Request = None):
    token_payload = verify_token(request)
    user_id = token_payload.get("user_id")
    
    record = db.query(ProcessRecord).filter(ProcessRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    machine = db.query(Machine).filter(Machine.id == record.machine_id).first()
    if not machine or not machine.ip_address:
        raise HTTPException(status_code=400, detail="机台未配置IP地址")
    
    if not record.parameter_values:
        raise HTTPException(status_code=400, detail="无工艺参数")
    
    plc = PLCClient(machine.ip_address, machine.rack, machine.slot)
    if not plc.connect():
        raise HTTPException(status_code=500, detail="PLC连接失败")
    
    results = {}
    for param in record.parameter_values:
        if param.is_readonly:
            results[param.parameter_name] = "只读参数，跳过写入"
            continue
            
        try:
            value = param.parameter_value
            if param.parameter_type == "Real":
                value = float(value)
            elif param.parameter_type == "Int":
                value = int(value)
            elif param.parameter_type == "Bool":
                value = value.lower() == "true"
            
            slot = param.slot if param.slot is not None else machine.slot
            success = plc.write_parameter(param.parameter_address, value, param.parameter_type, slot)
            results[param.parameter_name] = success
        except Exception:
            results[param.parameter_name] = False
    
    plc.disconnect()
    
    response_data = {"success": True, "results": results}
    log_record_write_to_plc(db, user_id, record_id, record.machine_id, record.parameter_values, response_data)
    return response_data

@router.get("/process-parameters/template/{machine_id}")
def get_parameter_template(machine_id: int, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="机台不存在")
    
    template = []
    
    if machine.template_id:
        template_obj = db.query(Template).filter(Template.id == machine.template_id).first()
        if template_obj:
            template_parameters = db.query(TemplateParameter).filter(TemplateParameter.template_id == template_obj.id).all()
            if template_parameters:
                for param in template_parameters:
                    template.append({
                        "parameter_name": param.parameter_name,
                        "parameter_address": param.parameter_address,
                        "parameter_value": param.parameter_value,
                        "parameter_unit": param.parameter_unit,
                        "parameter_type": param.parameter_type,
                        "is_readonly": param.is_readonly,
                        "slot": param.slot if param.slot is not None else 1
                    })
                return {"template": template}
            else:
                raise HTTPException(status_code=404, detail="模板中没有工艺参数")
        else:
            raise HTTPException(status_code=404, detail="绑定的模板不存在")
    
    raise HTTPException(status_code=404, detail="机台未绑定模板，请先绑定模板")