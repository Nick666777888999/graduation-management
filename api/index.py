import os
import json
from flask import Flask, jsonify, request, session
from flask_cors import CORS
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'graduation-system-secret-key-2024')
CORS(app, supports_credentials=True)

# 雲端數據存儲（模擬數據庫）
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
                'intro': '我是系統管理員',
                'anonymous': '管理員',
                'created_at': '2024-01-01T00:00:00Z'
            }
        }
        self.student_data = {
            'primary': [],
            'junior': [],
            'high': [],
            'other': []
        }
        self.pending_data = []
        self.announcements = []
        self.messages = []
        self.friends = {}
        self.private_messages = {}
        self.questions = []
        self.system_config = {}

    def save_all_data(self):
        """保存所有數據到持久化存儲"""
        # 在 Vercel 環境中，可以考慮使用外部存儲服務
        # 這裡使用環境變數或文件存儲（在 Vercel 中需要配置持久化）
        pass

storage = CloudStorage()

# ==================== 用戶管理 API ====================
@app.route('/api/register', methods=['POST'])
def register():
    """用戶註冊 - 雲端存儲"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        school = data.get('school', '').strip()
        email = data.get('email', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        intro = data.get('intro', '').strip()

        # 驗證數據
        if not all([name, school, email, username, password]):
            return jsonify({
                "success": False,
                "message": "請填寫所有必填欄位"
            }), 400

        if not email.endswith('@gmail.com'):
            return jsonify({
                "success": False,
                "message": "請使用 Gmail 信箱"
            }), 400

        if len(intro) < 50:
            return jsonify({
                "success": False,
                "message": "個人介紹至少需要50字"
            }), 400

        if username in storage.users:
            return jsonify({
                "success": False,
                "message": "此帳號已被使用"
            }), 400

        # 創建新用戶 - 存儲到雲端
        storage.users[username] = {
            'password': password,
            'name': name,
            'school': school,
            'email': email,
            'is_admin': False,
            'intro': intro,
            'anonymous': name,
            'avatar': None,
            'personality': '',
            'hobbies': '',
            'likes': '',
            'created_at': datetime.now().isoformat()
        }

        # 初始化用戶的好友數據
        storage.friends[username] = {
            'friends': [],
            'sent_requests': [],
            'received_requests': []
        }

        return jsonify({
            "success": True,
            "message": "註冊成功，請登入",
            "user": {
                "username": username,
                "name": name
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"註冊失敗: {str(e)}"
        }), 500

@app.route('/api/login', methods=['POST'])
def login():
    """用戶登入 - 從雲端驗證"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        # 從雲端存儲驗證用戶
        user = storage.users.get(username)
        
        if user and user['password'] == password:
            session['user'] = username
            session['is_admin'] = user.get('is_admin', False)
            
            return jsonify({
                "success": True,
                "message": "登入成功",
                "user": {
                    "name": user['name'],
                    "isAdmin": user.get('is_admin', False),
                    "username": username
                }
            })
        else:
            return jsonify({
                "success": False,
                "message": "帳號或密碼錯誤"
            }), 401

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"登入失敗: {str(e)}"
        }), 500

@app.route('/api/users', methods=['GET'])
def get_all_users():
    """獲取所有用戶列表（用於好友系統）"""
    try:
        # 只返回基本信息，不包含密碼
        users_info = {}
        for username, user in storage.users.items():
            users_info[username] = {
                'name': user['name'],
                'school': user['school'],
                'email': user['email'],
                'intro': user['intro'],
                'avatar': user.get('avatar'),
                'is_admin': user.get('is_admin', False)
            }

        return jsonify({
            "success": True,
            "users": users_info,
            "count": len(users_info),
            "message": "用戶數據獲取成功"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"獲取用戶失敗: {str(e)}"
        }), 500

# ==================== 數據同步 API ====================
@app.route('/api/sync-all-data', methods=['POST'])
def sync_all_data():
    """同步所有數據到雲端"""
    try:
        data = request.get_json()
        
        # 同步用戶數據
        if 'users' in data:
            for username, user_data in data['users'].items():
                if username not in storage.users:
                    storage.users[username] = user_data

        # 同步聊天消息
        if 'messages' in data:
            storage.messages = data['messages']

        # 同步好友數據
        if 'friends' in data:
            for username, friend_data in data['friends'].items():
                storage.friends[username] = friend_data

        # 同步問題數據
        if 'questions' in data:
            storage.questions = data['questions']

        return jsonify({
            "success": True,
            "message": "數據同步成功",
            "synced_items": list(data.keys())
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"同步失敗: {str(e)}"
        }), 500

@app.route('/api/get-all-data', methods=['GET'])
def get_all_data():
    """獲取所有雲端數據"""
    try:
        # 不返回密碼
        users_safe = {}
        for username, user in storage.users.items():
            user_copy = user.copy()
            user_copy.pop('password', None)
            users_safe[username] = user_copy

        return jsonify({
            "success": True,
            "data": {
                "users": users_safe,
                "student_data": storage.student_data,
                "pending_data": storage.pending_data,
                "announcements": storage.announcements,
                "messages": storage.messages,
                "friends": storage.friends,
                "private_messages": storage.private_messages,
                "questions": storage.questions,
                "system_config": storage.system_config
            },
            "message": "數據獲取成功"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"獲取數據失敗: {str(e)}"
        }), 500

# ==================== 現有 API 保持不變 ====================
@app.route('/')
def home():
    """系統信息"""
    return jsonify({
        "status": "success",
        "message": "畢業管理系統 API - 雲端版本",
        "version": "2.0.0",
        "features": {
            "cloud_storage": True,
            "multi_device": True,
            "user_registration": True
        },
        "endpoints": {
            "register": "/api/register",
            "login": "/api/login", 
            "users": "/api/users",
            "sync": "/api/sync-all-data",
            "get_data": "/api/get-all-data"
        }
    })

# ... 保持其他現有 API 不變 ...

# ==================== Vercel 配置 ====================
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)