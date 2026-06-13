# 挤出机工艺参数管理系统

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/pcb0y/plctodb)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> 基于FastAPI + Vue3的挤出机工艺参数管理系统，支持PLC数据读取、工艺参数管理、定时数据采集、历史趋势图等功能。

![Logo](frontend/logo.png)

## 📋 功能特性

- 🔐 **用户管理** - 支持管理员/操作员角色，JWT认证
- 🏭 **机台管理** - 机台信息维护，PLC连接配置，模板绑定
- 📦 **产品管理** - 产品信息维护，截面图上传，版本号管理
- 📋 **模板管理** - 工艺参数模板，支持只读/可写参数区分
- 📊 **工艺参数** - 实时读取PLC数据，参数批量写入，单参数编辑
- 📜 **存档参数** - 工艺参数存档，支持详情查看和PLC回写
- 📈 **趋势图** - PLC参数定时采集数据可视化，ECharts折线图
- ⏱️ **定时采集** - 每分钟自动采集PLC参数存库，长连接模式
- 🎨 **响应式UI** - 暗色主题，支持分页、加载状态、图片预览

## 🛠️ 技术栈

### 后端

- **FastAPI** - 高性能Python Web框架
- **SQLAlchemy** - ORM数据库操作
- **PyMySQL** - MySQL数据库连接
- **python-snap7** - PLC通信（西门子S7协议）
- **Passlib** - 密码加密
- **JWT** - 用户认证

### 前端

- **Vue 3** - 渐进式JavaScript框架
- **ECharts 5** - 数据可视化图表库
- **原生CSS** - 暗色主题，响应式布局
- **Fetch API** - 后端数据交互

### 数据库

- **MySQL 5.7+** - 关系型数据库

## 📁 项目结构

```
plctodb/
├── backend/                    # 后端代码
│   ├── main.py                # FastAPI主应用，启动/停止调度器
│   ├── models.py              # SQLAlchemy数据模型
│   ├── schemas.py             # Pydantic数据验证
│   ├── database.py            # 数据库连接配置
│   ├── config.py              # 应用配置
│   ├── plc_client.py          # PLC通信客户端
│   ├── scheduler.py           # PLC参数定时采集任务
│   ├── dependencies.py        # FastAPI依赖注入
│   ├── routers/               # API路由模块
│   │   ├── auth.py            # 用户认证
│   │   ├── machines.py        # 机台管理
│   │   ├── products.py        # 产品管理
│   │   ├── parameters.py      # 工艺参数
│   │   ├── templates.py       # 模板管理
│   │   ├── logs.py            # 操作日志
│   │   └── history.py         # 采集历史数据查询
│   ├── .env                   # 环境变量（需自行创建）
│   ├── .env.example           # 环境变量模板
│   └── database_schema.sql    # 数据库结构
├── frontend/                   # 前端代码
│   ├── index.html             # 主页面（Vue3单文件应用）
│   ├── js/vue.global.js       # Vue3框架
│   └── logo.png               # 系统Logo
├── logs/                       # 运行日志
├── requirements.txt            # Python依赖
├── run.sh                      # 启动脚本
├── start_backend.sh            # 后端启动脚本
└── README.md                   # 项目文档
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- MySQL 5.7+

### 2. 安装步骤

#### 克隆项目

```bash
git clone https://github.com/pcb0y/plctodb.git
cd plctodb
```

#### 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

#### 安装依赖

```bash
pip install -r requirements.txt
```

#### 配置环境变量

```bash
cp backend/.env.example backend/.env
# 编辑 .env 文件，填写实际配置
```

#### 创建数据库

```bash
mysql -u root -p < backend/database_schema.sql
```

### 3. 启动服务

```bash
cd backend
python main.py
```

服务启动后访问 <http://localhost:9527>

## ⚙️ 配置说明

### 环境变量 (.env)

```env
# 数据库配置
DB_HOST=localhost          # 数据库主机
DB_PORT=3306               # 数据库端口
DB_USER=root               # 数据库用户名
DB_PASSWORD=your_password  # 数据库密码
DB_NAME=plc_process_db     # 数据库名称

# JWT配置
SECRET_KEY=your-secret-key-change-in-production  # JWT密钥
ALGORITHM=HS256            # 加密算法
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # Token过期时间（分钟）

# PLC配置
PLC_PORT=102               # PLC通信端口
PLC_DB_NUMBER=1            # PLC数据块编号
```

## 📖 功能说明

### 定时数据采集

系统启动后自动开始定时采集（每60秒），从所有绑定了模板的机台PLC读取参数并存入 `parameter_collection` 表。

**采集特性：**
- 长连接模式：维护PLC持久连接，断线自动重连
- slot分组优化：按slot排序读取，减少断连重连次数
- 数据分离：自动采集数据存 `parameter_collection`，手动存档存 `process_records`

### 趋势图

点击左侧菜单"趋势图"：

1. 选择机台（自动加载有采集数据的机台）
2. 选择时间模式：
   - **快捷选择**：5分钟/30分钟/1小时/6小时/24小时/7天/30天/1年
   - **自定义时间段**：指定开始和结束时间
3. 勾选要展示的参数（支持多选）
4. 点击"查询"生成折线图

图表支持：鼠标悬停查看数值、底部拖拽缩放、图例点击显示/隐藏。

### 其他功能

- **机台管理** - 添加机台、绑定模板、读取PLC数据
- **产品管理** - 产品信息维护、截面图上传预览
- **模板管理** - 创建参数模板、管理模板参数
- **工艺参数** - 实时读取、单参数编辑、保存记录
- **存档参数** - 历史记录查看、写入PLC回写
- **操作日志** - 管理员查看系统操作记录
- **用户管理** - 管理员添加用户、修改密码

## 🔌 PLC通信说明

### 支持的PLC类型

- 西门子S7-200/300/1200/1500系列
- 支持S7协议的其他设备

### 数据类型映射

| 系统类型 | PLC类型 | 说明     |
| ---- | ----- | ------ |
| Int  | INT   | 16位整数  |
| Real | REAL  | 32位浮点数 |
| Bool | BOOL  | 布尔值    |

### 地址格式

- **V区**: `VW0` (Word), `VD0` (DWord/Real), `VB0` (Byte), `V0.0` (Bit)
- **计数器**: `C0`
- **定时器**: `T0`

## 🗄️ 数据库表说明

| 表名 | 说明 |
|------|------|
| users | 用户信息 |
| machines | 机台信息 |
| products | 产品信息 |
| templates | 工艺模板 |
| template_parameters | 模板参数定义 |
| process_records | 手动存档记录 |
| process_parameter_values | 存档参数值 |
| parameter_collection | 定时采集数据 |
| operation_logs | 操作日志 |

## 🔒 安全说明

1. **密码安全** - 使用bcrypt加密存储
2. **JWT认证** - API访问需携带有效Token
3. **SQL注入防护** - 使用SQLAlchemy ORM
4. **CORS配置** - 支持跨域访问

## 🐛 常见问题

### Q: 无法连接PLC？

A: 检查以下几点：

- PLC IP地址是否正确
- 网络是否连通（ping测试）
- PLC是否允许远程连接
- Rack和Slot配置是否正确

### Q: 数据库连接失败？

A: 检查以下几点：

- MySQL服务是否启动
- .env文件中的数据库配置是否正确
- 数据库用户权限是否足够

### Q: 趋势图没有数据？

A: 检查以下几点：

- 机台是否已绑定模板
- 后端日志中是否有采集记录
- 数据库中 `parameter_collection` 表是否有数据

## 📝 更新日志

### v1.2.0 (2026-06-13)

- ✨ 新增PLC参数定时采集功能（每分钟自动采集）
- ✨ 新增趋势图页面（ECharts折线图）
- ✨ 支持快捷时间范围和自定义时间段查询
- ✨ PLC长连接模式，断线自动重连
- ✨ 采集参数按slot分组优化
- 🐛 修复采集时间时区问题

### v1.1.0 (2026-05-16)

- ✨ 产品管理新增截面图上传和预览
- ✨ 产品列表添加截面图缩略图列
- ✨ 表格布局优化（横向滚动、列宽控制）
- ✨ 文件上传按钮样式美化
- 🐛 修复前端新增产品400错误无提示

### v1.0.0 (2026-04-28)

- ✨ 初始版本发布
- ✨ 完整的CRUD功能
- ✨ PLC数据读取/写入
- ✨ 版本号管理
- ✨ 响应式UI设计

## 📄 许可证

[MIT License](LICENSE)

***

**Made with ❤️ by YARDCOM**
