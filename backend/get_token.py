import requests

API_BASE = "http://localhost:8000/api"

response = requests.post(f"{API_BASE}/auth/login", json={
    "username": "admin",
    "password": "Windows,.1"
})

if response.status_code == 200:
    data = response.json()
    token = data.get("access_token")
    print(f"登录成功！Token: {token[:50]}...")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    param_response = requests.get(f"{API_BASE}/process-parameters/template/1", headers=headers)
    print(f"\n状态码: {param_response.status_code}")

    if param_response.status_code == 200:
        param_data = param_response.json()
        print(f"返回数据包含: {list(param_data.keys())}")

        if "template" in param_data:
            print(f"\n模板参数数量: {len(param_data['template'])}")
            if len(param_data["template"]) > 0:
                print("\n前3个参数的is_readonly值:")
                for i, param in enumerate(param_data["template"][:3]):
                    print(f"  参数{i+1}: {param.get('parameter_name')}, is_readonly: {param.get('is_readonly')}")
    else:
        print(f"错误: {param_response.text}")
else:
    print(f"登录失败: {response.text}")