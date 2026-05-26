#!/bin/bash

# 构建镜像脚本
echo "=== 构建Docker镜像 ==="

# 构建arm64本地镜像
echo "1. 构建本地镜像..."
docker build -t plctodb:local .

# 登录阿里云容器镜像服务
echo ""
echo "2. 登录阿里云容器镜像服务..."
echo "请输入阿里云容器镜像服务用户名（通常是阿里云账号全称）："
read ALIYUN_USERNAME
echo "请输入阿里云容器镜像服务密码（需要在阿里云控制台创建访问凭证）："
read -s ALIYUN_PASSWORD

echo "$ALIYUN_PASSWORD" | docker login --username="$ALIYUN_USERNAME" registry.cn-hangzhou.aliyuncs.com

# 构建并推送linux/amd64镜像到阿里云
echo ""
echo "3. 构建并推送linux/amd64镜像到阿里云..."
docker buildx build --platform linux/amd64 -t registry.cn-hangzhou.aliyuncs.com/plctodb/plctodb:latest --push .

echo ""
echo "=== 操作完成 ==="
echo "镜像已推送至: registry.cn-hangzhou.aliyuncs.com/plctodb/plctodb:latest"
