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
    {"name": "25B调速故障", "type": "SV", "address": "V4550.1", "data_type": "Bool", "unit": ""},
    {"name": "25B调速故障", "type": "PV", "address": "V4550.7", "data_type": "Bool", "unit": ""},
    {"name": "25B料筒冷却风机故障", "type": "SV", "address": "V4550.4", "data_type": "Bool", "unit": ""},
    {"name": "25A调速故障", "type": "SV", "address": "V4551.4", "data_type": "Bool", "unit": ""},
    {"name": "25A料筒冷却风机故障", "type": "SV", "address": "V4551.4", "data_type": "Bool", "unit": ""},
    {"name": "25A调速故障", "type": "PV", "address": "V4551.4", "data_type": "Bool", "unit": ""},
    {"name": "25A过电流", "type": "SV", "address": "V4551.7", "data_type": "Bool", "unit": ""},
    {"name": "25A料筒冷却风机故障", "type": "PV", "address": "V4550.6", "data_type": "Bool", "unit": ""},
    {"name": "25B转速", "type": "SV", "address": "VD212", "data_type": "Real", "unit": "RPM"},
    {"name": "25B转速", "type": "PV", "address": "VD532", "data_type": "Real", "unit": "RPM"},
    {"name": "25B电流", "type": "SV", "address": "VD2300", "data_type": "Real", "unit": "%"},
    {"name": "25B电流", "type": "PV", "address": "VD556", "data_type": "Real", "unit": "A"},
    {"name": "25A转速", "type": "SV", "address": "VD208", "data_type": "Real", "unit": "RPM"},
    {"name": "25A转速", "type": "PV", "address": "VD232", "data_type": "Real", "unit": "RPM"},
    {"name": "25A电流", "type": "SV", "address": "VD3300", "data_type": "Real", "unit": "%"},
    {"name": "25A电流", "type": "PV", "address": "VD256", "data_type": "Real", "unit": "A"},
    {"name": "B组25机1区", "type": "SV", "address": "VW102", "data_type": "Int", "unit": "℃"},
    {"name": "B组25机1区", "type": "PV", "address": "VW104", "data_type": "Int", "unit": "℃"},
    {"name": "B组25机2区", "type": "SV", "address": "VW104", "data_type": "Int", "unit": "℃"},
    {"name": "B组25机2区", "type": "PV", "address": "VW304", "data_type": "Int", "unit": "℃"},
    {"name": "B组25机3区", "type": "SV", "address": "VW106", "data_type": "Int", "unit": "℃"},
    {"name": "B组25机3区", "type": "PV", "address": "VW306", "data_type": "Int", "unit": "℃"},
    {"name": "A组25机1区", "type": "SV", "address": "VW108", "data_type": "Int", "unit": "℃"},
    {"name": "A组25机1区", "type": "PV", "address": "VW308", "data_type": "Int", "unit": "℃"},
    {"name": "A组25机2区", "type": "SV", "address": "VW116", "data_type": "Int", "unit": "℃"},
    {"name": "A组25机2区", "type": "PV", "address": "VW316", "data_type": "Int", "unit": "℃"},
    {"name": "A组25机3区", "type": "SV", "address": "VW118", "data_type": "Int", "unit": "℃"},
    {"name": "A组25机3区", "type": "PV", "address": "VW318", "data_type": "Int", "unit": "℃"},
    {"name": "A组25机3区", "type": "SV", "address": "VW1130", "data_type": "Int", "unit": "℃"},
    {"name": "A组25机3区", "type": "PV", "address": "VW3130", "data_type": "Int", "unit": "℃"},
    {"name": "25B共挤备用1", "type": "SV", "address": "VW130", "data_type": "Int", "unit": "℃"},
    {"name": "25B共挤备用1", "type": "PV", "address": "VW330", "data_type": "Int", "unit": "℃"},
    {"name": "25B共挤备用2", "type": "SV", "address": "VW132", "data_type": "Int", "unit": "℃"},
    {"name": "25B共挤备用2", "type": "PV", "address": "VW332", "data_type": "Int", "unit": "℃"},
    {"name": "25A共挤备用1", "type": "SV", "address": "VW134", "data_type": "Int", "unit": "℃"},
    {"name": "25A共挤备用1", "type": "PV", "address": "VW334", "data_type": "Int", "unit": "℃"},
    {"name": "25A共挤备用2", "type": "SV", "address": "VW136", "data_type": "Int", "unit": "℃"},
    {"name": "25A共挤备用2", "type": "PV", "address": "VW336", "data_type": "Int", "unit": "℃"},
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