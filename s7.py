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
        client.connect('192.168.18.223', 1, 2, 102)  # IP, rack, slot, port
        
        if client.get_connected():
            print("✅ PLC 连接成功")
        else:
            print("❌ PLC 连接失败")
            return
        
        # 读取数据点定义
        data_points = [
            # 功能, 地址, 数据类型, 计量单位
            ("编号", "C3", "Int", ""),
            ("保温时长", "C3", "Int", "s"),
            ("主机报警", "VW132", "Int", ""),
            ("喂料报警", "VW132", "Int", ""),
            ("主机状态", "", "", ""),
            ("主机转速 SV", "VD208", "Real", ""),
            ("主机转速 PV", "VD232", "Real", "°C"),
            ("主机电流 SV", "VD256", "Real", "%"),
            ("主机电流 PV", "VD3300", "Real", "A"),
            ("喂料转速 SV", "VD32", "Real", "°C"),
            ("喂料转速 PV", "VD244", "Real", "°C"),
            ("喂料电流 SV", "VD260", "Real", "%"),
            ("喂料电流 PV", "VD3304", "Real", "A"),
            ("机筒1区 SV", "VW102", "Int", "°C"),
            ("机筒1区 PV", "VW302", "Int", "°C"),
            ("机筒2区 SV", "VW104", "Int", "°C"),
            ("机筒2区 PV", "VW304", "Int", "°C"),
            ("机筒3区 SV", "VW106", "Int", "°C"),
            ("机筒3区 PV", "VW306", "Int", "°C"),
            ("机筒4区 SV", "VW108", "Int", "°C"),
            ("机筒4区 PV", "VW308", "Int", "°C"),
            ("合流区 SV", "VW154", "Int", "°C"),
            ("合流区 PV", "VW384", "Int", "°C"),
            ("芯层-挤出 ED1 SV", "VW1130", "Int", "°C"),
            ("芯层-挤出 ED1 PV", "VW330", "Int", "°C"),
            ("芯层-挤出 ED2 SV", "VW1132", "Int", "°C"),
            ("芯层-挤出 ED2 PV", "VW332", "Int", "°C"),
            ("芯层-挤出 ED3 SV", "VW1134", "Int", "°C"),
            ("芯层-挤出 ED3 PV", "VW334", "Int", "°C"),
            ("芯层-挤出 ED4 SV", "VW1136", "Int", "°C"),
            ("芯层-挤出 ED4 PV", "VW336", "Int", "°C"),
            ("芯层-挤出 ED5 SV", "VW1138", "Int", "°C"),
            ("芯层-挤出 ED5 PV", "VW338", "Int", "°C"),
            ("芯层-挤出 ED6 SV", "VW1140", "Int", "°C"),
            ("芯层-挤出 ED6 PV", "VW340", "Int", "°C"),
            ("芯层-挤出 ED7 SV", "VW1142", "Int", "°C"),
            ("芯层-挤出 ED7 PV", "VW342", "Int", "°C"),
            ("芯层-挤出 ED8 SV", "VW1144", "Int", "°C"),
            ("芯层-挤出 ED8 PV", "VW344", "Int", "°C"),
            ("芯层-挤出 ED9 SV", "VW1146", "Int", "°C"),
            ("芯层-挤出 ED9 PV", "VW346", "Int", "°C"),
            ("芯层-挤出 ED10 SV", "VW1148", "Int", "°C"),
            ("芯层-挤出 ED10 PV", "VW348", "Int", "°C"),
            ("芯层-挤出 ED11 SV", "VW1150", "Int", "°C"),
            ("芯层-挤出 ED11 PV", "VW350", "Int", "°C"),
            ("芯层-挤出 ED12 SV", "VW1152", "Int", "°C"),
            ("芯层-挤出 ED12 PV", "VW352", "Int", "°C"),
            ("芯层-挤出 ED13 SV", "VW1162", "Int", "°C"),
            ("芯层-挤出 ED13 PV", "VW362", "Int", "°C"),
            ("芯层-挤出 ED14 SV", "VW1164", "Int", "°C"),
            ("芯层-挤出 ED14 PV", "VW364", "Int", "°C"),
            ("供给A转速 SV", "VD508", "Real", "r/m"),
            ("供给A转速 PV", "VD532", "Real", "r/m"),
            ("供给A电流 PV", "VD2300", "Real", "%"),
            ("供给A电流 PV", "VD2512", "Real", "A"),
            ("供给B转速 SV", "VD556", "Real", "r/m"),
            ("供给B转速 PV", "VD2236", "Real", "r/m"),
            ("供给B电流 SV", "VD3380", "Real", "%"),
            ("供给B电流 PV", "VD264", "Real", "A"),
            ("供给C转速 SV", "VD212", "Real", "r/m"),
            ("供给C转速 PV", "VD532", "Real", "r/m"),
            ("供给C电流 PV", "VD2300", "Real", "%"),
            ("供给C电流 PV", "VD5082", "Real", "A"),
            ("供给D转速 SV", "VD232", "Real", "r/m"),
            ("供给D转速 PV", "VD232", "Real", "°C"),
            ("供给D电流 SV", "VD3300", "Real", "%"),
            ("供给D电流 PV", "VD256", "Real", "A"),
            ("35AEH1 SV", "VW116", "Int", "°C"),
            ("35AEH1 PV", "VW316", "Int", "°C"),
            ("35AEH2 SV", "VW118", "Int", "°C"),
            ("35AEH2 PV", "VW318", "Int", "°C"),
            ("35AEH3 SV", "VW168", "Int", "°C"),
            ("35AEH3 PV", "VW368", "Int", "°C"),
            ("35BEH1 SV", "VW170", "Int", "°C"),
            ("35BEH1 PV", "VW370", "Int", "°C"),
            ("35BEH2 SV", "VW120", "Int", "°C"),
            ("35BEH2 PV", "VW322", "Int", "°C"),
            ("35BEH3 SV", "VW112", "Int", "°C"),
            ("35BEH3 PV", "VW312", "Int", "°C"),
            ("35CEH1 SV", "VW102", "Int", "°C"),
            ("35CEH1 PV", "VW302", "Int", "°C"),
            ("35CEH2 SV", "VW104", "Int", "°C"),
            ("35CEH2 PV", "VW304", "Int", "°C"),
            ("35CEH3 SV", "VW106", "Int", "°C"),
            ("35CEH3 PV", "VW306", "Int", "°C"),
            ("35DEH1 SV", "VW108", "Int", "°C"),
            ("35DEH1 PV", "VW308", "Int", "°C"),
            ("35DEH2 SV", "VW116", "Int", "°C"),
            ("35DEH2 PV", "VW316", "Int", "°C"),
            ("35DEH3 SV", "VW118", "Int", "°C"),
            ("35DEH3 PV", "VW318", "Int", "°C"),
            ("3ED1 SV", "VW1130", "Int", "°C"),
            ("3ED1 PV", "VW330", "Int", "°C"),
            ("3ED2 SV", "VW1132", "Int", "°C"),
            ("3ED2 PV", "VW332", "Int", "°C"),
            ("4ED1 SV", "VW1134", "Int", "°C"),
            ("4ED1 PV", "VW334", "Int", "°C"),
            ("4ED2 SV", "VW1136", "Int", "°C"),
            ("4ED2 PV", "VW336", "Int", "°C"),
        ]
        
        # 报警数据点定义
        alarm_points = [
            # 地址, 报警内容
            ("M7.1", "主机料温过低"),
            ("M5.0", "主机料温过高"),
            ("M6.4", "主机熔压超限"),
            ("M5.4", "主机调速故障"),
            ("M6.6", "主机过电流"),
            ("M5.5", "共挤B调速故障"),
            ("M23.1", "喂料变频器故障"),
            ("M14.0", "螺杆异位报警"),
            ("M5.1", "急停信号未松开"),
            ("M5.6", "料筒冷却风机故障"),
            ("M29.1", "共挤A料温过低"),
            ("M29.0", "共挤A料温过高"),
            ("V90.1", "失油报警"),
            ("M20.4", "共挤A调速故障"),
            ("M14.6", "共挤A过电流"),
            ("M7.0", "牵引过电流"),
            ("M7.3", "主机风机故障"),
            ("M6.2", "主机熔压超差"),
            ("M7.4", "减速机定路堵塞"),
            ("V4551.3", "螺杆油箱开关异位，请检查相关设备！"),
            ("V4550.3", "35A共挤冷却风机故障！请确定原因后，排除问题，再合电机保护开关！"),
            ("V4550.1", "35A共挤减速机故障！请根据调速器所显示故障排除问题！"),
            ("V4556.6", "共挤机至少有一段温度超上限！请检查温度偏差设定值和温控回路！"),
            ("V4556.7", "共挤机至少有一段温度超下限！请检查温度偏差设定值和温控回路！"),
            ("V4553.4", "主机冷却风机故障！请确定原因后，排除问题，再合电机保护开关！"),
            ("V4551.3", "80料筒冷却风机报警！请确定原因后，排除问题，再合电机保护开关！"),
            ("V4553.2", "主机至少有一段温度超下限！请检查温度偏差设定值和温控回路！"),
            ("V4551.4", "主电机调速器故障！请根据调速器所显示故障排除问题！"),
            ("V4551.5", "1#热油泵故障！请检查相关回路！"),
            ("V4550.7", "35A共挤电流实测值超出极限设定值！主电机已经保护停止！"),
            ("V4553.1", "1#真空泵故障！请检查相关回路！"),
            ("V4553.2", "80料筒4冷却风机报警！请确定原因后，排除问题，再合电机保护开关！"),
            ("V4550.0", "齿轮箱缺油报警，请检查齿轮箱！！！"),
            ("V4555.0", "喂料变频器故障"),
            ("V4550.2", "主机熔体压力超出极限设定值！主电机已经保护停止！"),
            ("V4553.5", "1#真空泵故障！请检查相关回路！"),
            ("V4550.4", "料筒冷却风机报警！请确定原因后，排除问题，再合电机保护开关！"),
            ("V4551.0", "急停按钮未松开！请确定原因后，重新松开按钮！"),
            ("V4551.1", "主机至少有一段温度超上限！请检查温度偏差设定值和温控回路！"),
            ("V4551.6", "1#热油箱缺油，热油泵已经停止工作！请尽快加油！"),
            ("V4550.6", "80料筒3冷却风机报警！请确定原因后，排除问题，再合电机保护开关！"),
            ("V4551.7", "1#主机电流实测值超出极限设定值！主机已经保护停止！"),
            ("V4550.5", "35B电机调速器故障！请根据调速器显示故障排除问题！"),
            ("V4551.0", "2#主机急停按钮未松开！请确定原因后，重新松开按钮！"),
            ("V4553.4", "2#主机冷却风机故障！请确定原因后，排除问题，再合电机保护开关！"),
            ("V4553.0", "2#真空泵故障！请检查相关回路！"),
            ("V4550.7", "50料筒3冷却风机报警！请确定原因后，排除问题，再合电机保护开关！"),
            ("V4551.7", "2#主机电流实测值超出极限设定值！主电机已经保护停止！"),
            ("V4550.1", "2#齿轮箱缺油报警，请检查齿轮箱！！！"),
            ("V4551.3", "2#螺杆定位开关异位，请检查相关设备！"),
            ("V4550.2", "2#主机熔体压力超出极限设定值！主电机已经保护停止！"),
            ("V4553.1", "2#35B电流实测值超出极限设定值！电机已经保护停止！"),
            ("V4551.1", "2#主机至少有一段温度超上限！请检查温度偏差设定值和温控回路！"),
            ("V4551.4", "2#主电机调速器故障！请根据调速器所显示故障排除问题！"),
            ("V4553.2", "2#主机至少有一段温度超下限！请检查温度偏差设定值和温控回路！"),
            ("V4551.2", "50料筒4冷却风机报警！请确定原因后，排除问题，再合电机保护开关！"),
            ("V4551.6", "2#热油箱缺油，热油泵已经停止工作！请尽快加油！"),
            ("V4550.4", "2#料筒冷却风机报警！请确定原因后，排除问题，再合电机保护开关！"),
            ("V4551.5", "2#热油泵故障！请检查相关回路！"),
        ]
        
        print("\n" + "=" * 80)
        print("PLC 数据读取结果:")
        print("=" * 80)
        print(f"{'功能':<20} {'地址':<10} {'值':<15} {'单位':<10}")
        print("-" * 80)
        
        # 对于 S7-200，V 存储区映射到 DB1
        db_number = 1
        
        for func, address, data_type, unit in data_points:
            if not address:
                print(f"{func:<20} {'-':<10} {'-':<15} {'-':<10}")
                continue
            
            try:
                # 解析地址
                if address.startswith("VW"):
                    start_address = int(address[2:])
                    size = 2  # 2字节
                elif address.startswith("VD"):
                    start_address = int(address[2:])
                    size = 4  # 4字节
                elif address.startswith("C"):
                    # 计数器地址，需要特殊处理
                    print(f"{func:<20} {address:<10} {'-':<15} {'-':<10}")
                    continue
                else:
                    print(f"{func:<20} {address:<10} {'-':<15} {'-':<10}")
                    continue
                
                # 读取数据
                data = client.read_area(snap7.client.S7Area.DB, db_number, start_address, size)
                
                # 解析数据
                if data_type == "Int":
                    value = get_int(data, 0)
                elif data_type == "Real":
                    value = get_real(data, 0)
                else:
                    value = "未知类型"
                
                print(f"{func:<20} {address:<10} {value:<15} {unit:<10}")
                
            except Exception as e:
                print(f"{func:<20} {address:<10} {'错误':<15} {str(e):<10}")
        
        print("=" * 80)
        
        # 读取报警数据
        print("\n" + "=" * 80)
        print("PLC 报警数据读取结果:")
        print("=" * 80)
        print(f"{'地址':<10} {'报警内容':<80} {'状态':<10}")
        print("-" * 80)
        
        for address, alarm_content in alarm_points:
            try:
                # 解析报警地址
                if address.startswith("M"):
                    # M地址格式: M<byte>.<bit>
                    parts = address[1:].split(".")
                    if len(parts) != 2:
                        print(f"{address:<10} {'地址格式错误':<80} {'-':<10}")
                        continue
                    byte_address = int(parts[0])
                    bit_address = int(parts[1])
                    
                    # 读取M区数据
                    data = client.read_area(snap7.client.S7Area.MK, 0, byte_address, 1)  # 1字节
                    value = get_bool(data, 0, bit_address)
                elif address.startswith("V"):
                    # V地址格式: V<address>
                    v_address = int(address[1:])
                    
                    # 对于 S7-200，V 存储区映射到 DB1
                    data = client.read_area(snap7.client.S7Area.DB, 1, v_address, 1)  # 1字节
                    value = get_bool(data, 0, 0)
                else:
                    print(f"{address:<10} {'不支持的地址类型':<80} {'-':<10}")
                    continue
                
                print(f"{address:<10} {alarm_content:<80} {value:<10}")
                
            except Exception as e:
                print(f"{address:<10} {alarm_content:<80} {'错误':<10}")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        # 断开连接
        if client.get_connected():
            client.disconnect()
            print("\n✅ PLC 连接已断开")

def write_s7_plc(address, value, data_type="Int"):
    """向 S7 PLC 写入数据"""
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
            return False
        
        # 解析地址
        if address.startswith("VW"):
            start_address = int(address[2:])
            size = 2  # 2字节
        elif address.startswith("VD"):
            start_address = int(address[2:])
            size = 4  # 4字节
        else:
            print(f"不支持的地址类型: {address}")
            return False
        
        # 对于 S7-200，V 存储区映射到 DB1
        db_number = 1
        
        # 创建数据缓冲区
        data = bytearray(size)
        
        # 根据数据类型写入值
        if data_type == "Int":
            set_int(data, 0, value)
        elif data_type == "Real":
            set_real(data, 0, value)
        elif data_type == "Bool":
            set_bool(data, 0, 0, value)
        else:
            print(f"不支持的数据类型: {data_type}")
            return False
        
        # 写入数据
        client.write_area(snap7.client.S7Area.DB, db_number, start_address, data)
        print(f"✅ 成功写入 {address} = {value} ({data_type})")
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False
    finally:
        # 断开连接
        if client.get_connected():
            client.disconnect()
            print("✅ PLC 连接已断开")

if __name__ == "__main__":
    # 安装依赖: pip install python-snap7
    try:
        import snap7
        # 读取数据
        read_s7_plc()
        
        # 示例：写入数据 - 测试机筒1区 SV
        write_s7_plc("VW102", 144, "Int")  # 写入整数（将机筒1区设定温度改为150°C）
        
    except ImportError:
        print("请先安装 python-snap7 库:")
        print("pip install python-snap7")