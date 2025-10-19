import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
CORS(app, supports_credentials=True)

# 完整的數據存儲結構
storage = {
    'users': {
        'Nick20130104': {
            'username': 'Nick20130104',
            'password': 'Nick20130104',
            'name': '系統管理員',
            'school': '管理學校',
            'email': 'admin@system.com',
            'intro': '我是系統管理員',
            'is_admin': True
        }
    },
    'messages': [],
    'friends': {},
    'questions': [],
    'announcements': [],
    'student_data': {
        'primary': [],
        'junior': [],
        'high': [],
        'other': []
    },
    'system_config': {},
    'pending_data': []
}

# ==================== 基礎 API ====================
@app.route('/')
def home():
    return jsonify({'message': '畢業管理系統 API', 'status': 'running'})

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy'})

# ==================== 用戶系統 ====================
@app.route('/api/users', methods=['GET', 'POST'])
def users_api():
    if request.method == 'GET':
        return jsonify({'success': True, 'users': storage['users']})
    elif request.method == 'POST':
        data = request.json
        username = data.get('username')
        if username in storage['users']:
            return jsonify({'success': False, 'message': '用戶名已存在'}), 400
        storage['users'][username] = data
        return jsonify({'success': True, 'message': '用戶創建成功'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = storage['users'].get(username)
    if user and user.get('password') == password:
        session['username'] = username
        session['is_admin'] = user.get('is_admin', False)
        return jsonify({
            'success': True,
            'user': {
                'name': user.get('name'),
                'isAdmin': user.get('is_admin', False),
                'username': username
            }
        })
    return jsonify({'success': False, 'message': '帳號或密碼錯誤'}), 401

# ==================== 管理員功能 API ====================
@app.route('/api/admin/users')
def admin_users():
    return jsonify({'success': True, 'users': storage['users']})

@app.route('/api/admin/student-data')
def admin_student_data():
    return jsonify({'success': True, 'data': storage['student_data']})

@app.route('/api/admin/pending-approvals')
def admin_pending_approvals():
    return jsonify({'success': True, 'pending': storage['pending_data']})

@app.route('/api/admin/system-config', methods=['GET', 'POST'])
def admin_system_config():
    if request.method == 'GET':
        return jsonify({'success': True, 'config': storage['system_config']})
    elif request.method == 'POST':
        storage['system_config'].update(request.json)
        return jsonify({'success': True, 'message': '系統配置已更新'})

@app.route('/api/admin/approve-data/<data_id>', methods=['POST'])
def admin_approve_data(data_id):
    # 審核通過邏輯
    return jsonify({'success': True, 'message': '數據已審核通過'})

@app.route('/api/admin/reject-data/<data_id>', methods=['POST'])
def admin_reject_data(data_id):
    # 審核拒絕邏輯
    return jsonify({'success': True, 'message': '數據已拒絕'})

# ==================== 同步功能 ====================
@app.route('/api/sync-data', methods=['POST'])
def sync_data():
    try:
        data = request.json
        # 同步所有數據
        for key in ['users', 'messages', 'student_data', 'announcements', 'questions']:
            if key in data:
                if key == 'student_data' and isinstance(data[key], list):
                    # 處理學生數據格式轉換
                    pass
                else:
                    storage[key].update(data[key]) if isinstance(data[key], dict) else storage[key].extend(data[key])
        return jsonify({'success': True, 'message': '同步成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/get-sync-data', methods=['GET'])
def get_sync_data():
    return jsonify({
        'success': True,
        'users': storage['users'],
        'messages': storage['messages'],
        'student_data': storage['student_data'],
        'announcements': storage['announcements'],
        'questions': storage['questions']
    })

# ==================== Vercel 配置 ====================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
else:
    application = app
