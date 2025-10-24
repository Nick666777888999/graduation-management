from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# 预置用户数据 - 直接在代码中定义
PRESET_USERS = {
    'Nick20130104': {
        'name': '系統管理員',
        'school': '管理學校', 
        'email': 'admin@system.com',
        'password': 'Nick20130104',
        'is_admin': True,
        'intro': '我是系統管理員'
    },
    'reliableuser': {
        'name': '可靠测试用户',
        'school': '可靠学校',
        'email': 'reliable@gmail.com', 
        'password': 'reliable123',
        'is_admin': False,
        'intro': '可靠测试用户账号'
    },
    'testusera': {
        'name': '测试用户A',
        'school': '测试学校A',
        'email': 'testa@gmail.com',
        'password': 'test123', 
        'is_admin': False,
        'intro': '测试用户A账号'
    },
    'testuserb': {
        'name': '测试用户B', 
        'school': '测试学校B',
        'email': 'testb@gmail.com',
        'password': 'test123',
        'is_admin': False,
        'intro': '测试用户B账号'
    }
}

# 内存数据存储
class PresetStorage:
    def __init__(self):
        self.data = {
            'users': PRESET_USERS.copy(),
            'student_data': {
                'primary': [],
                'junior': [], 
                'high': [],
                'other': []
            },
            'pending_data': [],
            'announcements': [],
            'chat_messages': [],
            'questions': [],
            'friends': {},
            'private_messages': {}
        }
    
    def get_data(self):
        return self.data
    
    def save_data(self, new_data):
        self.data = new_data
        return True

storage = PresetStorage()

@app.route('/api/health')
def health():
    return jsonify({'service': 'graduation-management-system', 'status': 'healthy'})

@app.route('/api/get-all-data')
def get_all_data():
    data = storage.get_data()
    return jsonify({'success': True, 'data': data})

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        school = data.get('school', '').strip()
        email = data.get('email', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not all([name, school, email, username, password]):
            return jsonify({'success': False, 'message': '所有欄位都是必填的'})

        all_data = storage.get_data()
        users = all_data.get('users', {})

        if username in users:
            return jsonify({'success': False, 'message': '用戶名已存在'})

        # 创建新用户
        users[username] = {
            'name': name,
            'school': school,
            'email': email,
            'password': password,
            'is_admin': False,
            'intro': '系統用戶',
            'created_at': datetime.now().isoformat()
        }

        all_data['users'] = users
        storage.save_data(all_data)

        return jsonify({
            'success': True,
            'message': '註冊成功', 
            'user': {'name': name, 'username': username}
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'註冊失敗: {str(e)}'})

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({'success': False, 'message': '請輸入帳號和密碼'})

        all_data = storage.get_data()
        users = all_data.get('users', {})

        if username not in users:
            return jsonify({'success': False, 'message': '帳號或密碼錯誤'})

        user = users[username]
        stored_password = user.get('password')

        if not stored_password or stored_password != password:
            return jsonify({'success': False, 'message': '帳號或密碼錯誤'})

        return jsonify({
            'success': True,
            'message': '登入成功',
            'user': {
                'name': user['name'],
                'username': username,
                'isAdmin': user.get('is_admin', False)
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'登入失敗: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
