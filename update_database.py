#!/usr/bin/env python3

"""
更新数据库表结构，添加缺失的列
"""

import pymysql
from backend.config import DB_CONFIG

# 连接到 MySQL 服务器
conn = pymysql.connect(
    host=DB_CONFIG["host"],
    user=DB_CONFIG["user"],
    password=DB_CONFIG["password"],
    port=DB_CONFIG["port"],
    db=DB_CONFIG["database"]
)

cursor = conn.cursor()

try:
    # 检查 machines 表是否存在 template_id 列
    cursor.execute("SHOW COLUMNS FROM machines LIKE 'template_id'")
    result = cursor.fetchone()
    
    if not result:
        # 添加 template_id 列
        cursor.execute("ALTER TABLE machines ADD COLUMN template_id INT NULL, ADD FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE SET NULL")
        print("✅ 已添加 template_id 列到 machines 表")
    else:
        print("⚠️  template_id 列已存在")
    
    conn.commit()
    print("✅ 数据库更新成功")
    
except Exception as e:
    print(f"❌ 数据库更新失败: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()