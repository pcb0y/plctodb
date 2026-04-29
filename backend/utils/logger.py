import os
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import OperationLog

LOG_DIR = "/Users/zong/code/plctodb/logs"
MAX_LOG_AGE_DAYS = 180

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def get_today_log_file():
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"operation_{today}.log")

def cleanup_old_logs():
    try:
        cutoff_date = datetime.now() - timedelta(days=MAX_LOG_AGE_DAYS)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")
        
        for filename in os.listdir(LOG_DIR):
            if filename.startswith("operation_") and filename.endswith(".log"):
                date_str = filename.replace("operation_", "").replace(".log", "")
                if date_str < cutoff_str:
                    file_path = os.path.join(LOG_DIR, filename)
                    os.remove(file_path)
                    print(f"删除旧日志文件: {filename}")
    except Exception as e:
        print(f"清理旧日志文件失败: {e}")

def write_to_file(operation_type, target_type, user_id, details, request_data=None, response_data=None):
    try:
        log_file = get_today_log_file()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_lines = []
        log_lines.append(f"{timestamp} | {operation_type} | {target_type} | 用户ID:{user_id}")
        
        if request_data:
            try:
                request_str = json.dumps(request_data, ensure_ascii=False, indent=2)
                log_lines.append(f"请求参数:\n{request_str}")
            except:
                log_lines.append(f"请求参数: {str(request_data)[:1000]}")
        
        if details:
            log_lines.append(f"详情: {details}")
        
        if response_data:
            try:
                response_str = json.dumps(response_data, ensure_ascii=False, indent=2)
                log_lines.append(f"返回结果:\n{response_str}")
            except:
                log_lines.append(f"返回结果: {str(response_data)[:1000]}")
        
        log_lines.append("-" * 60)
        log_content = "\n".join(log_lines) + "\n"
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_content)
    except Exception as e:
        print(f"写入日志文件失败: {e}")

def log_operation(db: Session, user_id: int, operation_type: str, target_type: str, target_id: int = None, details: str = None, request_data=None, response_data=None):
    try:
        request_params_json = json.dumps(request_data, ensure_ascii=False) if request_data else None
        response_data_json = json.dumps(response_data, ensure_ascii=False) if response_data else None
        
        log_entry = OperationLog(
            user_id=user_id,
            operation_type=operation_type,
            target_type=target_type,
            target_id=target_id,
            details=details,
            request_params=request_params_json,
            response_data=response_data_json
        )
        db.add(log_entry)
        db.commit()
        
        write_to_file(operation_type, target_type, user_id, details, request_data, response_data)
        
        cleanup_old_logs()
    except Exception as e:
        print(f"记录操作日志失败: {e}")
        db.rollback()

def log_plc_read(db: Session, user_id: int, machine_id: int, machine_name: str, parameters: dict = None, response_data=None):
    details = f"机台: {machine_name} (ID: {machine_id})"
    if parameters:
        details += f", 参数数量: {len(parameters)}"
    
    params_info = {}
    if parameters:
        for param_name, param_data in parameters.items():
            params_info[param_name] = {
                "address": param_data.get("address", ""),
                "value": param_data.get("value", ""),
                "unit": param_data.get("unit", ""),
                "type": param_data.get("type", "")
            }
    
    log_operation(db, user_id, "读取PLC", "机台", machine_id, details, params_info, response_data)

def log_plc_write(db: Session, user_id: int, machine_id: int, machine_name: str, parameters: dict = None, response_data=None):
    details = f"机台: {machine_name} (ID: {machine_id})"
    if parameters:
        details += f", 写入参数数量: {len(parameters)}"
    
    params_info = {}
    if parameters:
        for param_name, param_data in parameters.items():
            params_info[param_name] = {
                "address": param_data.get("address", ""),
                "value": param_data.get("value", ""),
                "type": param_data.get("type", "")
            }
    
    log_operation(db, user_id, "写入PLC", "机台", machine_id, details, params_info, response_data)

def log_machine_create(db: Session, user_id: int, machine_id: int, machine_name: str, request_data=None, response_data=None):
    log_operation(db, user_id, "创建", "机台", machine_id, f"创建机台: {machine_name}", request_data, response_data)

def log_machine_update(db: Session, user_id: int, machine_id: int, machine_name: str, request_data=None, response_data=None):
    log_operation(db, user_id, "更新", "机台", machine_id, f"更新机台: {machine_name}", request_data, response_data)

def log_machine_delete(db: Session, user_id: int, machine_id: int, machine_name: str):
    log_operation(db, user_id, "删除", "机台", machine_id, f"删除机台: {machine_name}")

def log_product_create(db: Session, user_id: int, product_id: int, product_name: str, request_data=None, response_data=None):
    log_operation(db, user_id, "创建", "产品", product_id, f"创建产品: {product_name}", request_data, response_data)

def log_product_update(db: Session, user_id: int, product_id: int, product_name: str, request_data=None, response_data=None):
    log_operation(db, user_id, "更新", "产品", product_id, f"更新产品: {product_name}", request_data, response_data)

def log_product_delete(db: Session, user_id: int, product_id: int, product_name: str):
    log_operation(db, user_id, "删除", "产品", product_id, f"删除产品: {product_name}")

def log_template_create(db: Session, user_id: int, template_id: int, template_name: str, request_data=None, response_data=None):
    log_operation(db, user_id, "创建", "模板", template_id, f"创建模板: {template_name}", request_data, response_data)

def log_template_update(db: Session, user_id: int, template_id: int, template_name: str, request_data=None, response_data=None):
    log_operation(db, user_id, "更新", "模板", template_id, f"更新模板: {template_name}", request_data, response_data)

def log_template_delete(db: Session, user_id: int, template_id: int, template_name: str):
    log_operation(db, user_id, "删除", "模板", template_id, f"删除模板: {template_name}")

def log_parameter_save(db: Session, user_id: int, machine_id: int, product_id: int = None, parameters: list = None, response_data=None):
    details = f"机台ID: {machine_id}"
    if product_id:
        details += f", 产品ID: {product_id}"
    if parameters:
        details += f", 参数数量: {len(parameters)}"
    
    params_info = []
    if parameters:
        for param in parameters:
            params_info.append({
                "name": param.get("parameter_name", "") if isinstance(param, dict) else getattr(param, "parameter_name", ""),
                "address": param.get("parameter_address", "") if isinstance(param, dict) else getattr(param, "parameter_address", ""),
                "value": param.get("parameter_value", "") if isinstance(param, dict) else getattr(param, "parameter_value", ""),
                "unit": param.get("parameter_unit", "") if isinstance(param, dict) else getattr(param, "parameter_unit", ""),
                "type": param.get("parameter_type", "") if isinstance(param, dict) else getattr(param, "parameter_type", "")
            })
    
    log_operation(db, user_id, "保存", "参数", machine_id, details, params_info, response_data)

def log_record_write_to_plc(db: Session, user_id: int, record_id: int, machine_id: int, parameters: list = None, response_data=None):
    details = f"记录ID: {record_id}, 机台ID: {machine_id}"
    
    params_info = []
    if parameters:
        for param in parameters:
            params_info.append({
                "name": getattr(param, "parameter_name", ""),
                "address": getattr(param, "parameter_address", ""),
                "value": getattr(param, "parameter_value", ""),
                "unit": getattr(param, "parameter_unit", ""),
                "type": getattr(param, "parameter_type", ""),
                "readonly": getattr(param, "is_readonly", False)
            })
    
    log_operation(db, user_id, "写入PLC", "记录", record_id, details, params_info, response_data)

def log_user_create(db: Session, user_id: int, new_user_id: int, username: str, request_data=None, response_data=None):
    log_operation(db, user_id, "创建", "用户", new_user_id, f"创建用户: {username}", request_data, response_data)

def log_user_delete(db: Session, user_id: int, deleted_user_id: int, username: str):
    log_operation(db, user_id, "删除", "用户", deleted_user_id, f"删除用户: {username}")

def log_password_change(db: Session, user_id: int, target_user_id: int):
    log_operation(db, user_id, "更新", "密码", target_user_id, f"修改密码, 用户ID: {target_user_id}")

def log_template_bind(db: Session, user_id: int, machine_id: int, template_id: int, request_data=None, response_data=None):
    log_operation(db, user_id, "绑定", "模板", machine_id, f"机台ID: {machine_id}, 模板ID: {template_id}", request_data, response_data)

def log_template_unbind(db: Session, user_id: int, machine_id: int, response_data=None):
    log_operation(db, user_id, "解绑", "模板", machine_id, f"机台ID: {machine_id}", None, response_data)