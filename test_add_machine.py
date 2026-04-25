#!/usr/bin/env python3
"""
测试添加机台的API
"""

import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from backend.database import engine, SessionLocal
from backend.models import Machine

# 创建数据库会话
db = SessionLocal()

print("=== 测试添加机台 ===")

# 测试添加一个新的机台
new_machine = Machine(
    machine_code="TEST001",
    machine_name="测试机台",
    machine_type="S7-200",
    ip_address="192.168.1.100",
    rack=0,
    slot=1
)

try:
    db.add(new_machine)
    db.commit()
    db.refresh(new_machine)
    print(f"✅ 成功添加机台: ID={new_machine.id}, 编号={new_machine.machine_code}")
    
except Exception as e:
    print(f"❌ 添加机台失败: {e}")
    db.rollback()

print("\n=== 查看所有机台 ===")

# 查询所有机台
machines = db.query(Machine).all()
print(f"数据库中机台数量: {len(machines)}")

for machine in machines:
    print(f"ID: {machine.id}, 编号: {machine.machine_code}, 名称: {machine.machine_name}, IP: {machine.ip_address}")

print("\n=== 测试完成 ===")

# 关闭会话
db.close()