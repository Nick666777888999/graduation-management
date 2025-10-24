import re

# 讀取當前後端
with open('api/index.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("重建後端確保正常工作...")

# 確保 storage 是類實例而不是字典
if "storage = {" in content:
    # 替換為類實例
    new_storage = '''
# 雲端數據存儲
class Storage:
    def __init__(self):
        self.users = {
            'Nick20130104': {
                'username': 'Nick20130104',
                'password': 'Nick20130104', 
                'name': '系統管理員',
                'school': '管理學校',
                'email': 'admin@system.com',
                'is_admin': True,
                'intro': '我是系統管理員'
            }
        }
        self.messages = []
        self.student_data = {'primary': [], 'junior': [], 'high': [], 'other': []}
        self.pending_data = []
        self.system_config = {}
        self.announcements = []
        self.friends = {}
        self.private_messages = {}
        self.questions = []

storage = Storage()
'''
    content = re.sub(r"storage = \\{[^}]+\\}", new_storage, content, flags=re.DOTALL)
    print("✅ Storage 已修復為類實例")

# 確保 register 路由正確
correct_register = '''@app.route('/api/register', methods=['POST'])
def register():
    """用戶註冊"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        school = data.get('school', '').strip()
        email = data.get('email', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        intro = data.get('intro', '').strip()

        # 檢查用戶是否已存在
        if username in storage.users:
            return jsonify({"success": False, "message": "此帳號已被使用"}), 400

        # 創建新用戶 - 保存所有數據包括密碼
        storage.users[username] = {
            'password': password,
            'name': name,
            'school': school,
            'email': email,
            'is_admin': False,
            'intro': intro
        }

        return jsonify({
            "success": True,
            "message": "註冊成功，請登入",
            "user": {"username": username, "name": name}
        })

    except Exception as e:
        return jsonify({
            "success": False, 
            "message": f"註冊失敗: {str(e)}"
        }), 500'''

# 替換 register 路由
if "@app.route('/api/register'" in content:
    pattern = r"@app.route\('/api/register'[^}]+}"
    content = re.sub(pattern, correct_register, content, flags=re.DOTALL)
    print("✅ Register 路由已完全修復")

with open('api/index.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("後端重建完成！")
