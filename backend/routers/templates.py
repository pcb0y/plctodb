from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Template, TemplateParameter
from backend.schemas import TemplateCreate, TemplateResponse, TemplateUpdate, TemplateParameterBase
from backend.dependencies import verify_token

router = APIRouter(prefix="/api")

@router.get("/templates")
def get_templates(page: int = 1, limit: int = 10, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    total = db.query(Template).count()
    offset = (page - 1) * limit
    templates = db.query(Template).offset(offset).limit(limit).all()
    
    template_responses = []
    for template in templates:
        template_response = TemplateResponse(
            id=template.id,
            name=template.name,
            param_count=len(template.template_parameters),
            machine_count=len(template.machines) if hasattr(template, 'machines') else 0,
            created_at=template.created_at,
            updated_at=template.updated_at,
            parameters=template.template_parameters
        )
        template_responses.append(template_response)
    
    return {"items": template_responses, "total": total, "page": page, "limit": limit}

@router.post("/templates", response_model=TemplateResponse)
def create_template(template: TemplateCreate, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    
    db_template = Template(name=template.name)
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    for param in template.parameters:
        db_param = TemplateParameter(
            template_id=db_template.id,
            parameter_name=param.parameter_name,
            parameter_address=param.parameter_address,
            parameter_value=param.parameter_value,
            parameter_unit=param.parameter_unit,
            parameter_type=param.parameter_type
        )
        db.add(db_param)
    
    db.commit()
    db.refresh(db_template)
    
    response = TemplateResponse(
        id=db_template.id,
        name=db_template.name,
        param_count=len(db_template.template_parameters),
        machine_count=len(db_template.machines) if hasattr(db_template, 'machines') else 0,
        created_at=db_template.created_at,
        updated_at=db_template.updated_at,
        parameters=db_template.template_parameters
    )
    
    return response

@router.get("/templates/{template_id}", response_model=TemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    response = TemplateResponse(
        id=template.id,
        name=template.name,
        param_count=len(template.template_parameters),
        machine_count=len(template.machines) if hasattr(template, 'machines') else 0,
        created_at=template.created_at,
        updated_at=template.updated_at,
        parameters=template.template_parameters
    )
    
    return response

@router.put("/templates/{template_id}", response_model=TemplateResponse)
def update_template(template_id: int, template: TemplateUpdate, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    db_template = db.query(Template).filter(Template.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    if template.name is not None:
        db_template.name = template.name
    
    if template.parameters is not None:
        db.query(TemplateParameter).filter(TemplateParameter.template_id == template_id).delete()
        for param in template.parameters:
            db_param = TemplateParameter(
                template_id=template_id,
                parameter_name=param.parameter_name,
                parameter_address=param.parameter_address,
                parameter_value=param.parameter_value,
                parameter_unit=param.parameter_unit,
                parameter_type=param.parameter_type
            )
            db.add(db_param)
    
    db.commit()
    db.refresh(db_template)
    
    response = TemplateResponse(
        id=db_template.id,
        name=db_template.name,
        param_count=len(db_template.template_parameters),
        machine_count=len(db_template.machines) if hasattr(db_template, 'machines') else 0,
        created_at=db_template.created_at,
        updated_at=db_template.updated_at,
        parameters=db_template.template_parameters
    )
    
    return response

@router.delete("/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    db.delete(template)
    db.commit()
    
    return {"message": "模板删除成功"}

@router.post("/templates/{template_id}/parameters")
def add_template_parameter(template_id: int, parameter: TemplateParameterBase, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    db_param = TemplateParameter(
        template_id=template_id,
        parameter_name=parameter.parameter_name,
        parameter_address=parameter.parameter_address,
        parameter_value=parameter.parameter_value,
        parameter_unit=parameter.parameter_unit,
        parameter_type=parameter.parameter_type,
        is_readonly=getattr(parameter, 'is_readonly', False)
    )
    db.add(db_param)
    db.commit()
    db.refresh(db_param)
    
    response = {
        "id": db_param.id,
        "template_id": db_param.template_id,
        "parameter_name": db_param.parameter_name,
        "parameter_address": db_param.parameter_address,
        "parameter_value": db_param.parameter_value,
        "parameter_unit": db_param.parameter_unit,
        "parameter_type": db_param.parameter_type,
        "is_readonly": db_param.is_readonly
    }
    
    return response

@router.put("/templates/{template_id}/parameters/{parameter_id}")
def update_template_parameter(template_id: int, parameter_id: int, parameter: TemplateParameterBase, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    db_param = db.query(TemplateParameter).filter(
        TemplateParameter.id == parameter_id,
        TemplateParameter.template_id == template_id
    ).first()
    if not db_param:
        raise HTTPException(status_code=404, detail="模板参数不存在")
    
    db_param.parameter_name = parameter.parameter_name
    db_param.parameter_address = parameter.parameter_address
    db_param.parameter_value = parameter.parameter_value
    db_param.parameter_unit = parameter.parameter_unit
    db_param.parameter_type = parameter.parameter_type
    db_param.is_readonly = getattr(parameter, 'is_readonly', False)
    
    db.commit()
    db.refresh(db_param)
    
    response = {
        "id": db_param.id,
        "template_id": db_param.template_id,
        "parameter_name": db_param.parameter_name,
        "parameter_address": db_param.parameter_address,
        "parameter_value": db_param.parameter_value,
        "parameter_unit": db_param.parameter_unit,
        "parameter_type": db_param.parameter_type,
        "is_readonly": db_param.is_readonly
    }
    
    return response

@router.delete("/templates/{template_id}/parameters/{parameter_id}")
def delete_template_parameter(template_id: int, parameter_id: int, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    db_param = db.query(TemplateParameter).filter(
        TemplateParameter.id == parameter_id,
        TemplateParameter.template_id == template_id
    ).first()
    if not db_param:
        raise HTTPException(status_code=404, detail="模板参数不存在")
    
    db.delete(db_param)
    db.commit()
    
    return {"message": "模板参数删除成功"}

@router.get("/templates/{template_id}/parameters")
def get_template_parameters(template_id: int, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    parameters = db.query(TemplateParameter).filter(TemplateParameter.template_id == template_id).all()
    
    response = []
    for param in parameters:
        response.append({
            "id": param.id,
            "template_id": param.template_id,
            "parameter_name": param.parameter_name,
            "parameter_address": param.parameter_address,
            "parameter_value": param.parameter_value,
            "parameter_unit": param.parameter_unit,
            "parameter_type": param.parameter_type,
            "is_readonly": param.is_readonly
        })
    
    return response

@router.get("/templates/{template_id}/parameters/{parameter_id}")
def get_template_parameter(template_id: int, parameter_id: int, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    db_param = db.query(TemplateParameter).filter(
        TemplateParameter.id == parameter_id,
        TemplateParameter.template_id == template_id
    ).first()
    if not db_param:
        raise HTTPException(status_code=404, detail="模板参数不存在")
    
    response = {
        "id": db_param.id,
        "template_id": db_param.template_id,
        "parameter_name": db_param.parameter_name,
        "parameter_address": db_param.parameter_address,
        "parameter_value": db_param.parameter_value,
        "parameter_unit": db_param.parameter_unit,
        "parameter_type": db_param.parameter_type,
        "is_readonly": db_param.is_readonly
    }
    
    return response