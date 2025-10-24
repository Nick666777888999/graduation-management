from flask import Flask, request, jsonify
import json
import os
import requests
from datetime import datetime

app = Flask(__name__)

# 使用外部JSON存储作为模拟数据库
DB_URL = "https://api.jsonbin.io/v3/b/65b5a5e7266cfc3fde8c3a0f"  # 需要替换为实际JSONBin ID
API_KEY = "$2a$10$YOUR_API_KEY"  # 需要实际API Key

# 预置用户（保底）
PRESET_USERS = {
    'Nick20130104': {'name': '系統管理員', 'password': 'Nick20130104', 'is_admin': True},
    'reliableuser': {'name': '可靠测试用户', 'password': 'reliable123', 'is_admin': False},
    'testusera': {'name': '测试用户A', 'password': 'test123', 'is_admin': False},
    'testuserb': {'name': '测试用户B', 'password': 'test123', 'is_admin': False}
}

class HybridStorage:
    def __init__(self):
        self.memory_data = {
            'users': PRESET_USERS.copy(),
            'student_data': {'primary': [], 'junior': [], 'high': [], 'other': []},
            'pending_data': [], 'announcements': [], 'chat_messages': [],
            'questions': [], 'friends': {}, 'private_messages': {}
        }
    
    def get_data(self):
        return self.memory_data
    
    def save_user(self, username, user_data):
        """保存用户到内存（临时）"""
        self.memory_data['users'][username] = user_data
        return True

storage = HybridStorage()

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

        # 创建新用户（保存在内存中）
        new_user = {
            'name': name, 'school': school, 'email': email,
            'password': password, 'is_admin': False,
            'intro': '新注册用户', 'created_at': datetime.now().isoformat()
        }
        
        storage.save_user(username, new_user)

        return jsonify({
            'success': True, 'message': '註冊成功（临时存储）',
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
            'success': True, 'message': '登入成功',
            'user': {'name': user['name'], 'username': username, 'isAdmin': user.get('is_admin', False)}
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'登入失敗: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
