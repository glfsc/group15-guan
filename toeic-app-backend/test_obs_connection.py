#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

def test_obs_config():
    """测试OBS配置"""
    print("🔍 检查OBS配置...")
    
    # 加载环境变量
    load_dotenv()
    
    # 获取配置
    obs_ak = os.getenv('OBS_AK')
    obs_sk = os.getenv('OBS_SK')
    bucket_name = os.getenv('OBS_BUCKET')
    region = os.getenv('OBS_REGION')
    endpoint = os.getenv('OBS_ENDPOINT')
    
    print(f"OBS配置信息:")
    print(f"  AK: {obs_ak[:4]}...{obs_ak[-4:] if obs_ak else 'None'}")
    print(f"  SK: {obs_sk[:4]}...{obs_sk[-4:] if obs_sk else 'None'}")
    print(f"  桶名: {bucket_name}")
    print(f"  区域: {region}")
    print(f"  端点: {endpoint}")
    
    # 检查配置
    if not obs_ak or not obs_sk:
        print("❌ AK或SK未配置")
        return False
    
    if obs_ak == 'your_access_key' or obs_sk == 'your_secret_key':
        print("❌ 请替换默认的AK/SK值")
        return False
    
    if not bucket_name:
        print("❌ 桶名未配置")
        return False
    
    if not region:
        print("❌ 区域未配置")
        return False
    
    print("✅ OBS配置检查通过")
    return True

def test_obs_connection():
    """测试OBS连接"""
    print("\n🔍 测试OBS连接...")
    
    try:
        # 尝试导入华为云OBS SDK
        from huaweicloudsdkcore.auth.credentials import BasicCredentials
        from huaweicloudsdkobs.obs_client import ObsClient
        
        # 加载环境变量
        load_dotenv()
        
        # 获取配置
        obs_ak = os.getenv('OBS_AK')
        obs_sk = os.getenv('OBS_SK')
        endpoint = os.getenv('OBS_ENDPOINT', 'https://obs.cn-north-4.myhuaweicloud.com')
        bucket_name = os.getenv('OBS_BUCKET', 'toeic-audio-files')
        
        # 创建凭证
        credentials = BasicCredentials(obs_ak, obs_sk)
        
        # 创建OBS客户端
        obs_client = ObsClient(credentials=credentials, endpoint=endpoint)
        
        # 测试连接 - 获取桶信息
        try:
            print(f"连接OBS服务: {endpoint}")
            print(f"测试桶: {bucket_name}")
            
            # 尝试列出桶
            resp = obs_client.listBuckets()
            buckets = resp.body.buckets if hasattr(resp.body, 'buckets') else []
            
            print(f"✅ OBS连接成功!")
            print(f"  可访问桶数量: {len(buckets)}")
            
            # 检查目标桶是否存在
            bucket_exists = False
            for bucket in buckets:
                if bucket.name == bucket_name:
                    bucket_exists = True
                    print(f"✅ 找到目标桶: {bucket_name}")
                    print(f"  创建时间: {bucket.creation_date}")
                    break
            
            if not bucket_exists:
                print(f"⚠️  目标桶 '{bucket_name}' 不存在")
                print("  请在华为云控制台创建此桶")
                
                # 尝试创建桶
                try:
                    print(f"尝试创建桶 '{bucket_name}'...")
                    create_resp = obs_client.createBucket(bucket_name)
                    print(f"✅ 桶 '{bucket_name}' 创建成功")
                    bucket_exists = True
                except Exception as create_error:
                    print(f"❌ 创建桶失败: {create_error}")
                    print("  请检查权限或手动创建桶")
            
            return True
            
        except Exception as e:
            print(f"❌ OBS连接失败: {e}")
            print("\n可能的原因:")
            print("1. AK/SK不正确")
            print("2. 网络连接问题")
            print("3. 区域配置错误")
            print("4. 权限不足")
            return False
            
    except ImportError:
        print("❌ huaweicloudsdkcore或huaweicloudsdkobs未安装")
        print("安装命令: pip install huaweicloudsdkcore huaweicloudsdkobs")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def main():
    print("=" * 60)
    print("华为云OBS连接测试")
    print("=" * 60)
    
    # 检查配置
    config_ok = test_obs_config()
    
    if config_ok:
        # 测试连接
        connection_ok = test_obs_connection()
        
        print("\n" + "=" * 60)
        print("📊 测试结果:")
        print("=" * 60)
        
        if connection_ok:
            print("✅ OBS配置和连接全部通过!")
            print("\n🎉 OBS服务已准备好接收音频文件")
            print("\n使用方法:")
            print("1. 前端上传音频文件到OBS桶")
            print("2. 后端生成预签名URL供前端访问")
            print("3. AI服务处理音频内容")
        else:
            print("❌ OBS连接测试失败")
            print("\n请检查:")
            print("1. AK/SK是否正确")
            print("2. OBS桶是否已创建")
            print("3. 网络连接是否正常")
    else:
        print("\n❌ 配置检查失败，请更新.env文件")

if __name__ == "__main__":
    main()