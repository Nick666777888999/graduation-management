import re

with open('api/index.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("修復註冊路由的密碼保存...")

# 修復 register 路由，確保保存密碼
new_register = '''@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if username in storage.users:
            return jsonify({"success": False, "message": "用戶已存在"}), 400
            
        # 重要：保存所有用戶數據，包括密碼
        storage.users[username] = {
            'password': data.get('password', ''),  # 保存密碼
            'name': data.get('name', ''),
            'school': data.get('school', ''),
            'email': data.get('email', ''),
            'is_admin': False,
            'intro': data.get('intro', '')
        }
        
        return jsonify({"success": True, "message": "註冊成功"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500'''

# 替換 register 路由
if "@app.route('/api/register'" in content:
    pattern = r"@app.route\('/api/register'[^}]+}"
    content = re.sub(pattern, new_register, content, flags=re.DOTALL)
    print("✅ 註冊路由已修復，現在會保存密碼")
else:
    print("❌ 找不到 register 路由")

with open('api/index.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("密碼保存修復完成！")
