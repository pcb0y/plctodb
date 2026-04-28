import requests

API_BASE = "http://localhost:8000/api"

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwiYWNjZXNzX3Rva2VuIjpudWxsLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NzczNTI0Njh9.DhS3zrJ3K3V2rXz3K3V2rXz3K3V2rXz3K3V2rXz3K"
}

response = requests.get(f"{API_BASE}/process-parameters/template/1", headers=headers)
print(f"状态码: {response.status_code}")
data = response.json()
print(f"返回数据: {data}")

if "template" in data:
    print(f"\n模板参数数量: {len(data['template'])}")
    if len(data["template"]) > 0:
        print("\n第一个参数的所有字段:")
        for key, value in data["template"][0].items():
            print(f"  {key}: {value}")