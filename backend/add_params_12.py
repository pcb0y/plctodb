import requests
import json

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc3NzQ0MDUyMn0.p3Jxd803vVRnLmYoM08Q7JCjqiA3Wxg_h8ZgkHNvC6U"
BASE_URL = "http://localhost:8000/api/templates/12/parameters"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

params = [
    {"name": "输出电压", "type": "SV", "address": "VD1000", "data_type": "Real", "unit": "V"},
    {"name": "输出电压", "type": "PV", "address": "VD1004", "data_type": "Real", "unit": "V"},
    {"name": "输出电流", "type": "SV", "address": "VD1008", "data_type": "Real", "unit": "A"},
    {"name": "输出电流", "type": "PV", "address": "VD1012", "data_type": "Real", "unit": "A"},
    {"name": "输出频率", "type": "SV", "address": "VD1016", "data_type": "Real", "unit": "Hz"},
    {"name": "输出频率", "type": "PV", "address": "VD1020", "data_type": "Real", "unit": "Hz"},
    {"name": "输出功率", "type": "SV", "address": "VD1024", "data_type": "Real", "unit": "kW"},
    {"name": "输出功率", "type": "PV", "address": "VD1028", "data_type": "Real", "unit": "kW"},
    {"name": "直流母线电压", "type": "PV", "address": "VD1032", "data_type": "Real", "unit": "V"},
    {"name": "散热器温度", "type": "PV", "address": "VD1036", "data_type": "Real", "unit": "°C"},
    {"name": "IGBT温度", "type": "PV", "address": "VD1040", "data_type": "Real", "unit": "°C"},
    {"name": "输入电压", "type": "PV", "address": "VD1044", "data_type": "Real", "unit": "V"},
    {"name": "运行模式", "type": "SV", "address": "VW1048", "data_type": "Int", "unit": ""},
    {"name": "运行模式", "type": "PV", "address": "VW1050", "data_type": "Int", "unit": ""},
    {"name": "启动指令", "type": "SV", "address": "V1052.0", "data_type": "Bool", "unit": ""},
    {"name": "停止指令", "type": "SV", "address": "V1052.1", "data_type": "Bool", "unit": ""},
    {"name": "故障复位", "type": "SV", "address": "V1052.2", "data_type": "Bool", "unit": ""},
    {"name": "运行状态", "type": "PV", "address": "V1053.0", "data_type": "Bool", "unit": ""},
    {"name": "故障状态", "type": "PV", "address": "V1053.1", "data_type": "Bool", "unit": ""},
    {"name": "报警状态", "type": "PV", "address": "V1053.2", "data_type": "Bool", "unit": ""},
    {"name": "过压保护", "type": "PV", "address": "V1053.3", "data_type": "Bool", "unit": ""},
    {"name": "欠压保护", "type": "PV", "address": "V1053.4", "data_type": "Bool", "unit": ""},
    {"name": "过流保护", "type": "PV", "address": "V1053.5", "data_type": "Bool", "unit": ""},
    {"name": "过载保护", "type": "PV", "address": "V1053.6", "data_type": "Bool", "unit": ""},
    {"name": "过热保护", "type": "PV", "address": "V1053.7", "data_type": "Bool", "unit": ""},
    {"name": "电流上限", "type": "SV", "address": "VD1056", "data_type": "Real", "unit": "A"},
    {"name": "电压上限", "type": "SV", "address": "VD1060", "data_type": "Real", "unit": "V"},
    {"name": "频率上限", "type": "SV", "address": "VD1064", "data_type": "Real", "unit": "Hz"},
    {"name": "功率上限", "type": "SV", "address": "VD1068", "data_type": "Real", "unit": "kW"},
    {"name": "PID比例", "type": "SV", "address": "VD1072", "data_type": "Real", "unit": ""},
    {"name": "PID积分", "type": "SV", "address": "VD1076", "data_type": "Real", "unit": "s"},
    {"name": "PID微分", "type": "SV", "address": "VD1080", "data_type": "Real", "unit": "s"},
    {"name": "加速时间", "type": "SV", "address": "VD1084", "data_type": "Real", "unit": "s"},
    {"name": "减速时间", "type": "SV", "address": "VD1088", "data_type": "Real", "unit": "s"},
    {"name": "脉冲频率", "type": "SV", "address": "VD1092", "data_type": "Real", "unit": "Hz"},
    {"name": "脉冲宽度", "type": "SV", "address": "VD1096", "data_type": "Real", "unit": "%"},
]

count = 0
for p in params:
    suffix = "设定值" if p["type"] == "SV" else "实际值"
    is_readonly = p["type"] == "PV"
    
    payload = {
        "parameter_name": f"{p['name']}{suffix}",
        "parameter_address": p["address"],
        "parameter_value": "",
        "parameter_unit": p["unit"],
        "parameter_type": p["data_type"],
        "is_readonly": is_readonly
    }
    
    response = requests.post(BASE_URL, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        count += 1
        print(f"添加成功: {p['name']}{suffix}")
    else:
        print(f"添加失败: {p['name']}{suffix} - {response.text}")

print(f"\n共添加 {count} 个参数")