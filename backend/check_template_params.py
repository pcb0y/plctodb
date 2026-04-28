import requests

API_BASE = "http://localhost:8000/api"

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwiYWNjZXNzX3Rva2VuIjpudWxsLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NzczNTI0Njh9.DhS3zrJ3K3V2rXz3K3V2rXz3K3V2rXz3K3V2rXz3K"
}

response = requests.get(f"{API_BASE}/process-parameters/template/1", headers=headers)
data = response.json()

if data.get("template"):
    print("后端返回的参数示例（前5个）：")
    for i, param in enumerate(data["template"][:5]):
        print(f"\n参数 {i+1}:")
        for key, value in param.items():
            print(f"  {key}: {value}")
else:
    print("没有返回模板数据")