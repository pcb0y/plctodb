#!/bin/bash

cd "$(dirname "$0")"

echo "正在安装后端依赖..."
uv pip install -r requirements.txt

echo "正在创建数据库..."
mysql -h 192.168.15.26 -u root -pwdmzjzzm1 -e "CREATE DATABASE IF NOT EXISTS plc_process_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

echo "正在启动后端服务..."
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "后端服务已启动 (PID: $BACKEND_PID)"
echo "前端页面: http://localhost:8000/frontend/index.html"
echo "API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"

trap "kill $BACKEND_PID 2>/dev/null; exit" INT TERM
wait $BACKEND_PID
