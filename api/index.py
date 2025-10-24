import os
import json
from flask import Flask, jsonify, request, session
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'graduation-system-secret-key-2024')
CORS(app, supports_credentials=True)

# 簡單的數據存儲
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

# ==================== 基礎 API ====================
@app.route('/')
def home():
    return jsonify({
        "status": "success", 
        "message": "畢業管理系統 API",
        "version": "2.0.0"
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "graduation-management-system"
    })

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        "success": True,
        "message": "API 測試成功"
    })

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    return jsonify({
        "authenticated": False,
        "message": "請先登入"
    })

# ==================== 用戶管理 API ====================
@app.route('/api/register', methods=['POST'])
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
        return jsonify({"success": False, "message": str(e)}), 500), 400
            
        storage.users[username] = {
            'password': data.get('password', ''),
            'name': data.get('name', ''),
            'school': data.get('school', ''),
            'email': data.get('email', ''),
            'is_admin': False,
            'intro': data.get('intro', '')
        }
        
        return jsonify({"success": True, "message": "註冊成功"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        user = storage.users.get(username)
        if user and user['password'] == password:
            session['user'] = username
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
            return jsonify({"success": False, "message": "帳號或密碼錯誤"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    users_safe = {}
    for username, user in storage.users.items():
        users_safe[username] = {
            'name': user['name'],
            'school': user['school'],
            'email': user['email'],
            'is_admin': user.get('is_admin', False)
        }
    return jsonify({"success": True, "users": users_safe})

# ==================== 雲端同步 API ====================
@app.route('/api/get-all-data', methods=['GET'])
def get_all_data():
    """獲取所有數據 - 簡單可靠版本"""
    try:
        # 安全地構建用戶數據（不包含密碼）
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
            "message": f"數據獲取失敗: {str(e)}"
        }), 500

@app.route('/api/sync-all-data', methods=['POST'])
def sync_all_data():
    try:
        data = request.get_json()
        return jsonify({
            "success": True,
            "message": "同步成功",
            "received_data": list(data.keys()) if data else []
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== 管理員 API ====================
@app.route('/api/admin/users', methods=['GET'])
def admin_users():
    users_safe = {}
    for username, user in storage.users.items():
        user_copy = user.copy()
        user_copy.pop('password', None)
        users_safe[username] = user_copy
    return jsonify({"success": True, "users": users_safe})

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    total_students = sum(len(v) for v in storage.student_data.values())
    return jsonify({
        "success": True,
        "stats": {
            "users_count": len(storage.users),
            "messages_count": len(storage.messages),
            "students_count": total_students,
            "pending_count": len(storage.pending_data),
            "announcements_count": len(storage.announcements)
        }
    })

@app.route('/api/admin/pending-approvals', methods=['GET'])
def admin_pending_approvals():
    return jsonify({"success": True, "pending": storage.pending_data})

@app.route('/api/admin/student-data', methods=['GET'])
def admin_student_data():
    return jsonify({"success": True, "data": storage.student_data})

@app.route('/api/admin/system-config', methods=['GET'])
def admin_system_config():
    return jsonify({"success": True, "config": storage.system_config})

# Vercel 需要
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
