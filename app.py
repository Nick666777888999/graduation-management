from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"status": "API Running", "message": "畢業管理系統 API"})

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/admin/users')
def admin_users():
    return jsonify({"users": [], "message": "管理員 API 正常"})

@app.route('/api/get-sync-data')
def get_sync_data():
    return jsonify({"success": True, "message": "同步 API 正常"})

if __name__ == '__main__':
    app.run()
else:
    application = app
