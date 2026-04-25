from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from backend.database import engine, get_db, Base
from backend.models import User, Machine, Product, ProcessParameter, ProcessRecord, ProcessParameterValue, OperationLog
from backend.schemas import *
from backend.plc_client import PLCClient
from backend.config import settings
import json

app = FastAPI(title="挤出机工艺参数管理系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/frontend", StaticFiles(directory=str(frontend_path)), name="frontend")

@app.get("/")
async def root():
    return RedirectResponse(url="/frontend/index.html")

# 使用安全的密码哈希（使用hashlib）
import hashlib

def verify_password(plain_password, hashed_password):
    # 验证密码
    hashed_input = hashlib.sha256(plain_password.encode()).hexdigest()
    return hashed_input == hashed_password

def get_password_hash(password):
    # 生成密码哈希
    return hashlib.sha256(password.encode()).hexdigest()

# 临时使用简单的密码验证（避免bcrypt问题）
# def verify_password(plain_password, hashed_password):
#     return plain_password == hashed_password
# 
# def get_password_hash(password):
#     return password

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(request: Request):
    import time
    start_time = time.time()
    token = request.headers.get('Authorization')
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    # 提取Bearer token
    if token.startswith('Bearer '):
        token = token[7:]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        end_time = time.time()
        print(f"verify_token 处理时间: {end_time - start_time:.4f} 秒")
        return payload
    except JWTError:
        end_time = time.time()
        print(f"verify_token 处理时间: {end_time - start_time:.4f} 秒")
        raise HTTPException(status_code=401, detail="令牌无效")

@app.on_event("startup")
async def startup():
    # 先尝试创建数据库（如果不存在）
    try:
        # 连接到MySQL服务器
        import pymysql
        conn = pymysql.connect(
            host=settings.DB_HOST,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            port=settings.DB_PORT
        )
        cursor = conn.cursor()
        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.close()
        conn.close()
        print(f"✅ 数据库 {settings.DB_NAME} 创建成功")
    except Exception as e:
        print(f"⚠️  数据库创建失败: {e}")
    
    # 创建表结构
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表结构创建成功")
    
    # 创建默认管理员用户
    db = Session(bind=engine)
    if not db.query(User).first():
        try:
            # 使用简单密码哈希
            hashed_password = get_password_hash("admin")
            admin_user = User(username="admin", hashed_password=hashed_password, role="admin")
            db.add(admin_user)
            db.commit()
            print("✅ 默认管理员用户创建成功")
        except Exception as e:
            print(f"⚠️  创建默认管理员失败: {e}")
    db.close()

@app.post("/api/auth/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    access_token = create_access_token(data={"sub": user.username, "user_id": user.id, "role": user.role})
    return LoginResponse(
        access_token=access_token,
        user=UserResponse(id=user.id, username=user.username, role=user.role, created_at=user.created_at)
    )

@app.get("/api/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    users = db.query(User).all()
    return users

@app.post("/api/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="不能删除管理员账号")
    db.delete(user)
    db.commit()
    return {"message": "用户删除成功"}

@app.get("/api/machines", response_model=List[MachineResponse])
def get_machines(db: Session = Depends(get_db), request: Request = None):
    import time
    start_time = time.time()
    print(f"GET /api/machines 开始处理: {start_time}")
    
    verify_token_time = time.time()
    verify_token(request)
    print(f"GET /api/machines verify_token 耗时: {time.time() - verify_token_time:.4f} 秒")
    
    db_query_time = time.time()
    machines = db.query(Machine).all()
    print(f"GET /api/machines 数据库查询耗时: {time.time() - db_query_time:.4f} 秒")
    
    # 不再动态检查状态，只返回基本信息
    end_time = time.time()
    print(f"GET /api/machines 总处理时间: {end_time - start_time:.4f} 秒")
    return machines

@app.post("/api/machines", response_model=MachineResponse)
def create_machine(machine: MachineCreate, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    existing = db.query(Machine).filter(Machine.machine_code == machine.machine_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="机台编号已存在")
    
    db_machine = Machine(**machine.model_dump())
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    return db_machine

@app.put("/api/machines/{machine_id}", response_model=MachineResponse)
def update_machine(machine_id: int, machine: MachineUpdate, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    db_machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not db_machine:
        raise HTTPException(status_code=404, detail="机台不存在")
    
    for key, value in machine.model_dump(exclude_unset=True).items():
        setattr(db_machine, key, value)
    
    db.commit()
    db.refresh(db_machine)
    return db_machine

@app.delete("/api/machines/{machine_id}")
def delete_machine(machine_id: int, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="机台不存在")
    db.delete(machine)
    db.commit()
    return {"message": "机台删除成功"}

@app.get("/api/machines/status")
def check_machines_status(db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    machines = db.query(Machine).all()
    status_list = []
    
    # 检查每个机台的PLC连接状态
    for machine in machines:
        status = "离线"
        if machine.ip_address:
            plc = PLCClient(machine.ip_address, machine.rack, machine.slot)
            try:
                if plc.connect():
                    status = "在线"
                else:
                    status = "离线"
            except Exception as e:
                status = "错误"
            finally:
                plc.disconnect()
        
        status_list.append({"id": machine.id, "status": status})
    
    return status_list

@app.get("/api/machines/{machine_id}/read")
def read_machine_parameters(machine_id: int, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="机台不存在")
    
    if not machine.ip_address:
        raise HTTPException(status_code=400, detail="机台未配置IP地址")
    
    print(f"开始读取机台 {machine.machine_name} (IP: {machine.ip_address}, Rack: {machine.rack}, Slot: {machine.slot})")
    
    plc = PLCClient(machine.ip_address, machine.rack, machine.slot)
    if not plc.connect():
        raise HTTPException(status_code=500, detail=f"PLC连接失败，请检查IP地址、Rack和Slot配置")
    
    parameters = db.query(ProcessParameter).filter(
        ProcessParameter.machine_id == machine_id,
        ProcessParameter.is_active == True
    ).all()
    
    if not parameters:
        plc.disconnect()
        raise HTTPException(status_code=404, detail="该机台没有配置工艺参数，请先添加工艺参数")
    
    results = {}
    success_count = 0
    error_count = 0
    
    for param in parameters:
        try:
            value = plc.read_parameter(param.parameter_address, param.parameter_type)
            if value is not None:
                results[param.parameter_name] = {
                    "address": param.parameter_address,
                    "value": value,
                    "unit": param.parameter_unit,
                    "type": param.parameter_type
                }
                success_count += 1
            else:
                print(f"读取参数 {param.parameter_name} ({param.parameter_address}) 失败: 返回值为None")
                error_count += 1
        except Exception as e:
            print(f"读取参数 {param.parameter_name} ({param.parameter_address}) 错误: {e}")
            error_count += 1
    
    plc.disconnect()
    
    print(f"读取完成: 成功 {success_count}, 失败 {error_count}")
    
    if not results:
        raise HTTPException(status_code=500, detail="所有参数读取失败，请检查PLC连接和参数地址配置")
    
    return {"machine": machine, "parameters": results}

@app.post("/api/machines/{machine_id}/write")
def write_machine_parameters(
    machine_id: int, 
    request: PLCWriteRequest, 
    db: Session = Depends(get_db), 
    req: Request = None
):
    verify_token(req)
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="机台不存在")
    
    if not machine.ip_address:
        raise HTTPException(status_code=400, detail="机台未配置IP地址")
    
    plc = PLCClient(machine.ip_address, machine.rack, machine.slot)
    if not plc.connect():
        raise HTTPException(status_code=500, detail="PLC连接失败")
    
    results = {}
    for param_name, param_data in request.parameters.items():
        success = plc.write_parameter(param_data.address, param_data.value, param_data.type)
        results[param_name] = success
    
    plc.disconnect()
    return {"success": True, "results": results}

@app.get("/api/products", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    return db.query(Product).all()

@app.post("/api/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    existing = db.query(Product).filter(Product.product_code == product.product_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="产品编号已存在")
    
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.put("/api/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    for key, value in product.model_dump(exclude_unset=True).items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    db.delete(product)
    db.commit()
    return {"message": "产品删除成功"}

@app.get("/api/process-parameters")
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

@app.post("/api/process-parameters")
def save_process_parameters(request: ParameterSaveRequest, db: Session = Depends(get_db), req: Request = None):
    verify_token(req)
    
    # 提取用户信息从token
    token_payload = verify_token(req)
    user_id = token_payload.get("user_id")
    
    # 打印接收到的备注信息
    print(f"Received notes: {request.notes}")
    
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
    
    # 创建工艺记录
    last_record = db.query(ProcessRecord).filter(
        ProcessRecord.machine_id == request.machine_id,
        ProcessRecord.product_id == request.product_id
    ).order_by(ProcessRecord.version.desc()).first()
    
    version = 1
    if last_record:
        version = last_record.version + 1
    
    # 创建工艺记录
    record = ProcessRecord(
        machine_id=request.machine_id,
        product_id=request.product_id,
        operator_id=user_id,
        notes=request.notes,
        version=version
    )
    db.add(record)
    db.flush()  # 确保record.id已生成
    
    # 处理参数快照
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
    return {"message": "工艺参数保存成功"}

@app.post("/api/process-parameters/bind")
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

@app.get("/api/process-records")
def get_process_records(
    machine_id: Optional[int] = None,
    product_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    request: Request = None
):
    verify_token(request)
    query = db.query(ProcessRecord)
    
    if machine_id:
        query = query.filter(ProcessRecord.machine_id == machine_id)
    if product_id:
        query = query.filter(ProcessRecord.product_id == product_id)
    
    records = query.order_by(ProcessRecord.record_time.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "machine_id": r.machine_id,
            "product_id": r.product_id,
            "operator_id": r.operator_id,
            "record_time": r.record_time,
            "notes": r.notes,
            "version": r.version,  # 添加版本号
            "parameters_snapshot": {  # 转换为前端需要的格式
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

@app.post("/api/process-records")
def create_process_record(request: ProcessRecordCreate, db: Session = Depends(get_db), req: Request = None):
    verify_token(req)
    
    # 计算版本号
    last_record = db.query(ProcessRecord).filter(
        ProcessRecord.machine_id == request.machine_id,
        ProcessRecord.product_id == request.product_id
    ).order_by(ProcessRecord.version.desc()).first()
    
    version = 1
    if last_record:
        version = last_record.version + 1
    
    # 创建工艺记录
    record = ProcessRecord(
        machine_id=request.machine_id,
        product_id=request.product_id,
        operator_id=request.operator_id,
        notes=request.notes,
        version=version
    )
    db.add(record)
    db.flush()  # 确保record.id已生成
    
    # 处理参数快照
    if request.parameters_snapshot:
        for param_name, param_info in request.parameters_snapshot.items():
            if isinstance(param_info, dict):
                param_value = ProcessParameterValue(
                    process_record_id=record.id,
                    parameter_name=param_name,
                    parameter_address=param_info.get("address", ""),
                    parameter_value=str(param_info.get("value", "")),
                    parameter_unit=param_info.get("unit", ""),
                    parameter_type=param_info.get("type", "Int")
                )
                db.add(param_value)
    
    db.commit()
    db.refresh(record)
    return {"id": record.id, "message": "工艺记录保存成功", "version": record.version}

@app.post("/api/process-records/{record_id}/write-to-plc")
def write_record_to_plc(record_id: int, db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    
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
        try:
            # 尝试将字符串值转换为适当的类型
            value = param.parameter_value
            if param.parameter_type == "Real":
                value = float(value)
            elif param.parameter_type == "Int":
                value = int(value)
            elif param.parameter_type == "Bool":
                value = value.lower() == "true"
            
            success = plc.write_parameter(param.parameter_address, value, param.parameter_type)
            results[param.parameter_name] = success
        except Exception as e:
            results[param.parameter_name] = False
    
    plc.disconnect()
    return {"success": True, "results": results}

@app.get("/api/process-parameters/template")
def get_parameter_template(db: Session = Depends(get_db), request: Request = None):
    verify_token(request)
    # 获取默认机台的工艺参数作为模板
    default_machine = db.query(Machine).filter(Machine.machine_code == 'DEFAULT').first()
    if not default_machine:
        raise HTTPException(status_code=404, detail="默认机台不存在")
    
    parameters = db.query(ProcessParameter).filter(
        ProcessParameter.machine_id == default_machine.id,
        ProcessParameter.is_active == True
    ).all()
    
    if not parameters:
        raise HTTPException(status_code=404, detail="默认机台没有工艺参数模板")
    
    # 转换为前端需要的格式
    template = []
    for param in parameters:
        template.append({
            "parameter_name": param.parameter_name,
            "parameter_address": param.parameter_address,
            "parameter_value": param.parameter_value,
            "parameter_unit": param.parameter_unit,
            "parameter_type": param.parameter_type
        })
    
    return {"template": template}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
