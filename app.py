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
    'friend_requests': [],
    'questions': [],
    'question_likes': [],
    'question_comments': [],
    'announcements': [],
    'student_data': {
        'primary': [],
        'junior': [],
        'high': [],
        'other': []
    },
    'pending_data': [],
    'private_messages': {},
    'system_config': {}
}

# ==================== 基礎 API ====================
@app.route('/')
def home():
    return jsonify({'message': '畢業管理系統 API', 'status': 'running'})

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
        return jsonify({'success': True, 'messages': storage['messages'][-100:]})
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
        
        # 只保留最近200條訊息
        storage['messages'] = storage['messages'][-200:]
        return jsonify({'success': True})

# ==================== 好友系統 ====================
@app.route('/api/friends', methods=['GET', 'POST'])
def friends_api():
    username = session.get('username')
    if not username:
        return jsonify({'success': False, 'message': '未登入'}), 401
    
    if request.method == 'GET':
        user_friends = storage['friends'].get(username, [])
        user_requests = [r for r in storage['friend_requests'] if r['to_user'] == username and r['status'] == 'pending']
        return jsonify({
            'success': True,
            'friends': user_friends,
            'requests': user_requests
        })
    
    elif request.method == 'POST':
        data = request.json
        target_user = data.get('username')
        
        # 發送好友申請
        storage['friend_requests'].append({
            'id': str(uuid.uuid4()),
            'from_user': username,
            'to_user': target_user,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        })
        return jsonify({'success': True, 'message': '好友申請已發送'})

# ==================== 問題討論系統 ====================
@app.route('/api/questions', methods=['GET', 'POST'])
def questions_api():
    if request.method == 'GET':
        return jsonify({'success': True, 'questions': storage['questions']})
    elif request.method == 'POST':
        data = request.json
        question_id = str(uuid.uuid4())
        
        storage['questions'].append({
            'id': question_id,
            'text': data.get('text'),
            'subject': data.get('subject'),
            'grade': data.get('grade'),
            'author': data.get('author'),
            'author_name': data.get('author_name'),
            'likes': 0,
            'created_at': datetime.now().isoformat()
        })
        return jsonify({'success': True})

# ==================== 學生資料系統 ====================
@app.route('/api/student-data', methods=['GET', 'POST'])
def student_data_api():
    if request.method == 'GET':
        level = request.args.get('level', 'all')
        if level == 'all':
            all_data = []
            for key in ['primary', 'junior', 'high', 'other']:
                all_data.extend(storage['student_data'][key])
            return jsonify({'success': True, 'data': all_data})
        else:
            return jsonify({'success': True, 'data': storage['student_data'].get(level, [])})
    
    elif request.method == 'POST':
        data = request.json
        level = data.get('level', 'other')
        
        student_record = {
            'id': str(uuid.uuid4()),
            'name': data.get('name'),
            'school': data.get('school'),
            'grade': data.get('grade'),
            'level': level,
            'personality': data.get('personality'),
            'hobbies': data.get('hobbies'),
            'likes': data.get('likes'),
            'intro': data.get('intro'),
            'submitted_by': data.get('submitted_by'),
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        storage['student_data'][level].append(student_record)
        return jsonify({'success': True, 'message': '學生資料已提交'})

# ==================== 公告系統 ====================
@app.route('/api/announcements', methods=['GET', 'POST'])
def announcements_api():
    if request.method == 'GET':
        return jsonify({'success': True, 'announcements': storage['announcements']})
    elif request.method == 'POST':
        if not session.get('is_admin'):
            return jsonify({'success': False, 'message': '權限不足'}), 403
        
        data = request.json
        announcement_id = str(uuid.uuid4())
        
        storage['announcements'].append({
            'id': announcement_id,
            'title': data.get('title'),
            'content': data.get('content'),
            'author': session['username'],
            'author_name': data.get('author_name'),
            'created_at': datetime.now().isoformat()
        })
        return jsonify({'success': True})

# ==================== 管理員功能 API ====================
@app.route('/api/admin/users')
def admin_users():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '權限不足'}), 403
    return jsonify({'success': True, 'users': storage['users']})

@app.route('/api/admin/student-data')
def admin_student_data():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '權限不足'}), 403
    return jsonify({'success': True, 'data': storage['student_data']})

@app.route('/api/admin/pending-approvals')
def admin_pending_approvals():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '權限不足'}), 403
    
    pending_data = []
    for level in ['primary', 'junior', 'high', 'other']:
        for item in storage['student_data'][level]:
            if item.get('status') == 'pending':
                pending_data.append(item)
    
    return jsonify({'success': True, 'pending': pending_data})

@app.route('/api/admin/approve-data/<data_id>', methods=['POST'])
def admin_approve_data(data_id):
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '權限不足'}), 403
    
    # 在所有學制中尋找並審核數據
    for level in ['primary', 'junior', 'high', 'other']:
        for item in storage['student_data'][level]:
            if item['id'] == data_id:
                item['status'] = 'approved'
                return jsonify({'success': True, 'message': '數據已審核通過'})
    
    return jsonify({'success': False, 'message': '未找到數據'}), 404

@app.route('/api/admin/system-config', methods=['GET', 'POST'])
def admin_system_config():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '權限不足'}), 403
    
    if request.method == 'GET':
        return jsonify({'success': True, 'config': storage['system_config']})
    elif request.method == 'POST':
        storage['system_config'].update(request.json)
        return jsonify({'success': True, 'message': '系統配置已更新'})

@app.route('/api/admin/stats')
def admin_stats():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '權限不足'}), 403
    
    return jsonify({
        'success': True,
        'stats': {
            'users_count': len(storage['users']),
            'messages_count': len(storage['messages']),
            'questions_count': len(storage['questions']),
            'announcements_count': len(storage['announcements']),
            'pending_approvals': len([item for level in storage['student_data'].values() for item in level if item.get('status') == 'pending'])
        }
    })

# ==================== 同步功能 ====================
@app.route('/api/sync-data', methods=['POST'])
def sync_data():
    try:
        data = request.json
        
        # 同步用戶數據
        if 'users' in data:
            storage['users'].update(data['users'])
        
        # 同步聊天訊息
        if 'messages' in data:
            storage['messages'] = data['messages'][-200:]
        
        return jsonify({'success': True, 'message': '同步成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/get-sync-data', methods=['GET'])
def get_sync_data():
    return jsonify({
        'success': True,
        'users': storage['users'],
        'messages': storage['messages'][-50:],
        'student_data': storage['student_data'],
        'announcements': storage['announcements'],
        'questions': storage['questions']
    })

# ==================== Vercel 配置 ====================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
else:
    application = app
