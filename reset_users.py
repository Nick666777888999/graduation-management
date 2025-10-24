import requests
import json

# 测试用户数据
test_users = [
    {
        "name": "可靠测试用户",
        "school": "可靠学校",
        "email": "reliable@gmail.com",
        "username": "reliableuser",
        "password": "reliable123"
    },
    {
        "name": "测试用户A",
        "school": "测试学校A", 
        "email": "testa@gmail.com",
        "username": "testusera",
        "password": "test123"
    },
    {
        "name": "测试用户B",
        "school": "测试学校B",
        "email": "testb@gmail.com", 
        "username": "testuserb",
        "password": "test123"
    }
]

base_url = "https://graduation-management.vercel.app/api"

print("=== 重置测试用户 ===")

for user_data in test_users:
    username = user_data["username"]
    password = user_data["password"]
    
    print(f"\\n处理用户: {username}")
    
    # 先尝试注册
    try:
        response = requests.post(f"{base_url}/register", json=user_data)
        result = response.json()
        
        if result.get("success"):
            print(f"  ✅ 注册成功")
        else:
            print(f"  ⚠️ 注册失败: {result.get('message')}")
    except Exception as e:
        print(f"  ❌ 注册错误: {e}")
    
    # 测试登录
    try:
        response = requests.post(f"{base_url}/login", json={
            "username": username,
            "password": password
        })
        result = response.json()
        
        if result.get("success"):
            print(f"  ✅ 登录成功 - {result.get('user', {}).get('name')}")
        else:
            print(f"  ❌ 登录失败: {result.get('message')}")
    except Exception as e:
        print(f"  ❌ 登录错误: {e}")

print("\\n=== 重置完成 ===")
