# 挤出机工艺参数管理系统

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/yourusername/plc-process-management)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> 基于FastAPI + Vue3的挤出机工艺参数管理系统，支持PLC数据读取、工艺参数管理、历史记录存档等功能。

![Logo](frontend/logo.png)

## 📋 功能特性

- 🔐 **用户管理** - 支持管理员/操作员角色，JWT认证
- 🏭 **机台管理** - 机台信息维护，PLC连接配置
- 📦 **产品管理** - 产品信息维护，版本号自动管理
- 📋 **模板管理** - 工艺参数模板，支持只读/可写参数区分
- 📊 **工艺参数** - 实时读取PLC数据，参数批量写入
- 📜 **历史记录** - 工艺参数存档，支持导出和PLC回写
- 🎨 **响应式UI** - 现代化界面，支持分页和加载状态

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
- **原生CSS** - 自定义样式，响应式布局
- **Fetch API** - 后端数据交互

### 数据库

- **MySQL 5.7+** - 关系型数据库

## 📁 项目结构

```
plctodb/
├── backend/                    # 后端代码
│   ├── main.py                # FastAPI主应用
│   ├── models.py              # SQLAlchemy数据模型
│   ├── schemas.py             # Pydantic数据验证
│   ├── database.py            # 数据库连接配置
│   ├── config.py              # 应用配置
│   ├── plc_client.py          # PLC通信客户端
│   ├── .env                   # 环境变量（需自行创建）
│   ├── .env.example           # 环境变量模板
│   └── database_schema.sql    # 数据库结构
├── frontend/                   # 前端代码
│   ├── index.html             # 主页面
│   └── logo.png               # 系统Logo
├── requirements.txt            # Python依赖
└── README.md                   # 项目文档
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- MySQL 5.7+
- Node.js（可选，用于前端开发）

### 2. 安装步骤

#### 克隆项目

```bash
git clone https://github.com/yourusername/plc-process-management.git
cd plc-process-management
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

#### 启动后端服务

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 访问前端页面

直接打开 `frontend/index.html` 或使用本地服务器：

```bash
cd frontend
python -m http.server 8080
```

访问 <http://localhost:8080>

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

## 📖 操作文档

### 1. 登录系统

1. 打开系统首页
2. 输入用户名和密码
   - 默认管理员：admin / admin
3. 点击"登录"按钮

### 2. 用户管理（管理员）

#### 添加用户

1. 点击左侧菜单"用户管理"
2. 点击"添加用户"按钮
3. 填写用户名、密码、角色
4. 点击"保存"

#### 修改密码

1. 在用户列表中找到目标用户
2. 点击"修改密码"按钮
3. 输入新密码并确认
4. 点击"保存"

### 3. 机台管理

#### 添加机台

1. 点击左侧菜单"机台管理"
2. 点击"添加机台"按钮
3. 填写机台信息：
   - 机台编号
   - 机台名称
   - 类型
   - IP地址
   - Rack/Slot
4. 点击"保存"

#### 绑定模板

1. 在机台列表中点击"绑定模板"按钮
2. 选择要绑定的工艺模板
3. 点击"保存"

#### 读取PLC数据

1. 点击机台行的"读取"按钮
2. 系统通过绑定的模板参数读取PLC数据
3. 显示读取结果

### 4. 产品管理

#### 添加产品

1. 点击左侧菜单"产品管理"
2. 点击"添加产品"按钮
3. 填写产品信息：
   - 产品编号
   - 产品名称
   - 产品规格
4. 点击"保存"

#### 编辑产品

1. 在产品列表中点击"编辑"按钮
2. 修改产品信息
3. 点击"保存"（版本号自动+1）

#### 查看历史记录

1. 点击产品名称（蓝色链接）
2. 弹出历史记录列表
3. 可查看该产品的所有工艺记录

### 5. 模板管理

#### 创建模板

1. 点击左侧菜单"模板管理"
2. 点击"添加模板"按钮
3. 输入模板名称和描述
4. 点击"保存"

#### 管理模板参数

1. 在模板列表中点击"管理参数"按钮
2. 添加/编辑/删除参数：
   - 参数名称
   - PLC地址
   - 数据类型（Int/Real/Bool）
   - 单位
   - 只读/可写
3. 点击"保存"

### 6. 工艺参数

#### 查看参数

1. 点击左侧菜单"工艺参数"
2. 选择机台和产品
3. 显示关联的工艺参数列表

#### 修改参数值

1. 在参数列表中直接编辑数值
2. 点击"保存"按钮

#### 保存工艺记录

1. 点击"保存为新记录"按钮
2. 填写备注信息（可选）
3. 点击"确认"

### 7. 历史记录（存档参数）

#### 查看记录

1. 点击左侧菜单"存档参数"
2. 查看所有工艺记录列表
3. 支持分页浏览

#### 查看详情

1. 点击记录行的"查看详情"按钮
2. 显示该记录的所有参数值

#### 写入PLC

1. 点击记录行的"写入PLC"按钮
2. 弹出确认框，显示要写入的参数
3. 点击"确认写入"
4. 系统将历史参数值写入PLC

## 🔌 PLC通信说明

### 支持的PLC类型

- 西门子S7-1200/1500系列
- 支持S7协议的其他设备

### 数据类型映射

| 系统类型 | PLC类型 | 说明     |
| ---- | ----- | ------ |
| Int  | INT   | 16位整数  |
| Real | REAL  | 32位浮点数 |
| Bool | BOOL  | 布尔值    |

### 地址格式

- **DB块**: `DB1.DBW0` (Word), `DB1.DBD4` (DWord/Real)
- **M区**: `M0.0` (Bool), `MW2` (Word)
- **I/Q区**: `I0.0`, `Q0.0`

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

### Q: 前端页面白屏？

A: 检查以下几点：

- 浏览器控制台是否有报错
- 后端服务是否正常运行
- 网络请求是否被拦截

## 📝 更新日志

### v1.0.0 (2026-04-28)

- ✨ 初始版本发布
- ✨ 完整的CRUD功能
- ✨ PLC数据读取/写入
- ✨ 版本号管理
- ✨ 响应式UI设计

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

## 📄 许可证

[MIT License](LICENSE)

## 📞 联系方式

- 作者：Your Name
- 邮箱：<your.email@example.com>
- 项目主页：<https://github.com/yourusername/plc-process-management>

***

**Made with ❤️ by YARDCOM**
