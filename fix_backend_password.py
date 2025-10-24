import requests
import json

def test_password_issue():
    """测试密码问题"""
    base_url = "https://graduation-management.vercel.app/api"
    
    # 测试用户
    test_user = {
        "name": "密码测试用户",
        "school": "测试学校",
        "email": "passwordtest@gmail.com", 
        "username": "passwordtest",
        "password": "password123"
    }
    
    print("=== 测试密码问题 ===")
    
    # 注册用户
    print("1. 注册用户...")
    response = requests.post(f"{base_url}/register", json=test_user)
    result = response.json()
    print(f"   注册结果: {result}")
    
    # 立即登录测试
    print("2. 立即登录测试...")
    response = requests.post(f"{base_url}/login", json={
        "username": "passwordtest",
        "password": "password123"
    })
    result = response.json()
    print(f"   登录结果: {result}")
    
    # 检查用户数据
    print("3. 检查用户数据...")
    response = requests.get(f"{base_url}/get-all-data")
    data = response.json()
    users = data.get('data', {}).get('users', {})
    
    if "passwordtest" in users:
        user_data = users["passwordtest"]
        print(f"   用户数据: {user_data}")
        print(f"   密码字段: {user_data.get('password', '未找到')}")
    else:
        print("   用户未找到")

if __name__ == "__main__":
    test_password_issue()
