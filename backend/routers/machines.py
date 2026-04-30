from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from database import get_db
from models import Machine, Template, TemplateParameter
from schemas import MachineCreate, MachineResponse, MachineUpdate, PLCWriteRequest
from plc_client import PLCClient
from dependencies import verify_token
from utils.logger import log_plc_read, log_plc_write, log_machine_create, log_machine_update, log_machine_delete, log_template_bind, log_template_unbind

router = APIRouter(prefix="/api")

@router.get("/machines")
def get_machines(page: int = 1, limit: int = 10, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    total = db.query(Machine).count()
    offset = (page - 1) * limit
    machines = db.query(Machine).offset(offset).limit(limit).all()
    
    for machine in machines:
        machine.status = "离线"
        if hasattr(machine, 'template') and machine.template:
            machine.template_id = machine.template.id
            machine.template_name = machine.template.name
        else:
            machine.template_id = None
            machine.template_name = None
    
    return {"items": machines, "total": total, "page": page, "limit": limit}

@router.post("/machines", response_model=MachineResponse)
def create_machine(machine: MachineCreate, db: Session = Depends(get_db), request: Request = None):
    token_payload = verify_token(request)
    user_id = token_payload.get("user_id")
    
    existing = db.query(Machine).filter(Machine.machine_code == machine.machine_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="机台编号已存在")
    
    db_machine = Machine(**machine.model_dump())
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    
    log_machine_create(db, user_id, db_machine.id, db_machine.machine_name)
    return db_machine

@router.put("/machines/{machine_id}", response_model=MachineResponse)
def update_machine(machine_id: int, machine: MachineUpdate, db: Session = Depends(get_db), request: Request = None):
    token_payload = verify_token(request)
    user_id = token_payload.get("user_id")
    
    db_machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not db_machine:
        raise HTTPException(status_code=404, detail="机台不存在")
    
    for key, value in machine.model_dump(exclude_unset=True).items():
        setattr(db_machine, key, value)
    
    db.commit()
    db.refresh(db_machine)
    
    log_machine_update(db, user_id, db_machine.id, db_machine.machine_name)
    return db_machine

@router.delete("/machines/{machine_id}")
def delete_machine(machine_id: int, db: Session = Depends(get_db), request: Request = None):
    token_payload = verify_token(request)
    user_id = token_payload.get("user_id")
    
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="机台不存在")
    
    machine_name = machine.machine_name
    db.delete(machine)
    db.commit()
    
    log_machine_delete(db, user_id, machine_id, machine_name)
    return {"message": "机台删除成功"}

@router.get("/machines/status")
def check_machines_status(db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    machines = db.query(Machine).all()
    status_list = []
    
    for machine in machines:
        status = "离线"
        if machine.ip_address:
            plc = PLCClient(machine.ip_address, machine.rack, machine.slot)
            try:
                if plc.connect():
                    status = "在线"
                else:
                    status = "离线"
            except Exception:
                status = "错误"
            finally:
                plc.disconnect()
        
        status_list.append({"id": machine.id, "status": status})
    
    return status_list

@router.get("/machines/{machine_id}/read")
def read_machine_parameters(machine_id: int, db: Session = Depends(get_db), request: Request = None):
    token_payload = verify_token(request)
    user_id = token_payload.get("user_id")
    
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="机台不存在")
    
    if not machine.ip_address:
        raise HTTPException(status_code=400, detail="机台未配置IP地址")
    
    plc = PLCClient(machine.ip_address, machine.rack, machine.slot)
    if not plc.connect():
        raise HTTPException(status_code=500, detail="PLC连接失败，请检查IP地址、Rack和Slot配置")
    
    parameters = []

    if machine.template_id:
        template = db.query(Template).filter(Template.id == machine.template_id).first()
        if template:
            template_parameters = db.query(TemplateParameter).filter(TemplateParameter.template_id == template.id).all()
            if template_parameters:
                for param in template_parameters:
                    temp_param = type('TempParam', (), {
                        'machine_id': machine_id,
                        'product_id': None,
                        'parameter_name': param.parameter_name,
                        'parameter_address': param.parameter_address,
                        'parameter_value': param.parameter_value,
                        'parameter_unit': param.parameter_unit,
                        'parameter_type': param.parameter_type,
                        'is_active': True,
                        'is_readonly': param.is_readonly,
                        'slot': param.slot if param.slot is not None else 1
                    })()
                    parameters.append(temp_param)
            else:
                plc.disconnect()
                raise HTTPException(status_code=404, detail="绑定的模板中没有配置工艺参数")
        else:
            plc.disconnect()
            raise HTTPException(status_code=404, detail="绑定的模板不存在")
    else:
        plc.disconnect()
        raise HTTPException(status_code=404, detail="机台未绑定模板，请先绑定模板")
    print("参数列表：")
    for param in parameters:
        print(f"参数名称: {param.parameter_name}, 地址: {param.parameter_address}, 类型: {param.parameter_type}, Slot: {param.slot}")
    
    results = {}
    success_count = 0
    error_count = 0
    
    for param in parameters:
        try:
            value = plc.read_parameter(param.parameter_address, param.parameter_type, param.slot)
            if value is not None:
                results[param.parameter_name] = {
                    "address": param.parameter_address,
                    "value": value,
                    "unit": param.parameter_unit,
                    "type": param.parameter_type,
                    "is_readonly": getattr(param, 'is_readonly', False),
                    "slot": param.slot
                }
                success_count += 1
            else:
                error_count += 1
        except Exception:
            error_count += 1
    
    plc.disconnect()
    
    if not results:
        raise HTTPException(status_code=500, detail="所有参数读取失败，请检查PLC连接和参数地址配置")
    
    response_data = {"machine": {"id": machine.id, "name": machine.machine_name}, "parameters": results}
    log_plc_read(db, user_id, machine.id, machine.machine_name, results, response_data)
    return response_data

@router.post("/machines/{machine_id}/write")
def write_machine_parameters(
    machine_id: int,
    request: PLCWriteRequest,
    db: Session = Depends(get_db),
    req: Request = None
):
    token_payload = verify_token(req)
    user_id = token_payload.get("user_id")

    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="机台不存在")

    if not machine.ip_address:
        raise HTTPException(status_code=400, detail="机台未配置IP地址")

    plc = PLCClient(machine.ip_address, machine.rack, machine.slot)
    if not plc.connect():
        raise HTTPException(status_code=500, detail="PLC连接失败")

    template_params = {}
    if machine.template_id:
        template_parameters = db.query(TemplateParameter).filter(TemplateParameter.template_id == machine.template_id).all()
        for tp in template_parameters:
            template_params[tp.parameter_name] = tp.slot if tp.slot is not None else 1

    results = {}
    for param_name, param_data in request.parameters.items():
        slot = template_params.get(param_name, machine.slot)
        success = plc.write_parameter(param_data.address, param_data.value, param_data.type, slot)
        results[param_name] = success

    plc.disconnect()

    response_data = {"success": True, "results": results}
    log_plc_write(db, user_id, machine.id, machine.machine_name, request.parameters.dict(), response_data)
    return response_data

@router.post("/machines/{machine_id}/bind-template")
def bind_template_to_machine(machine_id: int, request_data: dict, db: Session = Depends(get_db), request: Request = None):
    token_payload = verify_token(request)
    user_id = token_payload.get("user_id")
    
    template_id = request_data.get("template_id")
    if not template_id:
        raise HTTPException(status_code=400, detail="请提供template_id")
    
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="机台不存在")
    
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    machine.template_id = template_id
    db.commit()
    
    log_template_bind(db, user_id, machine_id, template_id)
    return {"message": "模板绑定成功"}

@router.post("/machines/{machine_id}/unbind-template")
def unbind_template_from_machine(machine_id: int, db: Session = Depends(get_db), request: Request = None):
    token_payload = verify_token(request)
    user_id = token_payload.get("user_id")
    
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="机台不存在")
    
    machine.template_id = None
    db.commit()
    
    log_template_unbind(db, user_id, machine_id)
    return {"message": "模板解绑成功"}