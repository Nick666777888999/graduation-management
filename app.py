import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 使用內存存儲（避免 SQLite 問題）
storage = {
    'users': {},
    'messages': []
}

@app.route('/')
def home():
    return jsonify({"status": "running", "message": "畢業管理系統 API"})

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/test')
def test():
    return jsonify({"success": True, "message": "API 正常工作"})

@app.route('/api/sync-data', methods=['POST'])
def sync_data():
    try:
        data = request.get_json()
        if 'users' in data:
            storage['users'].update(data['users'])
        if 'messages' in data:
            storage['messages'] = data['messages'][-100:]
        return jsonify({"success": True, "message": "同步成功"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/get-sync-data', methods=['GET'])
def get_sync_data():
    return jsonify({
        "success": True,
        "users": storage['users'],
        "messages": storage['messages'][-50:]
    })

# Vercel 需要這個
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
else:
    application = app
