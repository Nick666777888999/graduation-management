import os
import json
from flask import Flask, jsonify, request, session
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'graduation-system-secret-key-2024')
CORS(app, supports_credentials=True)

# 简单的内存存储
storage = {
    'users': {
        'Nick20130104': {
            'username': 'Nick20130104',
            'password': 'Nick20130104', 
            'name': '系统管理员',
            'school': '管理学校',
            'email': 'admin@system.com',
            'is_admin': True,
            'intro': '我是系统管理员'
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

# ==================== 基础 API ====================
@app.route('/')
def home():
    """系统信息"""
    return jsonify({
        "status": "success",
        "message": "毕业管理系统 API",
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
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "graduation-management-system",
        "timestamp": "2024-01-01T00:00:00Z"
    })

@app.route('/api/test')
def test():
    """测试 API"""
    return jsonify({
        "success": True,
        "message": "API 测试成功",
        "data": {"test": "ok"}
    })

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """检查登录状态"""
    return jsonify({
        "authenticated": False,
        "message": "请先登录",
        "user": None
    })

# ==================== 管理员 API ====================
@app.route('/api/admin/users', methods=['GET'])
def admin_users():
    """获取所有用户"""
    return jsonify({
        "success": True,
        "users": storage['users'],
        "count": len(storage['users']),
        "message": "用户数据获取成功"
    })

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    """系统统计"""
    return jsonify({
        "success": True,
        "stats": {
            "users_count": len(storage['users']),
            "messages_count": len(storage['messages']),
            "students_count": sum(len(v) for v in storage['student_data'].values()),
            "pending_count": len(storage['pending_data']),
            "announcements_count": len(storage['announcements'])
        },
        "message": "统计数据获取成功"
    })

@app.route('/api/admin/pending-approvals', methods=['GET'])
def admin_pending_approvals():
    """待审核数据"""
    return jsonify({
        "success": True,
        "pending": storage['pending_data'],
        "count": len(storage['pending_data']),
        "message": "待审核数据获取成功"
    })

@app.route('/api/admin/student-data', methods=['GET'])
def admin_student_data():
    """学生资料管理"""
    return jsonify({
        "success": True,
        "data": storage['student_data'],
        "total_count": sum(len(v) for v in storage['student_data'].values()),
        "message": "学生资料获取成功"
    })

@app.route('/api/admin/system-config', methods=['GET'])
def admin_system_config():
    """系统配置"""
    return jsonify({
        "success": True,
        "config": storage['system_config'],
        "message": "系统配置获取成功"
    })

# ==================== 同步功能 ====================
@app.route('/api/get-sync-data', methods=['GET'])
def get_sync_data():
    """获取同步数据"""
    return jsonify({
        "success": True,
        "data": {
            "users": storage['users'],
            "messages": storage['messages'],
            "student_data": storage['student_data'],
            "announcements": storage['announcements'],
            "system_config": storage['system_config']
        },
        "message": "同步数据获取成功"
    })

@app.route('/api/sync-data', methods=['POST'])
def sync_data():
    """同步数据"""
    try:
        data = request.get_json()
        return jsonify({
            "success": True,
            "message": "数据同步成功",
            "received_data": list(data.keys()) if data else []
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"同步失败: {str(e)}"
        }), 500

# ==================== 登录功能 ====================
@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
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
                "message": "登录成功",
                "user": {
                    "name": user['name'],
                    "isAdmin": user.get('is_admin', False),
                    "username": username
                }
            })
        else:
            return jsonify({
                "success": False,
                "message": "账号或密码错误"
            }), 401
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"登录失败: {str(e)}"
        }), 500

# ==================== Vercel 配置 ====================
# Vercel 需要这个
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)