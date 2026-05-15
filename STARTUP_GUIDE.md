# 托业学习应用启动指南

## 环境要求
- Python 3.11+
- PostgreSQL 15+
- Node.js 18+

## 配置步骤

### 1. 安装系统依赖
```bash
# Windows用户需要手动安装：
# 1. PostgreSQL: https://www.postgresql.org/download/windows/
# 2. Redis: https://redis.io/download/ (可选，目前项目未使用Redis)
```

### 2. 后端配置
```bash
# 进入后端目录
cd toeic-app-backend

# 创建虚拟环境（推荐）
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装Python依赖
pip install -r requirements.txt

# 华为云MaaS API密钥已配置完成
# 如果需要OBS功能，请配置OBS_AK和OBS_SK

# 初始化数据库
python scripts/init_database.py

# 启动后端服务
python scripts/start_server.py
```
服务启动后访问：http://localhost:8000

### 3. 前端配置
```bash
# 进入前端目录
cd toeic-app-frontend

# 安装Node依赖
npm install

# 启动开发服务器
npm run dev
```
前端服务启动后访问：http://localhost:3000

### 4. 访问应用
打开浏览器访问：http://localhost:3000

## 快速测试

### 创建测试用户
使用curl或Postman调用API创建用户：

```bash
curl -X POST http://localhost:8000/api/v1/settings/users \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "测试用户",
    "email": "test@example.com",
    "learning_goal": "提高托业听力成绩"
  }'
```

### 测试API接口

1. **生成听力题目**：
```bash
curl -X POST "http://localhost:8000/api/v1/questions/listening/generate?difficulty=medium&question_type=conversation&count=5"
```

2. **生成语法题目**：
```bash
curl -X POST "http://localhost:8000/api/v1/questions/grammar/generate?knowledge_point=tense&difficulty=medium&count=5"
```

## 故障排除

### 1. PostgreSQL连接失败
错误信息：`could not connect to server: Connection refused`
解决：
- 确保PostgreSQL服务正在运行
- Windows: 检查PostgreSQL服务是否启动
- Linux/Mac: `sudo service postgresql start`

### 2. Python依赖安装失败
使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. MaaS API调用失败
检查：
- API密钥是否正确配置
- 网络连接是否正常
- 华为云MaaS服务是否可用

### 4. 前端无法连接后端
检查：
- 后端服务是否正常运行
- 前端代理配置是否正确（vite.config.ts）
- 端口是否被占用（后端8000，前端3000）

## 开发说明

### API文档
访问 `http://localhost:8000/docs` 查看Swagger API文档

### 数据库管理
- 数据库名称：toeic_app
- 用户名：postgres
- 密码：空
- 端口：5432

### 项目结构
后端服务：FastAPI + SQLAlchemy + PostgreSQL
前端界面：Vue3 + TypeScript + Element Plus
AI集成：华为云MaaS API

## 注意事项
1. 首次使用需配置华为云MaaS API密钥（已配置）
2. 如需音频功能，需配置华为云OBS
3. 项目已配置为开发模式，生产环境需要调整配置
