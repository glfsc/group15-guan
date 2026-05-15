# 托业英语学习应用

一个基于Python FastAPI和Vue3的托业英语学习应用，帮助用户提高听力和语法能力。

## 功能特性

- 🎧 **听力练习**：生成托业听力题目，支持多种题型
- 📚 **语法练习**：覆盖托业核心语法知识点
- 🤖 **AI生成题目**：集成华为云MaaS API智能生成题目
- 📊 **学习进度追踪**：统计正确率、能力评估
- ⚙️ **个性化设置**：字体大小、背景颜色等个性化配置
- 👤 **个人信息管理**：管理用户学习目标

## 技术栈

### 后端
- Python 3.11
- FastAPI
- SQLAlchemy (异步)
- PostgreSQL
- Redis
- 华为云MaaS API
- 华为云OBS

### 前端
- Vue 3
- TypeScript
- Element Plus
- Pinia
- Vue Router
- Axios

## 项目结构

```
toeic-app-backend/          # 后端项目
├── app/
│   ├── models/            # 数据模型
│   ├── routers/           # API路由
│   ├── services/          # 业务服务
│   ├── clients/           # 外部API客户端
│   ├── schemas/           # 数据验证模式
│   ├── db/                # 数据库配置
│   └── main.py            # 应用入口
├── scripts/               # 启动脚本
└── requirements.txt       # Python依赖

toeic-app-frontend/         # 前端项目
├── src/
│   ├── views/             # 页面组件
│   ├── components/        # 通用组件
│   ├── api/               # API封装
│   ├── stores/            # 状态管理
│   ├── router/            # 路由配置
│   └── main.ts            # 入口文件
└── package.json           # Node依赖
```

## 快速开始

### 1. 环境准备

确保已安装：
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### 2. 后端配置

```bash
cd toeic-app-backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，填入数据库连接信息和华为云API密钥

# 初始化数据库
python scripts/init_database.py

# 启动服务
python scripts/start_server.py
```

### 3. 前端配置

```bash
cd toeic-app-frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用

打开浏览器访问：http://localhost:3000

## 环境变量配置

在`.env`文件中配置以下参数：

```env
# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/toeic_app
DB_HOST=localhost
DB_PORT=5432
DB_NAME=toeic_app
DB_USER=postgres
DB_PASSWORD=password

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379

# 华为云MaaS API配置
MAAS_ENDPOINT=https://maas.cn-north-4.myhuaweicloud.com
MAAS_AK=your_access_key
MAAS_SK=your_secret_key
MAAS_MODEL=glm-4

# 华为云OBS配置
OBS_BUCKET=toeic-audio-files
OBS_REGION=cn-north-4
OBS_AK=your_access_key
OBS_SK=your_secret_key
```

## API接口

### 题目生成
- `POST /api/v1/questions/listening/generate` - 生成听力题
- `POST /api/v1/questions/grammar/generate` - 生成语法题

### 答题
- `POST /api/v1/answers/submit` - 提交答案

### 统计
- `GET /api/v1/stats/progress/{user_id}` - 获取学习进度
- `GET /api/v1/stats/errors/{user_id}` - 获取错题列表

### 设置
- `GET /api/v1/settings/page/{user_id}` - 获取页面设置
- `PUT /api/v1/settings/page/{user_id}` - 更新页面设置
- `GET /api/v1/settings/users/{user_id}` - 获取用户信息
- `PUT /api/v1/settings/users/{user_id}` - 更新用户信息

## 开发说明

### 后端开发
```bash
# 运行开发服务器（热重载）
python scripts/start_server.py
```

### 前端开发
```bash
# 开发模式
npm run dev

# 构建生产版本
npm run build
```

## 注意事项

1. 确保华为云MaaS API密钥正确配置
2. PostgreSQL数据库需要提前创建
3. 音频文件功能需要配置华为云OBS
4. 首次使用需要通过API创建用户

## License

MIT
