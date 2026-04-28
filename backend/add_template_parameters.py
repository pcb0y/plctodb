import pymysql

conn = pymysql.connect(
    host='192.168.15.26',
    port=3307,
    user='root',
    password='F3jD8gH2mB6',
    database='plc_process_db'
)
cursor = conn.cursor()

parameters = [
    {"name": "外层模具石", "type": "SV", "address": "VW344", "data_type": "Int", "unit": "℃"},
    {"name": "外层模具石", "type": "PV", "address": "VW344", "data_type": "Int", "unit": "℃"},
    {"name": "A组合流芯", "type": "SV", "address": "VW346", "data_type": "Int", "unit": "℃"},
    {"name": "A组合流芯", "type": "PV", "address": "VW346", "data_type": "Int", "unit": "℃"},
    {"name": "A组转接模", "type": "SV", "address": "VW348", "data_type": "Int", "unit": "℃"},
    {"name": "A组转接模", "type": "PV", "address": "VW348", "data_type": "Int", "unit": "℃"},
    {"name": "A组连接管", "type": "SV", "address": "VW350", "data_type": "Int", "unit": "℃"},
    {"name": "A组连接管", "type": "PV", "address": "VW350", "data_type": "Int", "unit": "℃"},
    {"name": "B组合流芯", "type": "SV", "address": "VW352", "data_type": "Int", "unit": "℃"},
    {"name": "B组合流芯", "type": "PV", "address": "VW352", "data_type": "Int", "unit": "℃"},
    {"name": "B组转接模", "type": "SV", "address": "VW362", "data_type": "Int", "unit": "℃"},
    {"name": "B组转接模", "type": "PV", "address": "VW362", "data_type": "Int", "unit": "℃"},
    {"name": "B组连接管", "type": "SV", "address": "VW364", "data_type": "Int", "unit": "℃"},
    {"name": "B组连接管", "type": "PV", "address": "VW364", "data_type": "Int", "unit": "℃"},
    {"name": "35A转速", "type": "SV", "address": "VD508", "data_type": "Real", "unit": "RPM"},
    {"name": "35A转速", "type": "PV", "address": "VD532", "data_type": "Real", "unit": "RPM"},
    {"name": "35A电流", "type": "SV", "address": "VD2300", "data_type": "Real", "unit": "%"},
    {"name": "35A电流", "type": "PV", "address": "VD556", "data_type": "Real", "unit": "A"},
    {"name": "35B转速", "type": "SV", "address": "VD212", "data_type": "Real", "unit": "RPM"},
    {"name": "35B转速", "type": "PV", "address": "VD236", "data_type": "Real", "unit": "RPM"},
    {"name": "35B电流", "type": "SV", "address": "VD3308", "data_type": "Real", "unit": "%"},
    {"name": "35B电流", "type": "PV", "address": "VD264", "data_type": "Real", "unit": "A"},
    {"name": "A组35机1区", "type": "SV", "address": "VW116", "data_type": "Int", "unit": "℃"},
    {"name": "A组35机1区", "type": "PV", "address": "VW118", "data_type": "Int", "unit": "℃"},
    {"name": "A组35机2区", "type": "SV", "address": "VW316", "data_type": "Int", "unit": "℃"},
    {"name": "A组35机2区", "type": "PV", "address": "VW318", "data_type": "Int", "unit": "℃"},
    {"name": "A组35机3区", "type": "SV", "address": "VW368", "data_type": "Int", "unit": "℃"},
    {"name": "A组35机3区", "type": "PV", "address": "VW370", "data_type": "Int", "unit": "℃"},
    {"name": "B组35机1区", "type": "SV", "address": "VW118", "data_type": "Int", "unit": "℃"},
    {"name": "B组35机1区", "type": "PV", "address": "VW370", "data_type": "Int", "unit": "℃"},
    {"name": "B组35机2区", "type": "SV", "address": "VW120", "data_type": "Int", "unit": "℃"},
    {"name": "B组35机2区", "type": "PV", "address": "VW322", "data_type": "Int", "unit": "℃"},
    {"name": "B组35机3区", "type": "SV", "address": "VW112", "data_type": "Int", "unit": "℃"},
    {"name": "B组35机3区", "type": "PV", "address": "VW312", "data_type": "Int", "unit": "℃"},
    {"name": "A组备用1", "type": "SV", "address": "VW160", "data_type": "Int", "unit": "℃"},
    {"name": "A组备用1", "type": "PV", "address": "VW312", "data_type": "Int", "unit": "℃"},
    {"name": "A组备用2", "type": "SV", "address": "VW166", "data_type": "Int", "unit": "℃"},
    {"name": "A组备用2", "type": "PV", "address": "VW366", "data_type": "Int", "unit": "℃"},
    {"name": "B组备用1", "type": "SV", "address": "VW156", "data_type": "Int", "unit": "℃"},
    {"name": "B组备用1", "type": "PV", "address": "VW356", "data_type": "Int", "unit": "℃"},
    {"name": "B组备用2", "type": "SV", "address": "VW158", "data_type": "Int", "unit": "℃"},
    {"name": "B组备用2", "type": "PV", "address": "VW358", "data_type": "Int", "unit": "℃"},
]

template_id = 11
success_count = 0
fail_count = 0

try:
    for param in parameters:
        suffix = "设定值" if param["type"] == "SV" else "实际值"
        is_readonly = 1 if param["type"] == "PV" else 0
        
        sql = """
            INSERT INTO template_parameters 
            (template_id, parameter_name, parameter_address, parameter_value, parameter_unit, parameter_type, is_readonly)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            cursor.execute(sql, (
                template_id,
                f"{param['name']}{suffix}",
                param["address"],
                "",
                param["unit"],
                param["data_type"],
                is_readonly
            ))
            print(f"成功添加: {param['name']}{suffix}")
            success_count += 1
        except Exception as e:
            print(f"失败添加: {param['name']}{suffix} - {str(e)}")
            fail_count += 1
    
    conn.commit()
    print(f"\n批量添加完成！成功: {success_count}, 失败: {fail_count}")
except Exception as e:
    print(f"批量操作失败: {str(e)}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()