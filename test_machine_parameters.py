#!/usr/bin/env python3
"""
测试机台工艺参数
"""

import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from backend.database import engine, SessionLocal
from backend.models import Machine, ProcessParameter

# 创建数据库会话
db = SessionLocal()

print("=== 测试机台工艺参数 ===")

# 查询所有机台
machines = db.query(Machine).all()
print(f"数据库中机台数量: {len(machines)}")

for machine in machines:
    print(f"\n机台: {machine.machine_name} (ID: {machine.id})")
    # 查询该机台的工艺参数
    parameters = db.query(ProcessParameter).filter(ProcessParameter.machine_id == machine.id).all()
    print(f"  工艺参数数量: {len(parameters)}")
    for param in parameters[:5]:  # 只显示前5个参数
        print(f"  - {param.parameter_name}: {param.parameter_address} ({param.parameter_type})")
    if len(parameters) > 5:
        print(f"  ... 还有 {len(parameters) - 5} 个参数")

print("\n=== 测试完成 ===")

# 关闭会话
db.close()