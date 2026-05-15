#!/usr/bin/env python3
import sys
import subprocess
import os

def test_with_psql():
    """使用psql命令行工具测试"""
    print("🔍 使用psql测试数据库连接...")
    
    # 尝试多种可能的psql路径
    possible_paths = [
        r"C:\Program Files\PostgreSQL\16\bin\psql.exe",
        r"C:\Program Files\PostgreSQL\15\bin\psql.exe",
        r"C:\Program Files\PostgreSQL\14\bin\psql.exe",
        r"C:\Program Files\PostgreSQL\13\bin\psql.exe",
        r"C:\Program Files\PostgreSQL\12\bin\psql.exe",
        r"C:\Program Files (x86)\PostgreSQL\16\bin\psql.exe",
        r"C:\Program Files (x86)\PostgreSQL\15\bin\psql.exe",
        r"C:\Program Files (x86)\PostgreSQL\14\bin\psql.exe",
    ]
    
    psql_path = None
    for path in possible_paths:
        if os.path.exists(path):
            psql_path = path
            print(f"✅ 找到psql: {path}")
            break
    
    if not psql_path:
        print("❌ 未找到psql.exe，请手动安装依赖或使用pgAdmin")
        return False
    
    # 测试连接到postgres数据库
    print("\n🔍 测试连接到postgres数据库...")
    cmd = [psql_path, "-U", "postgres", "-h", "localhost", "-p", "5432", "-d", "postgres", "-c", "SELECT version();"]
    
    try:
        # 使用环境变量传递密码
        env = os.environ.copy()
        env['PGPASSWORD'] = 'sql1024'
        
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            print("✅ PostgreSQL服务器连接成功!")
            print(f"输出:\n{result.stdout}")
            
            # 检查toeic_app数据库是否存在
            print("\n🔍 检查toeic_app数据库是否存在...")
            check_cmd = [psql_path, "-U", "postgres", "-h", "localhost", "-p", "5432", "-d", "postgres", 
                        "-c", "SELECT datname FROM pg_database WHERE datname = 'toeic_app';", "-t"]
            
            result2 = subprocess.run(check_cmd, capture_output=True, text=True, env=env)
            
            if result2.returncode == 0:
                output = result2.stdout.strip()
                if output:
                    print(f"✅ toeic_app数据库已存在: {output}")
                    return True
                else:
                    print("❌ toeic_app数据库不存在")
                    return False
            else:
                print(f"❌ 检查失败: {result2.stderr}")
                return False
        else:
            print(f"❌ 连接失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False

def test_with_powershell():
    """使用PowerShell测试"""
    print("\n🔍 使用PowerShell测试...")
    
    # 检查数据库是否存在的PowerShell命令
    ps_command = '''
    $ErrorActionPreference = "Stop"
    try {
        $connString = "Host=localhost;Port=5432;Database=postgres;Username=postgres;Password=sql1024"
        $conn = New-Object Npgsql.NpgsqlConnection($connString)
        $conn.Open()
        Write-Host "✅ PostgreSQL连接成功"
        
        $cmd = $conn.CreateCommand()
        $cmd.CommandText = "SELECT datname FROM pg_database WHERE datname = 'toeic_app'"
        $reader = $cmd.ExecuteReader()
        
        if ($reader.Read()) {
            Write-Host "✅ toeic_app数据库已存在"
            $reader.Close()
            $conn.Close()
            exit 0
        } else {
            Write-Host "❌ toeic_app数据库不存在"
            $reader.Close()
            $conn.Close()
            exit 1
        }
    } catch {
        Write-Host "❌ 连接失败: $_"
        exit 2
    }
    '''
    
    try:
        result = subprocess.run(['powershell', '-Command', ps_command], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"❌ PowerShell执行失败: {e}")
        return False

def main():
    print("=" * 60)
    print("PostgreSQL数据库连接测试 (简化版)")
    print("=" * 60)
    
    # 方法1：使用psql
    if test_with_psql():
        print("\n🎉 数据库连接测试通过！")
        print("\n下一步：")
        print("1. 启动后端服务:")
        print("   cd toeic-app-backend")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("\n2. 如果启动失败，可能需要安装依赖:")
        print("   pip install asyncpg")
    else:
        print("\n❌ psql测试失败，尝试PowerShell...")
        
        # 方法2：使用PowerShell
        if test_with_powershell():
            print("\n🎉 数据库连接测试通过！")
        else:
            print("\n⚠️  所有测试方法都失败")
            print("\n请确认:")
            print("1. PostgreSQL服务正在运行")
            print("2. 数据库 'toeic_app' 已创建")
            print("3. 密码正确: sql1024")
            print("\n在pgAdmin中创建数据库步骤:")
            print("1. 右键 'Databases' -> 'Create' -> 'Database'")
            print("2. 名称: toeic_app")
            print("3. Owner: postgres")
            print("4. 点击 'Save'")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()