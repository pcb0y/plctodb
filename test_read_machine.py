#!/usr/bin/env python3
"""
测试读取机台工艺参数的API
"""

import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

import requests

# 获取token
print("=== 测试读取机台工艺参数 ===")

# 登录获取token
login_data = {
    "username": "admin",
    "password": "admin"
}

print("1. 登录获取token...")
try:
    login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
    login_response.raise_for_status()
    login_result = login_response.json()
    token = login_result['access_token']
    print("✅ 登录成功，获取到token")
except Exception as e:
    print(f"❌ 登录失败: {e}")
    sys.exit(1)

# 测试读取默认挤出机的工艺参数
print("\n2. 测试读取默认挤出机的工艺参数...")
headers = {
    'Authorization': f'Bearer {token}'
}

try:
    response = requests.get('http://localhost:8000/api/machines/1/read', headers=headers)
    print(f"响应状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 读取成功，获取到 {len(data.get('parameters', {}))} 个工艺参数")
        # 显示前5个参数
        params = data.get('parameters', {})
        for i, (name, info) in enumerate(list(params.items())[:5]):
            print(f"  {i+1}. {name}: {info['value']} {info['unit']} (地址: {info['address']})")
        if len(params) > 5:
            print(f"  ... 还有 {len(params) - 5} 个参数")
    else:
        error = response.json()
        print(f"❌ 读取失败: {error.get('detail')}")
except Exception as e:
    print(f"❌ 读取失败: {e}")

print("\n=== 测试完成 ===")