import re

with open('api/index.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("簡化 get-all-data 路由...")

# 創建簡單可靠的 get-all-data 路由
simple_get_all_data = '''@app.route('/api/get-all-data', methods=['GET'])
def get_all_data():
    """獲取所有雲端數據 - 簡化版本"""
    try:
        # 只返回用戶數據進行測試
        users_safe = {}
        for username, user in storage.users.items():
            users_safe[username] = {
                'name': user.get('name', ''),
                'school': user.get('school', ''),
                'email': user.get('email', ''),
                'is_admin': user.get('is_admin', False),
                'intro': user.get('intro', '')
            }

        return jsonify({
            "success": True,
            "data": {
                "users": users_safe,
                "student_data": {"primary": [], "junior": [], "high": [], "other": []},
                "pending_data": [],
                "announcements": [],
                "messages": [],
                "friends": {},
                "private_messages": {},
                "questions": [],
                "system_config": {}
            },
            "message": "數據獲取成功"
        })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return jsonify({
            "success": False,
            "message": "伺服器內部錯誤",
            "error": str(e)
        }), 500'''

# 替換 get-all-data 路由
if "@app.route('/api/get-all-data'" in content:
    pattern = r"@app.route\('/api/get-all-data'[^}]+}"
    content = re.sub(pattern, simple_get_all_data, content, flags=re.DOTALL)
    print("✅ get-all-data 路由已簡化")
else:
    print("❌ 找不到 get-all-data 路由")

with open('api/index.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("簡化完成！")
