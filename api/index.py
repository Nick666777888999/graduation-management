import os
import json
from flask import Flask, jsonify, request, session
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'graduation-system-secret-key-2024')
CORS(app, supports_credentials=True)

# 簡單的內存存儲
storage = {
    'users': {
        'Nick20130104': {
            'username': 'Nick20130104',
            'password': 'Nick20130104', 
            'name': '系統管理員',
            'school': '管理學校',
            'email': 'admin@system.com',
            'is_admin': True,
            'intro': '我是系統管理員'
        }
    },
    'messages': [],
    'student_data': {
        'primary': [],
        'junior': [],
        'high': [],
        'other': []
    },
    'pending_data': [],
    'system_config': {},
    'announcements': []
}

# ==================== 基礎 API ====================
@app.route('/')
def home():
    """系統信息"""
    return jsonify({
        "status": "success",
        "message": "畢業管理系統 API",
        "version": "2.0.0",
        "endpoints": {
            "health": "/api/health",
            "test": "/api/test", 
            "auth": "/api/check-auth",
            "admin": {
                "users": "/api/admin/users",
                "stats": "/api/admin/stats",
                "pending": "/api/admin/pending-approvals",
                "students": "/api/admin/student-data",
                "config": "/api/admin/system-config"
            },
            "sync": "/api/get-sync-data"
        }
    })

@app.route('/api/health')
def health():
    """健康檢查"""
    return jsonify({
        "status": "healthy",
        "service": "graduation-management-system",
        "timestamp": "2024-01-01T00:00:00Z"
    })

@app.route('/api/test')
def test():
    """測試 API"""
    return jsonify({
        "success": True,
        "message": "API 測試成功",
        "data": {"test": "ok"}
    })

@app.route('/api/check-auth', methods=['GET', 'POST'])
def check_auth():
    """檢查登入狀態"""
    return jsonify({
        "authenticated": False,
        "message": "請先登入",
        "user": None
    })

# ==================== 管理員 API ====================
@app.route('/api/admin/users', methods=['GET'])
def admin_users():
    """獲取所有用戶"""
    return jsonify({
        "success": True,
        "users": storage['users'],
        "count": len(storage['users']),
        "message": "用戶數據獲取成功"
    })

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    """系統統計"""
    return jsonify({
        "success": True,
        "stats": {
            "users_count": len(storage['users']),
            "messages_count": len(storage['messages']),
            "students_count": sum(len(v) for v in storage['student_data'].values()),
            "pending_count": len(storage['pending_data']),
            "announcements_count": len(storage['announcements'])
        },
        "message": "統計數據獲取成功"
    })

@app.route('/api/admin/pending-approvals', methods=['GET'])
def admin_pending_approvals():
    """待審核數據"""
    return jsonify({
        "success": True,
        "pending": storage['pending_data'],
        "count": len(storage['pending_data']),
        "message": "待審核數據獲取成功"
    })

@app.route('/api/admin/student-data', methods=['GET'])
def admin_student_data():
    """學生資料管理"""
    return jsonify({
        "success": True,
        "data": storage['student_data'],
        "total_count": sum(len(v) for v in storage['student_data'].values()),
        "message": "學生資料獲取成功"
    })

@app.route('/api/admin/system-config', methods=['GET'])
def admin_system_config():
    """系統配置"""
    return jsonify({
        "success": True,
        "config": storage['system_config'],
        "message": "系統配置獲取成功"
    })

# ==================== 同步功能 ====================
@app.route('/api/get-sync-data', methods=['GET', 'POST'])
def get_sync_data():
    """獲取同步數據"""
    return jsonify({
        "success": True,
        "data": {
            "users": storage['users'],
            "messages": storage['messages'],
            "student_data": storage['student_data'],
            "announcements": storage['announcements'],
            "system_config": storage['system_config']
        },
        "message": "同步數據獲取成功"
    })

@app.route('/api/sync-data', methods=['GET', 'POST'])
def sync_data():
    """同步數據"""
    if request.method == 'GET':
        return jsonify({
            "success": True,
            "message": "同步API準備就緒",
            "method": "支持 GET 和 POST 請求",
            "usage": "使用 POST 方法提交同步數據"
        })
    
    try:
        data = request.get_json()
        return jsonify({
            "success": True,
            "message": "數據同步成功",
            "received_data": list(data.keys()) if data else []
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"同步失敗: {str(e)}"
        }), 500

# ==================== 登入功能 ====================
@app.route('/api/login', methods=['GET', 'POST'])
def login():
    """用戶登入"""
    if request.method == 'GET':
        return jsonify({
            "success": False,
            "message": "請使用 POST 方法提交登入資料",
            "example": {
                "username": "您的帳號",
                "password": "您的密碼"
            },
            "test_account": {
                "username": "Nick20130104",
                "password": "Nick20130104"
            }
        })
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = storage['users'].get(username)
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

# ==================== 新增測試用戶 API ====================
@app.route('/api/test-users', methods=['GET'])
def test_users():
    """獲取測試用戶資訊"""
    return jsonify({
        "success": True,
        "test_accounts": {
            "admin": {
                "username": "Nick20130104",
                "password": "Nick20130104",
                "name": "系統管理員"
            }
        },
        "message": "測試帳號資訊"
    })

# ==================== Vercel 配置 ====================
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)