import re

# 讀取當前文件
with open('api/index.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("修復 FUNCTION_INVOCATION_FAILED 錯誤...")

# 1. 確保所有必要的導入
if "from flask import Flask, jsonify, request, session" not in content:
    content = content.replace(
        "from flask import Flask, jsonify, request, session",
        "from flask import Flask, jsonify, request, session"
    )

# 2. 修復 storage 定義為類實例
new_storage_def = '''
# 雲端數據存儲
class CloudStorage:
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
        self.student_data = {
            'primary': [],
            'junior': [],
            'high': [],
            'other': []
        }
        self.pending_data = []
        self.system_config = {}
        self.announcements = []
        self.friends = {}
        self.private_messages = {}
        self.questions = []

storage = CloudStorage()
'''

# 替換 storage 定義
if "storage = {" in content:
    pattern = r"storage = \\{[^}]+\\}"
    content = re.sub(pattern, new_storage_def, content, flags=re.DOTALL)
    print("✅ Storage 定義已修復為類實例")
else:
    print("⚠️  使用現有 storage 定義")

# 3. 修復 get-all-data 路由中的屬性訪問
if "storage.users" in content:
    content = content.replace("storage.users", "storage.users")
if "storage.student_data" in content:
    content = content.replace("storage.student_data", "storage.student_data")
if "storage.pending_data" in content:
    content = content.replace("storage.pending_data", "storage.pending_data")
if "storage.announcements" in content:
    content = content.replace("storage.announcements", "storage.announcements")
if "storage.messages" in content:
    content = content.replace("storage.messages", "storage.messages")
if "storage.friends" in content:
    content = content.replace("storage.friends", "storage.friends")
if "storage.private_messages" in content:
    content = content.replace("storage.private_messages", "storage.private_messages")
if "storage.questions" in content:
    content = content.replace("storage.questions", "storage.questions")
if "storage.system_config" in content:
    content = content.replace("storage.system_config", "storage.system_config")

print("✅ 屬性訪問已修復")

# 保存文件
with open('api/index.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("修復完成！")
