import re

with open('api/index.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 檢查是否已有 sync-all-data 路由
if 'sync-all-data' not in content:
    print("添加 sync-all-data 路由...")
    
    sync_route = '''
@app.route('/api/sync-all-data', methods=['POST'])
def sync_all_data():
    """同步所有數據到雲端"""
    try:
        data = request.get_json()
        
        # 同步用戶數據
        if 'users' in data:
            for username, user_data in data['users'].items():
                if username not in storage.users:
                    storage.users[username] = user_data

        # 同步聊天消息
        if 'messages' in data:
            storage.messages = data['messages']

        # 同步好友數據
        if 'friends' in data:
            for username, friend_data in data['friends'].items():
                storage.friends[username] = friend_data

        # 同步問題數據
        if 'questions' in data:
            storage.questions = data['questions']

        return jsonify({
            "success": True,
            "message": "數據同步成功",
            "synced_items": list(data.keys())
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"同步失敗: {str(e)}"
        }), 500
'''

    # 在 get-all-data 路由後插入
    if '@app.route(\\'/api/get-all-data\\'' in content:
        content = content.replace(
            '@app.route(\\'/api/get-all-data\\'',
            sync_route + '\\n\\n@app.route(\\'/api/get-all-data\\''
        )
        print("✅ 已添加 sync-all-data 路由")
    else:
        print("❌ 找不到插入位置")

with open('api/index.py', 'w', encoding='utf-8') as f:
    f.write(content)
