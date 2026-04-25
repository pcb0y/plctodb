from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserBase(BaseModel):
    username: str
    role: str = "operator"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class MachineBase(BaseModel):
    machine_code: str
    machine_name: str
    machine_type: Optional[str] = None
    ip_address: Optional[str] = None
    rack: int = 0
    slot: int = 1

class MachineCreate(MachineBase):
    pass

class MachineUpdate(BaseModel):
    machine_code: Optional[str] = None
    machine_name: Optional[str] = None
    machine_type: Optional[str] = None
    ip_address: Optional[str] = None
    rack: Optional[int] = None
    slot: Optional[int] = None
    status: Optional[str] = None

class MachineResponse(MachineBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    product_code: str
    product_name: str
    product_spec: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    product_spec: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ParameterBase(BaseModel):
    parameter_name: str
    parameter_address: str
    parameter_value: Optional[str] = None
    parameter_unit: Optional[str] = ""
    parameter_type: str = "Int"

class ParameterCreate(ParameterBase):
    machine_id: int
    product_id: int

class ParameterUpdate(BaseModel):
    parameter_name: Optional[str] = None
    parameter_address: Optional[str] = None
    parameter_value: Optional[str] = None
    parameter_unit: Optional[str] = None
    parameter_type: Optional[str] = None
    is_active: Optional[bool] = None

class ParameterResponse(ParameterBase):
    id: int
    machine_id: int
    product_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ParameterSaveRequest(BaseModel):
    machine_id: int
    product_id: int
    parameters: List[ParameterBase]
    notes: Optional[str] = ""

class ParameterBindRequest(BaseModel):
    machine_id: int
    product_id: int
    source_machine_code: Optional[str] = None
    source_product_code: Optional[str] = None

class ProcessRecordBase(BaseModel):
    machine_id: int
    product_id: int
    notes: Optional[str] = ""

class ProcessRecordCreate(ProcessRecordBase):
    operator_id: Optional[int] = None
    parameters_snapshot: Dict[str, Any]

class ProcessRecordResponse(ProcessRecordBase):
    id: int
    operator_id: Optional[int]
    record_time: datetime
    parameters_snapshot: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class PLCParameterWrite(BaseModel):
    address: str
    value: Any
    type: str = "Int"

class PLCWriteRequest(BaseModel):
    parameters: Dict[str, PLCParameterWrite]
    operator_id: Optional[int] = None
