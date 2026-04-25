#!/usr/bin/env python3
"""
将 s7.py 中的示例数据导入到数据库
"""

import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from backend.database import engine, Base, SessionLocal
from backend.models import Machine, Product, ProcessParameter, AlarmParameter

# 从 s7.py 中提取数据点
def extract_data_points():
    """从 s7.py 文件中提取数据点"""
    data_points = []
    alarm_points = []
    
    with open('s7.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
        # 提取 data_points
        import re
        data_points_match = re.search(r'data_points = \[(.*?)\]', content, re.DOTALL)
        if data_points_match:
            data_points_str = data_points_match.group(1)
            # 解析数据点
            for line in data_points_str.split('\n'):
                line = line.strip()
                if line.startswith('(') and line.endswith('),'):
                    # 提取元组内容
                    line = line[1:-2].strip()
                    parts = line.split(',')
                    if len(parts) >= 4:
                        func = parts[0].strip().strip('"')
                        address = parts[1].strip().strip('"')
                        data_type = parts[2].strip().strip('"')
                        unit = parts[3].strip().strip('"')
                        data_points.append((func, address, data_type, unit))
        
        # 提取 alarm_points
        alarm_points_match = re.search(r'alarm_points = \[(.*?)\]', content, re.DOTALL)
        if alarm_points_match:
            alarm_points_str = alarm_points_match.group(1)
            # 解析报警点
            for line in alarm_points_str.split('\n'):
                line = line.strip()
                if line.startswith('(') and line.endswith('),'):
                    # 提取元组内容
                    line = line[1:-2].strip()
                    parts = line.split(',', 1)
                    if len(parts) >= 2:
                        address = parts[0].strip().strip('"')
                        alarm_content = parts[1].strip().strip('"')
                        alarm_points.append((address, alarm_content))
    
    return data_points, alarm_points

def main():
    """主函数"""
    print("正在从 s7.py 提取数据点...")
    data_points, alarm_points = extract_data_points()
    
    print(f"提取到 {len(data_points)} 个工艺参数点")
    print(f"提取到 {len(alarm_points)} 个报警点")
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 检查是否已有默认机台
        machine = db.query(Machine).filter(Machine.machine_code == 'DEFAULT').first()
        if not machine:
            # 创建默认机台
            machine = Machine(
                machine_code='DEFAULT',
                machine_name='默认挤出机',
                machine_type='S7-200',
                ip_address='192.168.18.223',
                rack=0,
                slot=1
            )
            db.add(machine)
            db.commit()
            db.refresh(machine)
            print("✅ 创建默认机台成功")
        else:
            print("✅ 默认机台已存在")
        
        # 检查是否已有默认产品
        product = db.query(Product).filter(Product.product_code == 'DEFAULT').first()
        if not product:
            # 创建默认产品
            product = Product(
                product_code='DEFAULT',
                product_name='默认产品',
                product_spec='标准规格'
            )
            db.add(product)
            db.commit()
            db.refresh(product)
            print("✅ 创建默认产品成功")
        else:
            print("✅ 默认产品已存在")
        
        # 导入工艺参数
        print("正在导入工艺参数...")
        imported_count = 0
        for func, address, data_type, unit in data_points:
            # 跳过空地址
            if not address:
                continue
            
            # 跳过计数器地址
            if address.startswith('C'):
                continue
            
            # 检查是否已存在
            existing = db.query(ProcessParameter).filter(
                ProcessParameter.machine_id == machine.id,
                ProcessParameter.product_id == product.id,
                ProcessParameter.parameter_name == func
            ).first()
            
            if existing:
                # 更新现有参数
                existing.parameter_address = address
                existing.parameter_type = data_type
                existing.parameter_unit = unit
            else:
                # 创建新参数
                param = ProcessParameter(
                    machine_id=machine.id,
                    product_id=product.id,
                    parameter_name=func,
                    parameter_address=address,
                    parameter_type=data_type,
                    parameter_unit=unit
                )
                db.add(param)
                imported_count += 1
        
        # 导入报警点
        print("正在导入报警点...")
        alarm_imported_count = 0
        for address, alarm_content in alarm_points:
            # 检查是否已存在
            existing = db.query(AlarmParameter).filter(
                AlarmParameter.machine_id == machine.id,
                AlarmParameter.alarm_address == address
            ).first()
            
            if existing:
                # 更新现有报警点
                existing.alarm_content = alarm_content
            else:
                # 创建新报警点
                alarm = AlarmParameter(
                    machine_id=machine.id,
                    alarm_address=address,
                    alarm_content=alarm_content
                )
                db.add(alarm)
                alarm_imported_count += 1
        
        db.commit()
        print(f"✅ 成功导入 {imported_count} 个工艺参数")
        print(f"✅ 成功导入 {alarm_imported_count} 个报警点")
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()