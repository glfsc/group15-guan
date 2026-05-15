#!/usr/bin/env python3
import socket
import sys

def test_port():
    """测试PostgreSQL端口是否开放"""
    print("🔍 测试PostgreSQL端口(5432)...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 5432))
        sock.close()
        
        if result == 0:
            print("✅ 端口5432已开放（PostgreSQL服务正在运行）")
            return True
        else:
            print("❌ 端口5432未开放，PostgreSQL服务可能未运行")
            return False
    except Exception as e:
        print(f"❌ 端口测试失败: {e}")
        return False

def check_windows_service():
    """检查Windows服务状态"""
    print("\n🔍 检查PostgreSQL Windows服务...")
    try:
        import subprocess
        result = subprocess.run(
            ['sc', 'query', 'postgresql-x64-16'],
            capture_output=True,
            text=True,
            shell=True
        )
        
        if 'RUNNING' in result.stdout:
            print("✅ PostgreSQL服务正在运行")
            
            # 提取服务状态信息
            for line in result.stdout.split('\n'):
                if 'STATE' in line:
                    print(f"   服务状态: {line.strip()}")
            return True
        else:
            print(f"❌ PostgreSQL服务未运行")
            print(f"   输出: {result.stdout[:200]}")
            return False
    except Exception as e:
        print(f"❌ 服务检查失败: {e}")
        return False

def get_installation_path():
    """查找PostgreSQL安装路径"""
    print("\n🔍 查找PostgreSQL安装路径...")
    
    possible_paths = [
        "C:/Program Files/PostgreSQL",
        "C:/Program Files (x86)/PostgreSQL",
        "D:/Program Files/PostgreSQL",
        "D:/Program Files (x86)/PostgreSQL",
    ]
    
    for path in possible_paths:
        try:
            import os
            if os.path.exists(path):
                print(f"✅ 找到PostgreSQL安装目录: {path}")
                # 列出子目录
                subdirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
                print(f"   版本目录: {subdirs}")
                return path
        except:
            continue
    
    print("❌ 未找到PostgreSQL安装目录")
    return None

if __name__ == "__main__":
    print("=" * 50)
    print("PostgreSQL安装和连接状态检查")
    print("=" * 50)
    
    # 检查服务状态
    service_running = check_windows_service()
    
    # 检查端口
    port_open = test_port()
    
    # 查找安装路径
    install_path = get_installation_path()
    
    print("\n" + "=" * 50)
    print("📋 检查结果总结:")
    print("=" * 50)
    
    if service_running and port_open:
        print("✅ PostgreSQL服务运行正常")
        print("\n下一步操作:")
        print("1. 使用pgAdmin创建数据库:")
        print("   a. 打开pgAdmin 4")
        print("   b. 连接到服务器 (密码: sql1024)")
        print("   c. 右键'Databases' -> 'Create' -> 'Database'")
        print("   d. 名称: toeic_app, Owner: postgres")
        print("   e. 点击'Save'")
        
        if install_path:
            print(f"\n2. PostgreSQL安装路径: {install_path}")
            print("   psql命令行工具路径可能为:")
            print(f"   {install_path}/版本号/bin/psql.exe")
            print("\n   添加到PATH后，可以使用命令行:")
            print('   psql -U postgres -c "CREATE DATABASE toeic_app;"')
    else:
        print("❌ PostgreSQL配置有问题")
        
        if not service_running:
            print("\n⚠️ PostgreSQL服务未运行")
            print("   启动命令: net start postgresql-x64-16")
            print("   或在Windows服务中启动PostgreSQL服务")
        
        if not port_open:
            print("\n⚠️ 端口5432未开放")
            print("   可能被防火墙阻止或服务未正确监听")
    
    print("\n" + "=" * 50)
    print("💡 快速创建数据库命令（如果psql可用）:")
    print('   psql -U postgres -c "CREATE DATABASE toeic_app;"')
    print("\n📝 密码提示: sql1024 (来自.env文件)")
    print("=" * 50)