from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"status": "success", "message": "畢業管理系統 API"})

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/admin/users')
def admin_users():
    return jsonify({"users": [], "message": "用戶數據"})

@app.route('/api/admin/stats') 
def admin_stats():
    return jsonify({"stats": {"users": 0, "messages": 0}})

@app.route('/api/admin/pending-approvals')
def admin_pending_approvals():
    return jsonify({"pending": [], "message": "待審核數據"})

@app.route('/api/admin/student-data')
def admin_student_data():
    return jsonify({"data": {"primary": [], "junior": [], "high": [], "other": []}})

@app.route('/api/messages')
def messages():
    return jsonify({"messages": []})

@app.route('/api/get-sync-data')
def get_sync_data():
    return jsonify({"data": {"users": {}, "messages": []}})

# Vercel 需要
application = app

if __name__ == '__main__':
    app.run()
