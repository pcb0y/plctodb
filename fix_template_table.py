#!/usr/bin/env python3

"""
修复 templates 表结构，移除 machine_id 字段
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
    # 检查 templates 表是否存在 machine_id 列
    cursor.execute("SHOW COLUMNS FROM templates LIKE 'machine_id'")
    result = cursor.fetchone()
    
    if result:
        # 先检查并移除外键约束
        cursor.execute("SHOW CREATE TABLE templates")
        create_table_sql = cursor.fetchone()[1]
        
        # 查找外键约束名称
        import re
        fk_match = re.search(r'CONSTRAINT `(.*?)` FOREIGN KEY \(`machine_id`\)', create_table_sql)
        if fk_match:
            fk_name = fk_match.group(1)
            cursor.execute(f"ALTER TABLE templates DROP FOREIGN KEY `{fk_name}`")
            print(f"✅ 已移除外键约束 {fk_name}")
        
        # 移除 machine_id 列
        cursor.execute("ALTER TABLE templates DROP COLUMN machine_id")
        print("✅ 已从 templates 表中移除 machine_id 列")
    else:
        print("⚠️  templates 表中不存在 machine_id 列")
    
    conn.commit()
    print("✅ 数据库更新成功")
    
except Exception as e:
    print(f"❌ 数据库更新失败: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()