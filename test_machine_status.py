#!/usr/bin/env python3
"""
测试机台状态
"""

import json
import http.client

# 登录获取token
print("=== 测试机台状态 ===")

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

# 获取机台列表
print("\n2. 获取机台列表...")
conn.request('GET', '/api/machines', headers={'Authorization': 'Bearer ' + token})
response = conn.getresponse()
print(f"响应状态码: {response.status}")
print(f"响应状态: {response.reason}")

data = response.read()
machines = json.loads(data)

print("\n3. 机台状态:")
for machine in machines:
    print(f"{machine['machine_name']}: {machine['status']}")
    print(f"  IP地址: {machine['ip_address']}")
    print(f"  Rack: {machine['rack']}")
    print(f"  Slot: {machine['slot']}")

conn.close()
print("\n=== 测试完成 ===")