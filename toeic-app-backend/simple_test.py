#!/usr/bin/env python3
import subprocess
import sys
import os

def test_postgres_connection():
    """测试PostgreSQL连接（使用命令行）"""
    print("🔍 测试PostgreSQL连接...")
    
    # 方法1：使用psql命令行工具
    try:
        # 尝试连接到默认的postgres数据库
        print("尝试方法1: 使用psql连接到PostgreSQL...")
        result = subprocess.run(
            ['psql', '-U', 'postgres', '-h', 'localhost', '-p', '5432', '-c', 'SELECT version();'],
            capture_output=True,
            text=True,
            input='sql1024\n'  # 输入密码
        )
        
        if result.returncode == 0:
            print("✅ PostgreSQL连接成功！")
            print(f"输出:\n{result.stdout}")
            return True
        else:
            print(f"❌ psql连接失败: {result.stderr}")
            
    except FileNotFoundError:
        print("⚠️  psql命令未找到，尝试方法2...")
    
    # 方法2：使用pg_isready工具
    try:
        print("尝试方法2: 使用pg_isready检查服务状态...")
        result = subprocess.run(
            ['pg_isready', '-h', 'localhost', '-p', '5432'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ PostgreSQL服务正在运行")
            return True
        else:
            print(f"❌ PostgreSQL服务未运行: {result.stdout}")
            
    except FileNotFoundError:
        print("⚠️  pg_isready命令未找到，尝试方法3...")
    
    # 方法3：检查服务状态
    print("尝试方法3: 检查Windows服务状态...")
    try:
        result = subprocess.run(
            ['sc', 'query', 'postgresql-x64-16'],
            capture_output=True,
            text=True,
            shell=True
        )
        
        if 'RUNNING' in result.stdout:
            print("✅ PostgreSQL服务正在运行（Windows服务）")
            return True
        else:
            print(f"❌ PostgreSQL服务未运行: {result.stdout[:200]}")
    except Exception as e:
        print(f"❌ 服务检查失败: {e}")
    
    return False

def create_database():
    """创建数据库"""
    print("\n🔨 尝试创建toeic_app数据库...")
    
    # 创建数据库的SQL命令
    create_db_sql = "CREATE DATABASE toeic_app;"
    
    try:
        result = subprocess.run(
            ['psql', '-U', 'postgres', '-h', 'localhost', '-p', '5432', '-c', create_db_sql],
            capture_output=True,
            text=True,
            input='sql1024\n'
        )
        
        if result.returncode == 0:
            print("✅ 数据库创建成功！")
            return True
        else:
            print(f"❌ 数据库创建失败: {result.stderr}")
            # 可能是数据库已存在
            if "already exists" in result.stderr:
                print("⚠️  数据库可能已存在")
                return True
            return False
            
    except FileNotFoundError:
        print("❌ psql命令未找到，无法创建数据库")
        return False

def check_database():
    """检查数据库是否存在"""
    print("\n🔍 检查toeic_app数据库是否存在...")
    
    check_sql = "SELECT 1 FROM pg_database WHERE datname = 'toeic_app';"
    
    try:
        result = subprocess.run(
            ['psql', '-U', 'postgres', '-h', 'localhost', '-p', '5432', '-c', check_sql, '-t'],
            capture_output=True,
            text=True,
            input='sql1024\n'
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if output == '1':
                print("✅ toeic_app数据库已存在")
                return True
            else:
                print("❌ toeic_app数据库不存在")
                return False
        else:
            print(f"❌ 检查失败: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ psql命令未找到")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("PostgreSQL数据库连接测试")
    print("=" * 50)
    
    # 测试连接
    if test_postgres_connection():
        print("\n✅ PostgreSQL服务器连接正常")
        
        # 检查数据库
        if check_database():
            print("\n🎉 所有检查通过！数据库已准备就绪")
        else:
            print("\n⚠️  数据库不存在，尝试创建...")
            if create_database():
                print("\n🎉 数据库创建成功！")
            else:
                print("\n❌ 数据库创建失败，请手动创建数据库")
                print("\n手动创建步骤:")
                print("1. 打开pgAdmin 4")
                print("2. 连接到PostgreSQL服务器")
                print("3. 右键点击'Databases' -> 'Create' -> 'Database'")
                print("4. 输入名称: toeic_app")
                print("5. 点击'Save'")
    else:
        print("\n❌ PostgreSQL连接测试失败")
        print("\n请检查:")
        print("1. PostgreSQL服务是否启动")
        print("2. 密码是否正确（.env文件中配置为sql1024）")
        print("3. 端口5432是否被占用")
        print("\n启动PostgreSQL服务:")
        print("  net start postgresql-x64-16")
        print("\n或者通过Windows服务管理器启动")
    
    print("\n" + "=" * 50)