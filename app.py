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

# 使用內存存儲
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
    'friends': [],
    'questions': [],
    'announcements': [],
    'student_data': []
}

# ==================== 基礎 API ====================
@app.route('/')
def home():
    return jsonify({
        'message': '畢業管理系統 API',
        'version': '1.0.0',
        'status': 'running'
    })

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/test')
def test_api():
    return jsonify({'success': True, 'message': 'API 測試成功'})

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
        
        storage['users'][username] = {
            'username': username,
            'password': data.get('password'),
            'name': data.get('name'),
            'school': data.get('school'),
            'email': data.get('email'),
            'intro': data.get('intro'),
            'is_admin': False
        }
        
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

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    if 'username' in session:
        user = storage['users'].get(session['username'])
        return jsonify({
            'authenticated': True,
            'user': {
                'name': user.get('name'),
                'isAdmin': user.get('is_admin', False),
                'username': session['username']
            }
        })
    return jsonify({'authenticated': False})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

# ==================== 聊天系統 ====================
@app.route('/api/messages', methods=['GET', 'POST'])
def messages_api():
    if request.method == 'GET':
        return jsonify({'success': True, 'messages': storage['messages']})
    
    elif request.method == 'POST':
        data = request.json
        message_id = str(uuid.uuid4())
        
        storage['messages'].append({
            'id': message_id,
            'sender': data.get('sender'),
            'text': data.get('text'),
            'sender_name': data.get('sender_name'),
            'is_admin': data.get('is_admin', False),
            'time': datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        })
        
        # 只保留最近100條訊息
        storage['messages'] = storage['messages'][-100:]
        
        return jsonify({'success': True})

# ==================== 同步系統 ====================
@app.route('/api/sync-data', methods=['POST'])
def sync_data():
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': '沒有收到數據'}), 400
        
        # 同步用戶數據
        if 'users' in data:
            storage['users'].update(data['users'])
        
        # 同步聊天訊息
        if 'messages' in data:
            storage['messages'] = data['messages'][-100:]
        
        return jsonify({
            'success': True, 
            'message': f'同步成功 - 用戶: {len(storage["users"])}, 訊息: {len(storage["messages"])}'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'同步失敗: {str(e)}'}), 500

@app.route('/api/get-sync-data', methods=['GET'])
def get_sync_data():
    return jsonify({
        'success': True,
        'users': storage['users'],
        'messages': storage['messages'][-50:],
        'stats': {
            'users_count': len(storage['users']),
            'messages_count': len(storage['messages'])
        }
    })

# ==================== 管理員功能 ====================
@app.route('/api/admin/users')
def admin_users():
    """獲取所有用戶資料"""
    return jsonify({
        'success': True,
        'users': storage['users'],
        'total_count': len(storage['users'])
    })

@app.route('/api/admin/messages')
def admin_messages():
    """獲取所有聊天訊息"""
    return jsonify({
        'success': True,
        'messages': storage['messages'],
        'total_count': len(storage['messages'])
    })

@app.route('/api/admin/stats')
def admin_stats():
    """系統統計數據"""
    return jsonify({
        'success': True,
        'stats': {
            'users_count': len(storage['users']),
            'messages_count': len(storage['messages']),
            'active_users': list(storage['users'].keys())[-10:],
            'recent_messages': storage['messages'][-10:]
        }
    })

# ==================== Vercel 配置 ====================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
else:
    application = app

# ==================== 管理員功能 ====================
@app.route('/api/admin/users')
def admin_users():
    """獲取所有用戶資料"""
    return jsonify({
        'success': True,
        'users': storage['users'],
        'total_count': len(storage['users'])
    })

@app.route('/api/admin/messages')
def admin_messages():
    """獲取所有聊天訊息"""
    return jsonify({
        'success': True,
        'messages': storage['messages'],
        'total_count': len(storage['messages'])
    })

@app.route('/api/admin/stats')
def admin_stats():
    """系統統計數據"""
    return jsonify({
        'success': True,
        'stats': {
            'users_count': len(storage['users']),
            'messages_count': len(storage['messages']),
            'active_users': list(storage['users'].keys())[-10:],
            'recent_messages': storage['messages'][-10:]
        }
    })
