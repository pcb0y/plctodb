#!/usr/bin/env python3
"""
更新数据库表结构
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from backend.database import engine, SessionLocal
from backend.models import Base, ProcessRecord, ProcessParameterValue

print("=== 更新数据库表结构 ===")

# 检查数据库连接
print("1. 连接数据库...")
try:
    db = SessionLocal()
    # 测试连接
    db.execute(text("SELECT 1"))
    print("✅ 数据库连接成功")
    db.close()
except Exception as e:
    print(f"❌ 数据库连接失败: {e}")
    sys.exit(1)

# 添加version字段到process_records表
print("\n2. 添加version字段到process_records表...")
try:
    with engine.connect() as conn:
        # 尝试添加version字段
        try:
            conn.execute(text("ALTER TABLE process_records ADD COLUMN version INT DEFAULT 1"))
            conn.commit()
            print("✅ version字段添加成功")
        except Exception as e:
            print(f"⚠️ version字段可能已存在: {e}")
except Exception as e:
    print(f"❌ 添加version字段失败: {e}")

# 创建process_parameter_values表
print("\n3. 创建process_parameter_values表...")
try:
    # 创建表
    Base.metadata.create_all(engine, tables=[ProcessParameterValue.__table__])
    print("✅ process_parameter_values表创建成功")
except Exception as e:
    print(f"❌ 创建process_parameter_values表失败: {e}")

print("\n=== 数据库表结构更新完成 ===")