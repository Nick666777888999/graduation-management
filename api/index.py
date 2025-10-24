from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# 内存数据存储
class MemoryStorage:
    def __init__(self):
        self.data = {
            'users': {
                'Nick20130104': {
                    'name': '系統管理員',
                    'school': '管理學校',
                    'email': 'admin@system.com',
                    'password': 'Nick20130104',
                    'is_admin': True,
                    'intro': '我是系統管理員'
                }
            },
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

# 全局存储实例
storage = MemoryStorage()

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

        # 验证必需字段
        if not all([name, school, email, username, password]):
            return jsonify({'success': False, 'message': '所有欄位都是必填的'})

        # 获取现有数据
        all_data = storage.get_data()
        users = all_data.get('users', {})

        # 检查用户名是否已存在
        if username in users:
            return jsonify({'success': False, 'message': '用戶名已存在'})

        # 创建新用户 - 确保密码保存
        users[username] = {
            'name': name,
            'school': school,
            'email': email,
            'password': password,  # 明确保存密码
            'is_admin': False,
            'intro': '這是系統用戶',
            'created_at': datetime.now().isoformat()
        }

        # 保存数据
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

        # 获取数据
        all_data = storage.get_data()
        users = all_data.get('users', {})

        # 检查用户是否存在
        if username not in users:
            return jsonify({'success': False, 'message': '帳號或密碼錯誤'})

        user = users[username]

        # 检查密码 - 使用明确的密码字段
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
