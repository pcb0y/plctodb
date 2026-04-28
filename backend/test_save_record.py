import requests

API_BASE = "http://localhost:8000/api"

response = requests.post(f"{API_BASE}/auth/login", json={
    "username": "admin",
    "password": "Windows,.1"
})

if response.status_code == 200:
    data = response.json()
    token = data.get("access_token")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    param_response = requests.get(f"{API_BASE}/process-parameters/template/1", headers=headers)
    param_data = param_response.json()

    if "template" in param_data:
        template_params = param_data["template"]

        snapshot = {}
        for param in template_params[:5]:
            snapshot[param["parameter_name"]] = {
                "address": param["parameter_address"],
                "value": param["parameter_value"],
                "unit": param["parameter_unit"],
                "type": param["parameter_type"],
                "readonly": param.get("is_readonly", False)
            }

        print("发送的snapshot数据示例:")
        for name, info in list(snapshot.items())[:3]:
            print(f"  {name}: readonly={info['readonly']}")

        save_data = {
            "machine_id": 1,
            "product_id": 1,
            "operator_id": 1,
            "parameters_snapshot": snapshot,
            "notes": "测试保存"
        }

        save_response = requests.post(f"{API_BASE}/process-records", headers=headers, json=save_data)
        print(f"\n保存响应状态: {save_response.status_code}")
        if save_response.status_code == 200:
            print("保存成功!")
            record_id = save_response.json().get("id")
            print(f"记录ID: {record_id}")

            check_response = requests.get(f"{API_BASE}/process-records/{record_id}", headers=headers)
            if check_response.status_code == 200:
                record = check_response.json()
                print(f"\n记录的参数值示例:")
                for pv in record.get("parameter_values", [])[:3]:
                    print(f"  {pv['parameter_name']}: is_readonly={pv.get('is_readonly')}")
        else:
            print(f"保存失败: {save_response.text}")
else:
    print(f"登录失败: {response.text}")