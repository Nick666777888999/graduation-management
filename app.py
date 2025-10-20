from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')
CORS(app)

# 簡單的內存存儲
storage = {
    'users': {},
    'messages': [],
    'announcements': []
}

@app.route('/')
def home():
    return jsonify({"status": "success", "message": "畢業管理系統 API", "version": "1.0"})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "graduation-system"})

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"success": True, "message": "API 測試成功"})

@app.route('/api/admin/users', methods=['GET'])
def admin_users():
    return jsonify({
        "success": True, 
        "users": storage['users'],
        "count": len(storage['users'])
    })

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    return jsonify({
        "success": True,
        "stats": {
            "users_count": len(storage['users']),
            "messages_count": len(storage['messages']),
            "announcements_count": len(storage['announcements'])
        }
    })

@app.route('/api/sync-data', methods=['POST'])
def sync_data():
    try:
        data = request.get_json()
        if data and 'users' in data:
            storage['users'].update(data['users'])
        return jsonify({"success": True, "message": "同步成功"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/get-sync-data', methods=['GET'])
def get_sync_data():
    return jsonify({
        "success": True,
        "users": storage['users'],
        "messages": storage['messages'][-50:],
        "announcements": storage['announcements']
    })

# Vercel 需要這個
if __name__ == '__main__':
    app.run(debug=False)
else:
    application = app
