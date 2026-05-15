#!/usr/bin/env python3
import sys
import os

# 尝试通过多种方式测试数据库连接

def test_with_sqlalchemy():
    """使用SQLAlchemy测试数据库连接"""
    print("🔍 使用SQLAlchemy测试数据库连接...")
    try:
        from sqlalchemy import create_engine, text
        
        # 使用.env文件中的配置
        DATABASE_URL = "postgresql+psycopg2://postgres:sql1024@localhost:5432/toeic_app"
        
        print(f"连接字符串: {DATABASE_URL.replace('sql1024', '******')}")
        
        # 创建连接引擎
        engine = create_engine(DATABASE_URL)
        
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version(), current_database(), current_user"))
            row = result.fetchone()
            print(f"✅ 连接成功!")
            print(f"   PostgreSQL版本: {row[0]}")
            print(f"   当前数据库: {row[1]}")
            print(f"   当前用户: {row[2]}")
            
            # 检查表是否存在
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = result.fetchall()
            
            if tables:
                print(f"✅ 数据库中有 {len(tables)} 个表:")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("ℹ️  数据库中没有表（正常，尚未初始化）")
            
            return True
            
    except Exception as e:
        print(f"❌ SQLAlchemy连接失败: {e}")
        return False

def test_simple_connection():
    """测试简单连接"""
    print("\n🔍 测试简单数据库连接...")
    try:
        # 尝试导入psycopg2
        import psycopg2
        
        try:
            # 尝试连接到toeic_app数据库
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="toeic_app",
                user="postgres",
                password="sql1024"
            )
            print("✅ 成功连接到toeic_app数据库")
            conn.close()
            return True
        except psycopg2.OperationalError as e:
            print(f"❌ 无法连接到toeic_app数据库: {e}")
            
            # 尝试连接到默认的postgres数据库
            try:
                conn = psycopg2.connect(
                    host="localhost",
                    port=5432,
                    database="postgres",
                    user="postgres",
                    password="sql1024"
                )
                print("✅ 成功连接到默认的postgres数据库")
                
                # 检查toeic_app是否存在
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'toeic_app'")
                exists = cursor.fetchone()
                
                if exists:
                    print("✅ toeic_app数据库已存在")
                else:
                    print("❌ toeic_app数据库不存在")
                    print("   请在pgAdmin中创建数据库:")
                    print("   1. 右键'Databases' -> 'Create' -> 'Database'")
                    print("   2. 名称: toeic_app")
                    print("   3. Owner: postgres")
                
                conn.close()
                return True
            except Exception as e2:
                print(f"❌ 无法连接到PostgreSQL: {e2}")
                return False
                
    except ImportError:
        print("❌ psycopg2模块未安装，尝试安装...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
            print("✅ psycopg2-binary安装成功，重新运行测试")
            return test_simple_connection()
        except:
            print("❌ 安装失败，请手动安装: pip install psycopg2-binary")
            return False

def check_requirements():
    """检查依赖是否安装"""
    print("\n🔍 检查Python依赖...")
    try:
        import pkg_resources
        
        # 检查requirements.txt中的主要依赖
        required = ['fastapi', 'sqlalchemy', 'asyncpg', 'psycopg2-binary']
        
        for package in required:
            try:
                dist = pkg_resources.get_distribution(package)
                print(f"✅ {package}: {dist.version}")
            except:
                print(f"❌ {package}: 未安装")
                
    except Exception as e:
        print(f"⚠️  依赖检查失败: {e}")

def test_backend_connection():
    """使用后端项目的数据库连接测试"""
    print("\n🔍 使用后端项目配置测试...")
    try:
        # 导入项目配置
        import sys
        sys.path.insert(0, '.')
        from app.config import settings
        
        print(f"数据库配置:")
        print(f"  主机: {settings.DB_HOST}")
        print(f"  端口: {settings.DB_PORT}")
        print(f"  数据库: {settings.DB_NAME}")
        print(f"  用户: {settings.DB_USER}")
        print(f"  密码: {'*' * len(settings.DB_PASSWORD)}")
        print(f"  连接URL: {settings.DATABASE_URL.replace('sql1024', '******')}")
        
        return True
    except ImportError as e:
        print(f"❌ 无法导入配置: {e}")
        return False
    except Exception as e:
        print(f"❌ 配置读取错误: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("PostgreSQL数据库连接测试")
    print("=" * 60)
    
    # 检查依赖
    check_requirements()
    
    # 测试后端配置
    config_ok = test_backend_connection()
    
    # 测试简单连接
    connection_ok = test_simple_connection()
    
    # 测试SQLAlchemy连接
    sqlalchemy_ok = test_with_sqlalchemy()
    
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print("=" * 60)
    
    if connection_ok and sqlalchemy_ok:
        print("✅ 所有数据库连接测试通过！")
        print("\n🎉 数据库已准备就绪，可以启动后端服务:")
        print("cd toeic-app-backend")
        print("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("❌ 部分测试失败")
        
        if not connection_ok:
            print("\n⚠️ 基础连接测试失败:")
            print("   1. 确认PostgreSQL服务正在运行")
            print("   2. 确认密码正确 (sql1024)")
            print("   3. 确认数据库 'toeic_app' 已创建")
        
        if not sqlalchemy_ok:
            print("\n⚠️ SQLAlchemy连接失败:")
            print("   可能需要安装依赖: pip install sqlalchemy psycopg2-binary")
    
    print("\n" + "=" * 60)