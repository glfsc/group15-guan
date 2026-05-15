#!/usr/bin/env python3
import asyncio
import asyncpg
from app.config import settings

async def test_postgres_connection():
    """测试PostgreSQL数据库连接"""
    try:
        # 尝试连接到默认的postgres数据库
        conn = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database='postgres'  # 连接到默认数据库
        )
        print("✅ 成功连接到PostgreSQL服务器")
        
        # 检查toeic_app数据库是否存在
        db_exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            settings.DB_NAME
        )
        
        if db_exists:
            print(f"✅ 数据库 '{settings.DB_NAME}' 已存在")
        else:
            print(f"⚠️  数据库 '{settings.DB_NAME}' 不存在，正在创建...")
            await conn.execute(f"CREATE DATABASE {settings.DB_NAME}")
            print(f"✅ 数据库 '{settings.DB_NAME}' 创建成功")
        
        await conn.close()
        return True
        
    except asyncpg.exceptions.InvalidPasswordError:
        print("❌ 密码错误，请检查 .env 文件中的 DB_PASSWORD")
        print(f"当前配置: host={settings.DB_HOST}, port={settings.DB_PORT}, user={settings.DB_USER}, password={settings.DB_PASSWORD}")
        return False
    except asyncpg.exceptions.ConnectionDoesNotExistError:
        print("❌ 无法连接到PostgreSQL服务器，请检查:")
        print("1. PostgreSQL服务是否启动")
        print("2. 防火墙是否允许端口5432")
        print("3. 主机地址是否正确")
        return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

async def test_toeic_app_database():
    """测试toeic_app数据库连接"""
    try:
        conn = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        print(f"✅ 成功连接到数据库 '{settings.DB_NAME}'")
        
        # 测试基本查询
        version = await conn.fetchval("SELECT version()")
        print(f"✅ PostgreSQL版本: {version}")
        
        # 测试时区设置
        timezone = await conn.fetchval("SHOW timezone")
        print(f"✅ 时区设置: {timezone}")
        
        await conn.close()
        return True
        
    except asyncpg.exceptions.InvalidCatalogNameError:
        print(f"❌ 数据库 '{settings.DB_NAME}' 不存在")
        return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

if __name__ == "__main__":
    print("🔍 开始测试数据库连接...")
    print(f"配置信息:")
    print(f"  主机: {settings.DB_HOST}")
    print(f"  端口: {settings.DB_PORT}")
    print(f"  数据库: {settings.DB_NAME}")
    print(f"  用户: {settings.DB_USER}")
    print(f"  密码: {'*' * len(settings.DB_PASSWORD)}")
    print("-" * 50)
    
    # 测试连接并创建数据库
    if asyncio.run(test_postgres_connection()):
        print("-" * 50)
        print("🔍 测试目标数据库连接...")
        # 测试目标数据库
        if asyncio.run(test_toeic_app_database()):
            print("✅ 数据库连接测试全部通过！")
        else:
            print("❌ 目标数据库连接失败")
    else:
        print("❌ 数据库连接测试失败，请检查PostgreSQL服务")