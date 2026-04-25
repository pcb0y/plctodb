#!/usr/bin/env python3
"""
测试机台API是否正常返回数据
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

print("=== 测试机台数据 ===")

# 查询所有机台
machines = db.query(Machine).all()
print(f"数据库中机台数量: {len(machines)}")

for machine in machines:
    print(f"ID: {machine.id}, 编号: {machine.machine_code}, 名称: {machine.machine_name}, IP: {machine.ip_address}")

print("\n=== 测试完成 ===")

# 关闭会话
db.close()