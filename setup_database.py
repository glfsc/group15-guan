"""
数据库配置脚本
创建 PostgreSQL 数据库和用户
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    """创建数据库和表结构"""
    
    # 基本连接参数
    host = "localhost"
    port = 5432
    user = "postgres"
    password = "sql1024"
    database = "toeic_app"
    
    # 连接到 PostgreSQL
    conn = None
    cursor = None
    
    try:
        # 连接到 PostgreSQL 服务器（默认数据库）
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"  # 连接默认数据库
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 检查数据库是否存在
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{database}'")
        exists = cursor.fetchone()
        
        if not exists:
            # 创建数据库
            print(f"创建数据库: {database}")
            cursor.execute(f"CREATE DATABASE {database}")
            print(f"数据库创建成功")
        else:
            print(f"数据库已存在: {database}")
        
        cursor.close()
        conn.close()
        
        # 重新连接到新数据库
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        
        # 检查表是否存在，如果不存在则通过脚本创建
        print("数据库连接成功，请运行以下命令创建表：")
        print("\n1. 切换到后端目录：")
        print("   cd toeic-app-backend")
        print("\n2. 安装Python依赖：")
        print("   pip install -r requirements.txt")
        print("\n3. 运行数据库初始化脚本：")
        print("   python scripts/init_database.py")
        
        cursor.close()
        
    except Exception as e:
        print(f"错误: {e}")
        print("\n请确保 PostgreSQL 已安装并运行")
        print("PostgreSQL 默认配置：")
        print("  主机: localhost")
        print("  端口: 5432")
        print("  用户名: postgres")
        print("  密码: 空")
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_database()
