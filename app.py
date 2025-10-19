from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# 預先填入數據的存儲
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
    'messages': [
        {
            'id': 'welcome_msg',
            'sender': 'system',
            'sender_name': '系統',
            'text': '歡迎使用畢業管理系統！',
            'time': '2025/10/19 12:00:00',
            'is_admin': True
        }
    ]
}

@app.route('/')
def home():
    return jsonify({"status": "API is running"})

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/admin/users')
def admin_users():
    return jsonify({
        "success": True, 
        "users": storage['users'],
        "count": len(storage['users'])
    })

@app.route('/api/admin/stats')
def admin_stats():
    return jsonify({
        "success": True,
        "stats": {
            "users_count": len(storage['users']),
            "messages_count": len(storage['messages'])
        }
    })

@app.route('/api/get-sync-data')
def get_sync_data():
    return jsonify({
        "success": True,
        "users": storage['users'],
        "messages": storage['messages']
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
else:
    application = app
