-- 创建toeic_app数据库的SQL脚本
-- 使用以下方式之一执行：

-- 方法1：通过pgAdmin图形界面
-- 1. 打开pgAdmin 4
-- 2. 连接到PostgreSQL服务器
-- 3. 右键点击"Databases" -> "Create" -> "Database"
-- 4. 输入：
--    Database: toeic_app
--    Owner: postgres
-- 5. 点击"Save"

-- 方法2：通过psql命令行
-- 1. 打开命令提示符或PowerShell
-- 2. 运行: psql -U postgres
-- 3. 输入密码: sql1024
-- 4. 执行以下命令：

-- 创建数据库
CREATE DATABASE toeic_app 
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Chinese (Simplified)_China.936'
    LC_CTYPE = 'Chinese (Simplified)_China.936'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

-- 检查数据库是否创建成功
SELECT datname, datcollate, datctype 
FROM pg_database 
WHERE datname = 'toeic_app';

-- 显示数据库列表
\l

-- 连接到toeic_app数据库
\c toeic_app

-- 检查连接
SELECT current_database(), current_user;

-- 退出psql
\q

-- 方法3：通过Windows PowerShell或命令提示符（一行命令）
-- psql -U postgres -c "CREATE DATABASE toeic_app;"
-- psql -U postgres -d toeic_app -c "SELECT current_database();"

-- 注意事项：
-- 1. 确保PostgreSQL服务已启动
-- 2. 密码是.env文件中配置的sql1024
-- 3. 如果连接失败，检查PostgreSQL服务状态