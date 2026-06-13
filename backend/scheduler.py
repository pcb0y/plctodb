"""
PLC参数定时采集任务
每分钟从所有在线机台的PLC读取参数值，存入parameter_collection表
使用长连接模式：维护每台机台的持久PLC连接，断线自动重连
"""
import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Machine, TemplateParameter, ParameterCollection
from plc_client import PLCClient

logger = logging.getLogger(__name__)

# 采集间隔（秒）
COLLECT_INTERVAL = 60

# 运行标志
_running = False

# PLC长连接池: {machine_id: PLCClient}
_connection_pool: dict = {}


def _get_or_create_connection(machine: Machine, first_slot: int) -> PLCClient:
    """获取或创建PLC长连接，断线自动重连"""
    machine_id = machine.id
    plc = _connection_pool.get(machine_id)

    if plc is not None:
        # 检查连接是否仍然有效（IP没变）
        if plc.ip != machine.ip_address:
            logger.info(f"机台 {machine.machine_name} IP变更 ({plc.ip} -> {machine.ip_address})，重建连接")
            plc.disconnect()
            plc = None
        elif plc.client and plc.client.get_connected():
            return plc
        else:
            # 连接已断开，尝试重连
            logger.info(f"机台 {machine.machine_name} 连接断开，尝试重连...")
            plc.slot = first_slot
            if plc.connect():
                return plc
            plc = None

    # 创建新连接
    plc = PLCClient(machine.ip_address, machine.rack or 0, first_slot)
    if plc.connect():
        _connection_pool[machine_id] = plc
        logger.info(f"机台 {machine.machine_name} 建立长连接成功")
        return plc
    else:
        logger.warning(f"机台 {machine.machine_name} ({machine.ip_address}) 连接失败")
        return None


def _cleanup_pool():
    """关闭所有长连接"""
    for machine_id, plc in _connection_pool.items():
        try:
            plc.disconnect()
        except Exception:
            pass
    _connection_pool.clear()
    logger.info("PLC长连接池已清空")


async def collect_parameters():
    """单次采集：遍历所有有IP且绑定了模板的机台，读取参数并存库"""
    db: Session = SessionLocal()
    try:
        machines = db.query(Machine).filter(
            Machine.ip_address.isnot(None),
            Machine.ip_address != "",
            Machine.template_id.isnot(None)
        ).all()

        if not machines:
            return

        active_machine_ids = set()
        for machine in machines:
            try:
                await _collect_machine_parameters(db, machine)
                active_machine_ids.add(machine.id)
            except Exception as e:
                logger.warning(f"采集机台 {machine.machine_name}({machine.ip_address}) 参数失败: {e}")

        # 清理已移除机台的连接
        stale_ids = set(_connection_pool.keys()) - active_machine_ids
        for mid in stale_ids:
            plc = _connection_pool.pop(mid, None)
            if plc:
                plc.disconnect()
                logger.info(f"清理已移除机台(id={mid})的长连接")

        db.commit()
    except Exception as e:
        logger.error(f"采集任务异常: {e}")
        db.rollback()
    finally:
        db.close()


async def _collect_machine_parameters(db: Session, machine: Machine):
    """采集单台机台的PLC参数（使用长连接）"""
    # 获取模板参数列表
    template_params = db.query(TemplateParameter).filter(
        TemplateParameter.template_id == machine.template_id
    ).all()

    if not template_params:
        return

    # 按slot分组排序，避免频繁断连重连
    sorted_params = sorted(template_params, key=lambda p: p.slot if p.slot is not None else (machine.slot or 1))

    # 用第一个参数的slot获取连接
    first_slot = sorted_params[0].slot if sorted_params[0].slot is not None else (machine.slot or 1)
    plc = _get_or_create_connection(machine, first_slot)
    if not plc:
        return

    try:
        now = datetime.now()
        records = []

        for param in sorted_params:
            slot = param.slot if param.slot is not None else (machine.slot or 1)
            value = plc.read_parameter(param.parameter_address, param.parameter_type, slot)

            # 转换为数值存储，非数值型跳过
            numeric_value = None
            if value is not None:
                try:
                    if isinstance(value, bool):
                        numeric_value = 1.0 if value else 0.0
                    else:
                        numeric_value = float(value)
                except (ValueError, TypeError):
                    continue

            records.append(ParameterCollection(
                machine_id=machine.id,
                parameter_name=param.parameter_name,
                parameter_address=param.parameter_address,
                parameter_value=numeric_value,
                parameter_unit=param.parameter_unit or "",
                parameter_type=param.parameter_type or "Int",
                collected_at=now
            ))

        if records:
            db.add_all(records)
            logger.info(f"机台 {machine.machine_name} 采集 {len(records)} 条参数记录")
    except Exception as e:
        # 采集异常可能是连接出了问题，标记下次重连
        logger.error(f"机台 {machine.machine_name} 读取参数异常: {e}")
        plc = _connection_pool.pop(machine.id, None)
        if plc:
            plc.disconnect()


async def start_scheduler():
    """启动定时采集循环"""
    global _running
    _running = True
    logger.info(f"参数采集任务已启动（长连接模式），间隔 {COLLECT_INTERVAL} 秒")

    while _running:
        try:
            await collect_parameters()
        except Exception as e:
            logger.error(f"采集循环异常: {e}")
        await asyncio.sleep(COLLECT_INTERVAL)


def stop_scheduler():
    """停止定时采集"""
    global _running
    _running = False
    _cleanup_pool()
    logger.info("参数采集任务已停止")
