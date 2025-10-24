from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# 数据文件路径
DATA_FILE = '/tmp/graduation_data.json'

def load_data():
    """加载数据"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        # 默认数据
        return {
            'users': {
                'Nick20130104': {
                    'name': '系統管理員',
                    'school': '管理學校',
                    'email': 'admin@system.com',
                    'password': 'Nick20130104',  # 明确保存密码
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

def save_data(data):
    """保存数据"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

@app.route('/api/health')
def health():
    return jsonify({'service': 'graduation-management-system', 'status': 'healthy'})

@app.route('/api/get-all-data')
def get_all_data():
    data = load_data()
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

        # 加载现有数据
        all_data = load_data()
        users = all_data.get('users', {})

        # 检查用户名是否已存在
        if username in users:
            return jsonify({'success': False, 'message': '用戶名已存在'})

        # 创建新用户 - 明确保存密码字段
        users[username] = {
            'name': name,
            'school': school,
            'email': email,
            'password': password,  # 关键修复：明确保存密码
            'is_admin': False,
            'intro': f"這是在完全重寫後端後創建的測試用戶",
            'created_at': datetime.now().isoformat()
        }

        # 保存数据
        all_data['users'] = users
        save_data(all_data)

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

        # 加载数据
        all_data = load_data()
        users = all_data.get('users', {})

        # 检查用户是否存在
        if username not in users:
            return jsonify({'success': False, 'message': '帳號或密碼錯誤'})

        user = users[username]

        # 检查密码 - 使用明确的密码字段
        if user.get('password') != password:
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

# 其他端点保持不变...

if __name__ == '__main__':
    app.run(debug=True)
