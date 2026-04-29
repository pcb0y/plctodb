from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import ProcessParameter, ProcessRecord, ProcessParameterValue, Machine, Product, Template, TemplateParameter
from schemas import ParameterSaveRequest, ParameterBindRequest, ProcessRecordCreate
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
    query = db.query(ProcessParameter)
    
    if machine_id:
        query = query.filter(ProcessParameter.machine_id == machine_id)
    if product_id:
        query = query.filter(ProcessParameter.product_id == product_id)
    
    params = query.all()
    return [
        {
            "id": p.id,
            "machine_id": p.machine_id,
            "product_id": p.product_id,
            "parameter_name": p.parameter_name,
            "parameter_address": p.parameter_address,
            "parameter_value": p.parameter_value,
            "parameter_unit": p.parameter_unit,
            "parameter_type": p.parameter_type,
            "is_active": p.is_active,
            "machine_name": p.machine.machine_name if p.machine else None,
            "product_name": p.product.product_name if p.product else None
        }
        for p in params
    ]

@router.post("/process-parameters")
def save_process_parameters(request: ParameterSaveRequest, db: Session = Depends(get_db), req: Request = None):
    verify_token(req)
    token_payload = verify_token(req)
    user_id = token_payload.get("user_id")
    
    for param in request.parameters:
        existing = db.query(ProcessParameter).filter(
            ProcessParameter.machine_id == request.machine_id,
            ProcessParameter.product_id == request.product_id,
            ProcessParameter.parameter_name == param.parameter_name
        ).first()
        
        if existing:
            existing.parameter_address = param.parameter_address
            existing.parameter_value = param.parameter_value
            existing.parameter_unit = param.parameter_unit
            existing.parameter_type = param.parameter_type
        else:
            db_param = ProcessParameter(
                machine_id=request.machine_id,
                product_id=request.product_id,
                **param.model_dump()
            )
            db.add(db_param)
    
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
    
    for param in request.parameters:
        param_value = ProcessParameterValue(
            process_record_id=record.id,
            parameter_name=param.parameter_name,
            parameter_address=param.parameter_address,
            parameter_value=str(param.parameter_value),
            parameter_unit=param.parameter_unit,
            parameter_type=param.parameter_type
        )
        db.add(param_value)
    
    db.commit()
    
    log_parameter_save(db, user_id, request.machine_id, request.product_id)
    return {"message": "工艺参数保存成功"}

@router.post("/process-parameters/bind")
def bind_product_machine(request: ParameterBindRequest, db: Session = Depends(get_db), req: Request = None):
    verify_token(req)
    
    if request.source_machine_code and request.source_product_code:
        source_machine = db.query(Machine).filter(Machine.machine_code == request.source_machine_code).first()
        source_product = db.query(Product).filter(Product.product_code == request.source_product_code).first()
        
        if not source_machine or not source_product:
            raise HTTPException(status_code=404, detail="源机台或源产品不存在")
        
        source_params = db.query(ProcessParameter).filter(
            ProcessParameter.machine_id == source_machine.id,
            ProcessParameter.product_id == source_product.id
        ).all()
        
        for sp in source_params:
            existing = db.query(ProcessParameter).filter(
                ProcessParameter.machine_id == request.machine_id,
                ProcessParameter.product_id == request.product_id,
                ProcessParameter.parameter_name == sp.parameter_name
            ).first()
            
            if existing:
                existing.parameter_value = sp.parameter_value
            else:
                db_param = ProcessParameter(
                    machine_id=request.machine_id,
                    product_id=request.product_id,
                    parameter_name=sp.parameter_name,
                    parameter_address=sp.parameter_address,
                    parameter_value=sp.parameter_value,
                    parameter_unit=sp.parameter_unit,
                    parameter_type=sp.parameter_type
                )
                db.add(db_param)
        
        db.commit()
    
    return {"message": "产品与机台绑定成功"}

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
                    is_readonly=param_info.get("readonly", False)
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
            
            success = plc.write_parameter(param.parameter_address, value, param.parameter_type)
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
                        "is_readonly": param.is_readonly
                    })
                return {"template": template}
            else:
                raise HTTPException(status_code=404, detail="模板中没有工艺参数")
        else:
            raise HTTPException(status_code=404, detail="绑定的模板不存在")
    
    raise HTTPException(status_code=404, detail="机台未绑定模板，请先绑定模板")