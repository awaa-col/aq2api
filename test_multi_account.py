#!/usr/bin/env python3
"""
测试多账号轮询功能
Test multi-account polling functionality
"""

import json
import os
import sys
import tempfile

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_multi_account_manager():
    """测试多账号管理器"""
    from main import MultiAccountManager, CONFIG, AmazonQAuthManager
    
    # 创建临时凭证文件用于测试
    temp_dir = tempfile.mkdtemp()
    
    # 创建测试凭证
    test_credentials = [
        {
            "client_id": "test_client_1",
            "client_secret": "test_secret_1",
            "refresh_token": "test_refresh_1",
            "access_token": "test_access_1"
        },
        {
            "client_id": "test_client_2",
            "client_secret": "test_secret_2",
            "refresh_token": "test_refresh_2",
            "access_token": "test_access_2"
        },
        {
            "client_id": "test_client_3",
            "client_secret": "test_secret_3",
            "refresh_token": "test_refresh_3",
            "access_token": "test_access_3"
        }
    ]
    
    # 保存临时凭证文件
    temp_creds = []
    for idx, cred in enumerate(test_credentials):
        temp_file = os.path.join(temp_dir, f"test_cred_{idx}.json")
        with open(temp_file, 'w') as f:
            json.dump(cred, f, indent=2)
        temp_creds.append(temp_file)
    
    # 测试从配置加载多个账号
    original_config = CONFIG.get("accounts", [])
    CONFIG["accounts"] = temp_creds
    
    # 创建多账号管理器实例
    manager = MultiAccountManager()
    
    # 恢复原配置
    if original_config:
        CONFIG["accounts"] = original_config
    else:
        CONFIG.pop("accounts", None)
    
    # 验证账号数量
    assert manager.get_account_count() == 3, f"期望 3 个账号，实际 {manager.get_account_count()}"
    print(f"✓ 账号数量正确: {manager.get_account_count()}")
    
    # 测试轮询
    accounts_used = []
    for i in range(6):
        account = manager.get_next_account()
        accounts_used.append(account.account_index)
    
    # 验证轮询顺序
    expected = [0, 1, 2, 0, 1, 2]
    assert accounts_used == expected, f"期望轮询顺序 {expected}，实际 {accounts_used}"
    print(f"✓ 轮询顺序正确: {accounts_used}")
    
    # 验证每个账号的凭证
    for idx, account in enumerate(manager.accounts):
        assert account.credentials["client_id"] == f"test_client_{idx+1}", \
            f"账号 {idx} 的 client_id 不正确"
        assert account.access_token == f"test_access_{idx+1}", \
            f"账号 {idx} 的 access_token 不正确"
    print(f"✓ 所有账号凭证正确")
    
    # 清理临时文件
    for temp_file in temp_creds:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    os.rmdir(temp_dir)
    
    print("\n✓ 所有测试通过！")
    return True


def test_single_account_compatibility():
    """测试单账号兼容性"""
    from main import MultiAccountManager
    
    # 测试无配置时的行为
    manager = MultiAccountManager()
    
    # 如果存在默认凭证文件，应该能加载
    if os.path.exists("amazonq_credentials.json"):
        assert manager.get_account_count() >= 1, "应该至少加载一个账号"
        print(f"✓ 单账号兼容性测试通过，加载了 {manager.get_account_count()} 个账号")
    else:
        print("✓ 单账号兼容性测试通过（无默认凭证文件）")
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("多账号轮询功能测试")
    print("=" * 60)
    
    try:
        # 测试1: 多账号管理器
        print("\n测试 1: 多账号管理器")
        print("-" * 60)
        test_multi_account_manager()
        
        # 测试2: 单账号兼容性
        print("\n测试 2: 单账号兼容性")
        print("-" * 60)
        test_single_account_compatibility()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
