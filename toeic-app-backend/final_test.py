#!/usr/bin/env python3
import sys
import os

# 添加PostgreSQL安装路径到系统PATH（如果找到）
def setup_environment():
    """设置环境变量以便找到psql"""
    print("🔧 尝试设置PostgreSQL环境...")
    
    # 常见的PostgreSQL安装路径
    possible_paths = [
        r"C:\Program Files\PostgreSQL\16\bin",
        r"C:\Program Files (x86)\PostgreSQL\16\bin", 
        r"D:\Program Files\PostgreSQL\16\bin",
        r"D:\Program Files (x86)\PostgreSQL\16\bin",
        # 尝试其他版本
        r"C:\Program Files\PostgreSQL\15\bin",
        r"C:\Program Files\PostgreSQL\14\bin",
        r"C:\Program Files\PostgreSQL\13\bin",
        r"C:\Program Files\PostgreSQL\12\bin",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ 找到PostgreSQL bin目录: {path}")
            os.environ['PATH'] = path + os.pathsep + os.environ['PATH']
            return path
    
    print("⚠️  未找到PostgreSQL bin目录，请手动添加")
    return None

def test_with_sql_command():
    """使用SQL命令测试连接"""
    print("\n🔍 测试数据库连接...")
    
    # 检查toeic_app数据库是否存在的SQL
    check_db_sql = '''
    SELECT 
        CASE 
            WHEN EXISTS (SELECT 1 FROM pg_database WHERE datname = 'toeic_app') 
            THEN 'Database toeic_app exists' 
            ELSE 'Database toeic_app does not exist' 
        END as status;
    '''
    
    # 尝试连接并执行SQL
    try:
        import subprocess
        
        # 使用Windows cmd执行psql
        cmd = [
            'cmd', '/c', 
            'echo', check_db_sql, '|', 
            'psql', '-U', 'postgres', '-h', 'localhost', '-p', '5432', '-d', 'postgres'
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        # 运行命令，输入密码
        result = subprocess.run(
            ' '.join(cmd),
            capture_output=True,
            text=True,
            shell=True,
            input='sql1024\n'
        )
        
        print(f"返回码: {result.returncode}")
        print(f"输出:\n{result.stdout}")
        if result.stderr:
            print(f"错误:\n{result.stderr}")
            
        if result.returncode == 0:
            if 'Database toeic_app exists' in result.stdout:
                print("✅ toeic_app数据库已存在！")
                return True
            elif 'Database toeic_app does not exist' in result.stdout:
                print("❌ toeic_app数据库不存在")
                return False
        else:
            print("❌ 命令执行失败")
            return False
            
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False

def provide_manual_instructions():
    """提供手动操作指南"""
    print("\n" + "="*60)
    print("📖 手动创建数据库指南")
    print("="*60)
    
    print("\n方法1: 使用pgAdmin 4 (推荐)")
    print("-" * 40)
    print("1. 打开pgAdmin 4 (开始菜单搜索)")
    print("2. 输入密码: sql1024")
    print("3. 右键'Databases' -> 'Create' -> 'Database'")
    print("4. 输入名称: toeic_app")
    print("5. Owner选择: postgres")
    print("6. 点击'Save'")
    
    print("\n方法2: 使用命令提示符")
    print("-" * 40)
    print("1. 打开命令提示符 (cmd)")
    print("2. 找到psql.exe的路径，例如:")
    print("   cd \"C:\\Program Files\\PostgreSQL\\16\\bin\"")
    print("3. 运行: psql -U postgres")
    print("4. 输入密码: sql1024")
    print("5. 执行: CREATE DATABASE toeic_app;")
    print("6. 检查: \\l")
    print("7. 退出: \\q")
    
    print("\n方法3: 使用PowerShell (一行命令)")
    print("-" * 40)
    print('& "C:\\Program Files\\PostgreSQL\\16\\bin\\psql.exe" -U postgres -c "CREATE DATABASE toeic_app;"')
    print("(需要输入密码: sql1024)")
    
    print("\n" + "="*60)
    print("✅ 数据库创建后，运行以下命令测试后端:")
    print("   cd toeic-app-backend")
    print("   python -m app.db.init_db")
    print("="*60)

if __name__ == "__main__":
    print("=" * 60)
    print("PostgreSQL数据库连接和创建测试")
    print("=" * 60)
    
    # 设置环境
    setup_environment()
    
    # 测试连接
    if test_with_sql_command():
        print("\n🎉 数据库检查完成！toeic_app数据库已存在")
        print("\n现在可以启动后端服务了:")
        print("cd toeic-app-backend")
        print("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("\n❌ 无法检查数据库状态或数据库不存在")
        provide_manual_instructions()
    
    print("\n" + "="*60)