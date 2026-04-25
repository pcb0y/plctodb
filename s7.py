#!/usr/bin/env python3
"""
西门子 S7 协议读取数据示例
读取 PLC: 192.168.18.223:102
"""

import snap7
from snap7.util import *
import time

def read_s7_plc():
    """读取 S7 PLC 数据"""
    # 创建客户端
    client = snap7.client.Client()
    
    try:
        # 连接 PLC
        print("正在连接 PLC: 192.168.18.223:102")
        client.connect('192.168.18.223', 0, 1, 102)  # IP, rack, slot, port
        
        if client.get_connected():
            print("✅ PLC 连接成功")
        else:
            print("❌ PLC 连接失败")
            return
        
        # 读取 VW302 (Int, 16位整数)
        print("\n读取 VW302 (Int 16位整数):")
        start_address = 302
        size = 2  # 2字节
        
        # 对于 S7-200，V 存储区映射到 DB1
        db_number = 1
        data = client.read_area(snap7.client.S7Area.DB, db_number, start_address, size)
        value = get_int(data, 0)
        print(f"VW302 = {value}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        # 断开连接
        if client.get_connected():
            client.disconnect()
            print("\n✅ PLC 连接已断开")

if __name__ == "__main__":
    # 安装依赖: pip install python-snap7
    try:
        import snap7
        read_s7_plc()
    except ImportError:
        print("请先安装 python-snap7 库:")
        print("pip install python-snap7")