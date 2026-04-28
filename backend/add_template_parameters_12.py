import requests

API_BASE = "http://localhost:8000/api"

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwiYXBpX3Rva2VuIjoiYjY1ZjUyY2JiYWYzNDQ5NzlmYTlhMDI4NjQyYzZkZjAiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3MzAwMDAwMDB9.5Y0T9y8uF1KjY2H6y6w0q5Y0T9y8uF1KjY2H6y6w0q5"
}

parameters = [
    {"name": "保温时长", "type": "SV", "address": "C3", "data_type": "Int", "unit": "s"},
    {"name": "主机料温过高", "type": "PV", "address": "V4551.0", "data_type": "Bool", "unit": ""},
    {"name": "主机料温过低", "type": "PV", "address": "V4551.1", "data_type": "Bool", "unit": ""},
    {"name": "主机调速故障", "type": "PV", "address": "V4551.4", "data_type": "Bool", "unit": ""},
    {"name": "主机料筒冷却风机故障", "type": "PV", "address": "V4550.7", "data_type": "Bool", "unit": ""},
    {"name": "喂料料筒冷却风机故障", "type": "PV", "address": "V4551.5", "data_type": "Bool", "unit": ""},
    {"name": "喂料调速器故障", "type": "PV", "address": "V4550.2", "data_type": "Bool", "unit": ""},
    {"name": "喂料过电流", "type": "PV", "address": "V4551.5", "data_type": "Bool", "unit": ""},
    {"name": "螺杆异位报警", "type": "PV", "address": "V4553.1", "data_type": "Bool", "unit": ""},
    {"name": "主机急停未松开", "type": "PV", "address": "V4553.0", "data_type": "Bool", "unit": ""},
    {"name": "65主机风机故障", "type": "PV", "address": "V4551.2", "data_type": "Bool", "unit": ""},
    {"name": "65主机风机故障", "type": "PV", "address": "V4553.5", "data_type": "Bool", "unit": ""},
    {"name": "65真空泵故障", "type": "PV", "address": "V4553.6", "data_type": "Bool", "unit": ""},
    {"name": "35共挤A调速故障", "type": "PV", "address": "V4551.6", "data_type": "Bool", "unit": ""},
    {"name": "35共挤A过电流", "type": "PV", "address": "V4553.1", "data_type": "Bool", "unit": ""},
    {"name": "35共挤A料筒冷却风机故障", "type": "PV", "address": "V4550.5", "data_type": "Bool", "unit": ""},
    {"name": "35共挤B调速故障", "type": "PV", "address": "V4550.3", "data_type": "Bool", "unit": ""},
    {"name": "35共挤B调速故障", "type": "PV", "address": "V4551.7", "data_type": "Bool", "unit": ""},
    {"name": "35共挤B过电流", "type": "PV", "address": "V4553.2", "data_type": "Bool", "unit": ""},
    {"name": "35共挤B料筒冷却风机故障", "type": "PV", "address": "V4550.4", "data_type": "Bool", "unit": ""},
    {"name": "主机转速", "type": "SV", "address": "VD224", "data_type": "Real", "unit": "RPM"},
    {"name": "主机转速", "type": "PV", "address": "VD200", "data_type": "Real", "unit": "RPM"},
    {"name": "主机电流", "type": "SV", "address": "VD232", "data_type": "Real", "unit": "%"},
    {"name": "主机电流", "type": "PV", "address": "VD228", "data_type": "Real", "unit": "A"},
    {"name": "喂料转速", "type": "SV", "address": "VD204", "data_type": "Real", "unit": "RPM"},
    {"name": "喂料转速", "type": "PV", "address": "VD228", "data_type": "Real", "unit": "RPM"},
    {"name": "喂料电流", "type": "SV", "address": "VD244", "data_type": "Real", "unit": "%"},
    {"name": "喂料电流", "type": "PV", "address": "VD240", "data_type": "Real", "unit": "A"},
    {"name": "65机筒1区", "type": "SV", "address": "VW102", "data_type": "Int", "unit": "℃"},
    {"name": "65机筒1区", "type": "PV", "address": "VW302", "data_type": "Int", "unit": "℃"},
    {"name": "65机筒2区", "type": "SV", "address": "VW104", "data_type": "Int", "unit": "℃"},
    {"name": "65机筒2区", "type": "PV", "address": "VW304", "data_type": "Int", "unit": "℃"},
    {"name": "65机筒3区", "type": "SV", "address": "VW106", "data_type": "Int", "unit": "℃"},
    {"name": "65机筒3区", "type": "PV", "address": "VW306", "data_type": "Int", "unit": "℃"},
    {"name": "65机筒4区", "type": "SV", "address": "VW108", "data_type": "Int", "unit": "℃"},
    {"name": "65机筒4区", "type": "PV", "address": "VW308", "data_type": "Int", "unit": "℃"},
    {"name": "65机合流芯", "type": "SV", "address": "VW180", "data_type": "Int", "unit": "℃"},
    {"name": "65机合流芯", "type": "PV", "address": "VW380", "data_type": "Int", "unit": "℃"},
    {"name": "芯层模具上", "type": "SV", "address": "VW140", "data_type": "Int", "unit": "℃"},
    {"name": "芯层模具上", "type": "PV", "address": "VW340", "data_type": "Int", "unit": "℃"},
    {"name": "芯层模具下", "type": "SV", "address": "VW142", "data_type": "Int", "unit": "℃"},
    {"name": "芯层模具下", "type": "PV", "address": "VW342", "data_type": "Int", "unit": "℃"},
    {"name": "芯层模具左", "type": "SV", "address": "VW144", "data_type": "Int", "unit": "℃"},
    {"name": "芯层模具左", "type": "PV", "address": "VW344", "data_type": "Int", "unit": "℃"},
    {"name": "芯层模具右", "type": "SV", "address": "VW146", "data_type": "Int", "unit": "℃"},
    {"name": "芯层模具右", "type": "PV", "address": "VW346", "data_type": "Int", "unit": "℃"},
    {"name": "外层模具上", "type": "SV", "address": "VW148", "data_type": "Int", "unit": "℃"},
    {"name": "外层模具上", "type": "PV", "address": "VW348", "data_type": "Int", "unit": "℃"},
    {"name": "外层模具下", "type": "SV", "address": "VW150", "data_type": "Int", "unit": "℃"},
    {"name": "外层模具下", "type": "PV", "address": "VW350", "data_type": "Int", "unit": "℃"},
    {"name": "外层模具左", "type": "SV", "address": "VW152", "data_type": "Int", "unit": "℃"},
    {"name": "外层模具左", "type": "PV", "address": "VW352", "data_type": "Int", "unit": "℃"},
    {"name": "外层模具右", "type": "SV", "address": "VW154", "data_type": "Int", "unit": "℃"},
    {"name": "外层模具右", "type": "PV", "address": "VW354", "data_type": "Int", "unit": "℃"},
    {"name": "A组合流芯", "type": "SV", "address": "VW156", "data_type": "Int", "unit": "℃"},
    {"name": "A组合流芯", "type": "PV", "address": "VW356", "data_type": "Int", "unit": "℃"},
    {"name": "A组转接模", "type": "SV", "address": "VW158", "data_type": "Int", "unit": "℃"},
    {"name": "A组转接模", "type": "PV", "address": "VW358", "data_type": "Int", "unit": "℃"},
    {"name": "A组连接管", "type": "SV", "address": "VW160", "data_type": "Int", "unit": "℃"},
    {"name": "A组连接管", "type": "PV", "address": "VW360", "data_type": "Int", "unit": "℃"},
    {"name": "B组合流芯", "type": "SV", "address": "VW162", "data_type": "Int", "unit": "℃"},
    {"name": "B组合流芯", "type": "PV", "address": "VW362", "data_type": "Int", "unit": "℃"},
    {"name": "B组转接模", "type": "SV", "address": "VW164", "data_type": "Int", "unit": "℃"},
    {"name": "B组转接模", "type": "PV", "address": "VW364", "data_type": "Int", "unit": "℃"},
    {"name": "B组连接管", "type": "SV", "address": "VW166", "data_type": "Int", "unit": "℃"},
    {"name": "B组连接管", "type": "PV", "address": "VW366", "data_type": "Int", "unit": "℃"},
    {"name": "备用1", "type": "SV", "address": "VW168", "data_type": "Int", "unit": "℃"},
    {"name": "备用1", "type": "PV", "address": "VW368", "data_type": "Int", "unit": "℃"},
    {"name": "备用2", "type": "SV", "address": "VW170", "data_type": "Int", "unit": "℃"},
    {"name": "备用2", "type": "PV", "address": "VW370", "data_type": "Int", "unit": "℃"},
    {"name": "35A转速", "type": "SV", "address": "VD208", "data_type": "Real", "unit": "RPM"},
    {"name": "35A转速", "type": "PV", "address": "VD248", "data_type": "Real", "unit": "RPM"},
    {"name": "35A电流", "type": "SV", "address": "VD256", "data_type": "Real", "unit": "%"},
    {"name": "35A电流", "type": "PV", "address": "VD252", "data_type": "Real", "unit": "A"},
    {"name": "35B转速", "type": "SV", "address": "VD212", "data_type": "Real", "unit": "RPM"},
    {"name": "35B转速", "type": "PV", "address": "VD260", "data_type": "Real", "unit": "RPM"},
    {"name": "35B电流", "type": "SV", "address": "VD268", "data_type": "Real", "unit": "%"},
    {"name": "35B电流", "type": "PV", "address": "VD264", "data_type": "Real", "unit": "A"},
    {"name": "A组35机1区", "type": "SV", "address": "VW112", "data_type": "Int", "unit": "℃"},
    {"name": "A组35机1区", "type": "PV", "address": "VW312", "data_type": "Int", "unit": "℃"},
    {"name": "A组35机2区", "type": "SV", "address": "VW114", "data_type": "Int", "unit": "℃"},
    {"name": "A组35机2区", "type": "PV", "address": "VW314", "data_type": "Int", "unit": "℃"},
    {"name": "A组35机3区", "type": "SV", "address": "VW116", "data_type": "Int", "unit": "℃"},
    {"name": "A组35机3区", "type": "PV", "address": "VW316", "data_type": "Int", "unit": "℃"},
    {"name": "B组35机1区", "type": "SV", "address": "VW118", "data_type": "Int", "unit": "℃"},
    {"name": "B组35机1区", "type": "PV", "address": "VW318", "data_type": "Int", "unit": "℃"},
    {"name": "B组35机2区", "type": "SV", "address": "VW120", "data_type": "Int", "unit": "℃"},
    {"name": "B组35机2区", "type": "PV", "address": "VW320", "data_type": "Int", "unit": "℃"},
    {"name": "B组35机3区", "type": "SV", "address": "VW122", "data_type": "Int", "unit": "℃"},
    {"name": "B组35机3区", "type": "PV", "address": "VW322", "data_type": "Int", "unit": "℃"},
    {"name": "25共挤A调速故障", "type": "PV", "address": "V4550.0", "data_type": "Bool", "unit": ""},
    {"name": "25共挤A过电流", "type": "PV", "address": "V4553.1", "data_type": "Bool", "unit": ""},
    {"name": "25共挤A料筒冷却风机故障", "type": "PV", "address": "V4550.5", "data_type": "Bool", "unit": ""},
    {"name": "25共挤B调速故障", "type": "PV", "address": "V4551.1", "data_type": "Bool", "unit": ""},
    {"name": "25共挤B过电流", "type": "PV", "address": "V4553.4", "data_type": "Bool", "unit": ""},
    {"name": "25共挤B料筒冷却风机故障", "type": "PV", "address": "V4550.6", "data_type": "Bool", "unit": ""},
    {"name": "25A转速", "type": "SV", "address": "VD216", "data_type": "Real", "unit": "RPM"},
    {"name": "25A转速", "type": "PV", "address": "VD272", "data_type": "Real", "unit": "RPM"},
    {"name": "25A电流", "type": "SV", "address": "VD2300", "data_type": "Real", "unit": "%"},
    {"name": "25A电流", "type": "PV", "address": "VD556", "data_type": "Real", "unit": "A"},
    {"name": "25B转速", "type": "SV", "address": "VD220", "data_type": "Real", "unit": "RPM"},
    {"name": "25B转速", "type": "PV", "address": "VD284", "data_type": "Real", "unit": "RPM"},
    {"name": "25B电流", "type": "SV", "address": "VD292", "data_type": "Real", "unit": "%"},
    {"name": "25B电流", "type": "PV", "address": "VD288", "data_type": "Real", "unit": "A"},
    {"name": "A组25机1区", "type": "SV", "address": "VW124", "data_type": "Int", "unit": "℃"},
    {"name": "A组25机1区", "type": "PV", "address": "VW324", "data_type": "Int", "unit": "℃"},
    {"name": "A组25机2区", "type": "SV", "address": "VW126", "data_type": "Int", "unit": "℃"},
    {"name": "A组25机2区", "type": "PV", "address": "VW326", "data_type": "Int", "unit": "℃"},
    {"name": "B组25机1区", "type": "SV", "address": "VW130", "data_type": "Int", "unit": "℃"},
    {"name": "B组25机1区", "type": "PV", "address": "VW330", "data_type": "Int", "unit": "℃"},
    {"name": "B组25机2区", "type": "SV", "address": "VW132", "data_type": "Int", "unit": "℃"},
    {"name": "B组25机2区", "type": "PV", "address": "VW332", "data_type": "Int", "unit": "℃"},
]

template_id = 12
success_count = 0
fail_count = 0

for param in parameters:
    suffix = "设定值" if param["type"] == "SV" else "实际值"
    is_readonly = True if param["type"] == "PV" else False
    
    data = {
        "parameter_name": f"{param['name']}{suffix}",
        "parameter_address": param["address"],
        "parameter_value": "",
        "parameter_unit": param["unit"],
        "parameter_type": param["data_type"],
        "is_readonly": is_readonly
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/templates/{template_id}/parameters",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            print(f"成功添加: {param['name']}{suffix}")
            success_count += 1
        else:
            print(f"失败添加: {param['name']}{suffix} - {response.text}")
            fail_count += 1
    except Exception as e:
        print(f"失败添加: {param['name']}{suffix} - {str(e)}")
        fail_count += 1

print(f"\n批量添加完成！成功: {success_count}, 失败: {fail_count}")