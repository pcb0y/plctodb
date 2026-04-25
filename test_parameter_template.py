#!/usr/bin/env python3
"""
测试获取工艺参数模板
"""

import json
import http.client

# 登录获取token
print("=== 测试获取工艺参数模板 ===")

conn = http.client.HTTPConnection('localhost', 8000)

# 登录
login_data = {
    "username": "admin",
    "password": "admin"
}

print("1. 登录获取token...")
conn.request('POST', '/api/auth/login', json.dumps(login_data), {'Content-Type': 'application/json'})
response = conn.getresponse()
data = response.read()
login_result = json.loads(data)
token = login_result['access_token']
print("✅ 登录成功，获取到token")

# 获取工艺参数模板
print("\n2. 获取工艺参数模板...")
conn.request('GET', '/api/process-parameters/template', headers={'Authorization': 'Bearer ' + token})
response = conn.getresponse()
print(f"响应状态码: {response.status}")
print(f"响应状态: {response.reason}")

data = response.read()
template = json.loads(data)

print("\n3. 模板参数:")
template_params = template.get('template', [])
print(f"模板参数数量: {len(template_params)}")

# 显示前5个参数
for i, param in enumerate(template_params[:5]):
    print(f"  {i+1}. {param['parameter_name']}: {param['parameter_address']} (类型: {param['parameter_type']})")

if len(template_params) > 5:
    print(f"  ... 还有 {len(template_params) - 5} 个参数")

conn.close()
print("\n=== 测试完成 ===")