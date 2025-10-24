import re

with open('api/index.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("正在添加管理員 API 路由...")

# 添加缺失的管理員 API 路由
admin_routes = '''# ==================== 管理員 API ====================
@app.route('/api/admin/users', methods=['GET'])
def admin_users():
    """獲取所有用戶"""
    # 不返回密碼
    users_safe = {}
    for username, user in storage.users.items():
        user_copy = user.copy()
        user_copy.pop('password', None)
        users_safe[username] = user_copy
        
    return jsonify({
        "success": True,
        "users": users_safe,
        "count": len(users_safe),
        "message": "用戶數據獲取成功"
    })

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    """系統統計"""
    total_students = sum(len(v) for v in storage.student_data.values())
    
    return jsonify({
        "success": True,
        "stats": {
            "users_count": len(storage.users),
            "messages_count": len(storage.messages),
            "students_count": total_students,
            "pending_count": len(storage.pending_data),
            "announcements_count": len(storage.announcements)
        },
        "message": "統計數據獲取成功"
    })

@app.route('/api/admin/pending-approvals', methods=['GET'])
def admin_pending_approvals():
    """待審核數據"""
    return jsonify({
        "success": True,
        "pending": storage.pending_data,
        "count": len(storage.pending_data),
        "message": "待審核數據獲取成功"
    })

@app.route('/api/admin/student-data', methods=['GET'])
def admin_student_data():
    """學生資料管理"""
    total_count = sum(len(v) for v in storage.student_data.values())
    return jsonify({
        "success": True,
        "data": storage.student_data,
        "total_count": total_count,
        "message": "學生資料獲取成功"
    })

@app.route('/api/admin/system-config', methods=['GET'])
def admin_system_config():
    """系統配置"""
    return jsonify({
        "success": True,
        "config": storage.system_config,
        "message": "系統配置獲取成功"
    })'''

# 在 get-all-data 路由之前插入管理員路由
if "@app.route('/api/get-all-data'" in content:
    content = content.replace(
        "@app.route('/api/get-all-data'",
        admin_routes + "\n\n@app.route('/api/get-all-data'"
    )
    print("✅ 管理員 API 路由已添加到 get-all-data 之前")
elif "@app.route('/'" in content:
    # 如果在根路由之後插入
    content = content.replace(
        "@app.route('/')",
        "@app.route('/')\n\n" + admin_routes + "\n\n"
    )
    print("✅ 管理員 API 路由已添加到根路由之後")
else:
    # 在文件末尾添加
    content = content + "\n\n" + admin_routes
    print("✅ 管理員 API 路由已添加到文件末尾")

with open('api/index.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("修復完成！")
