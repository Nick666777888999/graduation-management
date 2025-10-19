import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
CORS(app, supports_credentials=True)

# 数据库连接
def get_db_connection():
    conn = sqlite3.connect('graduation.db')
    conn.row_factory = sqlite3.Row
    return conn

# 数据库初始化
def init_db():
    conn = get_db_connection()
    
    # 用户表
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            name TEXT,
            school TEXT,
            email TEXT,
            is_admin BOOLEAN DEFAULT FALSE,
            intro TEXT,
            anonymous TEXT,
            avatar TEXT,
            personality TEXT,
            hobbies TEXT,
            likes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 聊天讯息表
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            sender TEXT,
            text TEXT,
            time TEXT,
            sender_name TEXT,
            is_admin BOOLEAN,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 好友关系表
    conn.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1 TEXT,
            user2 TEXT,
            status TEXT DEFAULT 'accepted',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user1, user2)
        )
    ''')
    
    # 好友申请表
    conn.execute('''
        CREATE TABLE IF NOT EXISTS friend_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user TEXT,
            to_user TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 问题表
    conn.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY,
            text TEXT,
            subject TEXT,
            grade TEXT,
            image TEXT,
            author TEXT,
            author_name TEXT,
            likes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 问题点赞表
    conn.execute('''
        CREATE TABLE IF NOT EXISTS question_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id TEXT,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(question_id, username)
        )
    ''')
    
    # 问题留言表
    conn.execute('''
        CREATE TABLE IF NOT EXISTS question_comments (
            id TEXT PRIMARY KEY,
            question_id TEXT,
            author TEXT,
            text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 公告表
    conn.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id TEXT PRIMARY KEY,
            title TEXT,
            content TEXT,
            author TEXT,
            author_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 学生资料表
    conn.execute('''
        CREATE TABLE IF NOT EXISTS student_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            school TEXT,
            email TEXT,
            grade TEXT,
            level TEXT,
            personality TEXT,
            hobbies TEXT,
            likes TEXT,
            intro TEXT,
            avatar TEXT,
            status TEXT DEFAULT 'approved',
            submitted_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 私讯表
    conn.execute('''
        CREATE TABLE IF NOT EXISTS private_messages (
            id TEXT PRIMARY KEY,
            chat_key TEXT,
            from_user TEXT,
            to_user TEXT,
            text TEXT,
            media_type TEXT,
            media_data TEXT,
            read_status BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # 确保管理员账号存在
    ensure_admin_user()

def ensure_admin_user():
    conn = get_db_connection()
    admin = conn.execute('SELECT * FROM users WHERE username = ?', ('Nick20130104',)).fetchone()
    if not admin:
        conn.execute('''
            INSERT INTO users (username, password, name, school, email, is_admin, intro, anonymous, personality, hobbies, likes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'Nick20130104', 
            generate_password_hash('Nick20130104'), 
            '系统管理员', '管理学校', 'admin@system.com', 
            True, '我是系统管理员，负责管理毕业资料系统。', '管理员', 
            '认真负责、细心严谨', '系统管理、程序设计', '解决问题、学习新技术'
        ))
        conn.commit()
    conn.close()

# 首页
@app.route('/')
def home():
    return jsonify({
        'message': '毕业管理系统 API',
        'version': '1.0.0',
        'status': 'running'
    })

# 用户 API
@app.route('/api/users', methods=['GET', 'POST'])
def users_api():
    if request.method == 'GET':
        conn = get_db_connection()
        users = conn.execute('SELECT username, name, school, email, is_admin, intro, anonymous, avatar, personality, hobbies, likes, created_at FROM users').fetchall()
        conn.close()
        return jsonify([dict(user) for user in users])
    
    elif request.method == 'POST':
        data = request.json
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO users (username, password, name, school, email, is_admin, intro, anonymous)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['username'], 
                generate_password_hash(data['password']),
                data['name'], 
                data['school'], 
                data['email'], 
                False,
                data['intro'], 
                data.get('anonymous', data['name'])
            ))
            conn.commit()
            return jsonify({'success': True, 'message': '用户创建成功'})
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        finally:
            conn.close()

# 登录 API
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (data['username'],)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], data['password']):
        session['username'] = user['username']
        session['is_admin'] = user['is_admin']
        return jsonify({
            'success': True, 
            'user': {
                'name': user['name'], 
                'isAdmin': user['is_admin'],
                'username': user['username']
            }
        })
    
    return jsonify({'success': False, 'message': '帐号或密码错误'}), 401

# 聊天讯息 API
@app.route('/api/messages', methods=['GET', 'POST'])
def messages_api():
    if request.method == 'GET':
        conn = get_db_connection()
        messages = conn.execute('SELECT * FROM messages ORDER BY timestamp DESC LIMIT 100').fetchall()
        conn.close()
        return jsonify([dict(msg) for msg in messages])
    
    elif request.method == 'POST':
        data = request.json
        conn = get_db_connection()
        message_id = str(uuid.uuid4())
        current_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        
        conn.execute('''
            INSERT INTO messages (id, sender, text, time, sender_name, is_admin)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            message_id, 
            data['sender'], 
            data['text'],
            current_time,
            data.get('sender_name', data['sender']),
            data.get('is_admin', False)
        ))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'id': message_id})

# 好友系统 API
@app.route('/api/friends', methods=['GET', 'POST', 'DELETE'])
def friends_api():
    username = session.get('username')
    if not username:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    if request.method == 'GET':
        conn = get_db_connection()
        
        # 获取好友列表
        friends = conn.execute('''
            SELECT u.username, u.name, u.avatar, u.school 
            FROM friends f 
            JOIN users u ON (
                (f.user1 = u.username AND f.user2 = ?) OR 
                (f.user2 = u.username AND f.user1 = ?)
            ) 
            WHERE u.username != ? AND f.status = 'accepted'
        ''', (username, username, username)).fetchall()
        
        # 获取好友申请
        requests = conn.execute('''
            SELECT fr.*, u.name as from_name, u.school as from_school
            FROM friend_requests fr 
            JOIN users u ON fr.from_user = u.username 
            WHERE fr.to_user = ? AND fr.status = 'pending'
        ''', (username,)).fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'friends': [dict(friend) for friend in friends],
            'requests': [dict(req) for req in requests]
        })
    
    elif request.method == 'POST':
        data = request.json
        from_user = username
        to_user = data['username']
        
        conn = get_db_connection()
        
        # 检查是否已经是好友
        existing_friend = conn.execute('''
            SELECT * FROM friends 
            WHERE (user1 = ? AND user2 = ?) OR (user1 = ? AND user2 = ?)
        ''', (from_user, to_user, to_user, from_user)).fetchone()
        
        if existing_friend:
            conn.close()
            return jsonify({'success': False, 'message': '已经是好友'}), 400
        
        # 检查是否已有 pending 的申请
        existing_request = conn.execute('''
            SELECT * FROM friend_requests 
            WHERE from_user = ? AND to_user = ? AND status = 'pending'
        ''', (from_user, to_user)).fetchone()
        
        if existing_request:
            conn.close()
            return jsonify({'success': False, 'message': '已发送过好友申请'}), 400
        
        conn.execute('''
            INSERT INTO friend_requests (from_user, to_user) VALUES (?, ?)
        ''', (from_user, to_user))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '好友申请已发送'})

# 处理好友申请
@app.route('/api/friend-requests/<int:request_id>/<action>', methods=['POST'])
def handle_friend_request(request_id, action):
    username = session.get('username')
    if not username:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    conn = get_db_connection()
    
    # 验证请求属于当前用户
    request_data = conn.execute('''
        SELECT * FROM friend_requests 
        WHERE id = ? AND to_user = ? AND status = 'pending'
    ''', (request_id, username)).fetchone()
    
    if not request_data:
        conn.close()
        return jsonify({'success': False, 'message': '请求不存在'}), 404
    
    if action == 'accept':
        # 添加好友关系
        conn.execute('''
            INSERT INTO friends (user1, user2) VALUES (?, ?)
        ''', (request_data['from_user'], request_data['to_user']))
        
        # 更新申请状态
        conn.execute('''
            UPDATE friend_requests SET status = 'accepted' WHERE id = ?
        ''', (request_id,))
        
    elif action == 'reject':
        # 更新申请状态
        conn.execute('''
            UPDATE friend_requests SET status = 'rejected' WHERE id = ?
        ''', (request_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': f'好友申请已{action}'})

# 问题讨论 API
@app.route('/api/questions', methods=['GET', 'POST'])
def questions_api():
    if request.method == 'GET':
        conn = get_db_connection()
        questions = conn.execute('''
            SELECT q.*, 
                   (SELECT COUNT(*) FROM question_likes WHERE question_id = q.id) as likes_count
            FROM questions q 
            ORDER BY q.created_at DESC
        ''').fetchall()
        conn.close()
        return jsonify([dict(q) for q in questions])
    
    elif request.method == 'POST':
        data = request.json
        conn = get_db_connection()
        question_id = f"q_{int(datetime.now().timestamp() * 1000)}"
        
        conn.execute('''
            INSERT INTO questions (id, text, subject, grade, image, author, author_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            question_id,
            data['text'], 
            data['subject'], 
            data['grade'],
            data.get('image'), 
            data['author'], 
            data['author_name']
        ))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'id': question_id})

# 问题点赞 API
@app.route('/api/questions/<question_id>/like', methods=['POST'])
def like_question(question_id):
    username = session.get('username')
    if not username:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    conn = get_db_connection()
    
    try:
        # 检查是否已经点赞
        existing_like = conn.execute('''
            SELECT * FROM question_likes WHERE question_id = ? AND username = ?
        ''', (question_id, username)).fetchone()
        
        if existing_like:
            # 取消点赞
            conn.execute('''
                DELETE FROM question_likes WHERE question_id = ? AND username = ?
            ''', (question_id, username))
            action = 'unliked'
        else:
            # 添加点赞
            conn.execute('''
                INSERT INTO question_likes (question_id, username) VALUES (?, ?)
            ''', (question_id, username))
            action = 'liked'
        
        conn.commit()
        
        # 获取更新后的点赞数
        likes_count = conn.execute('''
            SELECT COUNT(*) as count FROM question_likes WHERE question_id = ?
        ''', (question_id,)).fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'success': True, 
            'action': action,
            'likes_count': likes_count
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

# 公告 API
@app.route('/api/announcements', methods=['GET', 'POST'])
def announcements_api():
    if request.method == 'GET':
        conn = get_db_connection()
        announcements = conn.execute('SELECT * FROM announcements ORDER BY created_at DESC').fetchall()
        conn.close()
        return jsonify([dict(ann) for ann in announcements])
    
    elif request.method == 'POST':
        if not session.get('is_admin'):
            return jsonify({'success': False, 'message': '权限不足'}), 403
        
        data = request.json
        conn = get_db_connection()
        announcement_id = f"ann_{int(datetime.now().timestamp() * 1000)}"
        
        conn.execute('''
            INSERT INTO announcements (id, title, content, author, author_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            announcement_id,
            data['title'], 
            data['content'], 
            session['username'], 
            data['author_name']
        ))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'id': announcement_id})

# 学生资料 API
@app.route('/api/student-data', methods=['GET', 'POST'])
def student_data_api():
    if request.method == 'GET':
        level = request.args.get('level', 'all')
        conn = get_db_connection()
        
        if level == 'all':
            data = conn.execute('SELECT * FROM student_data WHERE status = "approved"').fetchall()
        else:
            data = conn.execute('SELECT * FROM student_data WHERE level = ? AND status = "approved"', (level,)).fetchall()
        
        conn.close()
        return jsonify([dict(item) for item in data])
    
    elif request.method == 'POST':
        data = request.json
        conn = get_db_connection()
        
        conn.execute('''
            INSERT INTO student_data (name, school, email, grade, level, personality, hobbies, likes, intro, avatar, submitted_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'], data['school'], data['email'], data['grade'],
            data['level'], data['personality'], data['hobbies'], data['likes'],
            data['intro'], data.get('avatar'), data.get('submitted_by')
        ))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

# 私讯 API
@app.route('/api/private-messages', methods=['GET', 'POST'])
def private_messages_api():
    username = session.get('username')
    if not username:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    if request.method == 'GET':
        chat_key = request.args.get('chat_key')
        conn = get_db_connection()
        messages = conn.execute('''
            SELECT * FROM private_messages 
            WHERE chat_key = ? 
            ORDER BY created_at 
            LIMIT 100
        ''', (chat_key,)).fetchall()
        conn.close()
        return jsonify([dict(msg) for msg in messages])
    
    elif request.method == 'POST':
        data = request.json
        conn = get_db_connection()
        message_id = str(uuid.uuid4())
        
        conn.execute('''
            INSERT INTO private_messages (id, chat_key, from_user, to_user, text)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            message_id,
            data['chat_key'], 
            data['from_user'],
            data['to_user'], 
            data['text']
        ))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'id': message_id})

# 检查登录状态
@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    if 'username' in session:
        conn = get_db_connection()
        user = conn.execute('SELECT username, name, is_admin FROM users WHERE username = ?', (session['username'],)).fetchone()
        conn.close()
        return jsonify({
            'authenticated': True,
            'user': {
                'username': user['username'],
                'name': user['name'], 
                'isAdmin': user['is_admin']
            }
        })
    return jsonify({'authenticated': False})

# 登出
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

# 健康检查
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
# ==================== 數據同步 API ====================
@app.route('/api/sync-data', methods=['POST'])
def sync_data():
    """接收前端 localStorage 數據並同步到數據庫"""
    try:
        data = request.json
        print("收到同步數據:", data.keys())
        
        # 同步用戶數據
        if 'users' in data:
            for username, user_data in data['users'].items():
                conn = get_db_connection()
                existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
                if not existing_user:
                    conn.execute('''
                        INSERT INTO users (username, password, name, school, email, intro, anonymous)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        username,
                        'synced_password',  # 臨時密碼
                        user_data.get('name', ''),
                        user_data.get('school', ''),
                        user_data.get('email', ''),
                        user_data.get('intro', ''),
                        user_data.get('anonymous', '')
                    ))
                conn.commit()
                conn.close()
        
        # 同步聊天訊息
        if 'messages' in data:
            for message in data['messages']:
                conn = get_db_connection()
                existing_msg = conn.execute('SELECT * FROM messages WHERE id = ?', (message.get('id'),)).fetchone()
                if not existing_msg:
                    conn.execute('''
                        INSERT INTO messages (id, sender, text, time, sender_name, is_admin)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        message.get('id', str(uuid.uuid4())),
                        message.get('sender', ''),
                        message.get('text', ''),
                        message.get('time', datetime.now().strftime('%Y/%m/%d %H:%M:%S')),
                        message.get('sender_name', ''),
                        message.get('is_admin', False)
                    ))
                conn.commit()
                conn.close()
        
        return jsonify({'success': True, 'message': '數據同步成功'})
    
    except Exception as e:
        print("同步錯誤:", str(e))
        return jsonify({'success': False, 'message': f'同步失敗: {str(e)}'}), 500

@app.route('/api/get-sync-data', methods=['GET'])
def get_sync_data():
    """獲取雲端數據供前端使用"""
    try:
        conn = get_db_connection()
        
        # 獲取用戶數據
        users = conn.execute('SELECT * FROM users').fetchall()
        users_dict = {user['username']: dict(user) for user in users}
        
        # 獲取聊天訊息
        messages = conn.execute('SELECT * FROM messages ORDER BY timestamp DESC LIMIT 100').fetchall()
        messages_list = [dict(msg) for msg in messages]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'users': users_dict,
            'messages': messages_list
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
# ==================== 測試和診斷 API ====================
@app.route('/api/test')
def test_api():
    """測試 API 是否正常工作"""
    return jsonify({'success': True, 'message': 'API 服務正常'})

@app.route('/api/test-db')
def test_db():
    """測試數據庫連接"""
    try:
        conn = get_db_connection()
        conn.execute('SELECT 1')
        conn.close()
        return jsonify({'success': True, 'message': '數據庫連接正常'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'數據庫錯誤: {str(e)}'}), 500

# ==================== 修復同步 API ====================
@app.route('/api/sync-data', methods=['POST'])
def sync_data():
    """接收前端 localStorage 數據並同步到數據庫"""
    try:
        print("=== 開始同步數據 ===")
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': '沒有收到數據'}), 400
        
        print(f"收到數據類型: {type(data)}")
        print(f"數據包含的鍵: {list(data.keys())}")
        
        # 測試數據庫連接
        conn = get_db_connection()
        print("數據庫連接成功")
        
        # 簡單同步示例 - 只同步用戶數據
        if 'users' in data and data['users']:
            users_count = 0
            for username, user_data in data['users'].items():
                existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
                if not existing_user:
                    conn.execute('''
                        INSERT INTO users (username, password, name, school, email, intro, anonymous)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        username,
                        'synced_password',
                        user_data.get('name', ''),
                        user_data.get('school', ''),
                        user_data.get('email', ''),
                        user_data.get('intro', ''),
                        user_data.get('anonymous', '')
                    ))
                    users_count += 1
            conn.commit()
            print(f"成功同步 {users_count} 個用戶")
        
        conn.close()
        return jsonify({'success': True, 'message': f'數據同步成功，新增 {users_count} 個用戶'})
    
    except Exception as e:
        print(f"同步錯誤: {str(e)}")
        import traceback
        print(f"錯誤堆棧: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'同步失敗: {str(e)}'}), 500

@app.route('/api/get-sync-data', methods=['GET'])
def get_sync_data():
    """獲取雲端數據供前端使用"""
    try:
        conn = get_db_connection()
        
        # 簡單返回用戶數量測試
        users_count = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
        messages_count = conn.execute('SELECT COUNT(*) as count FROM messages').fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'users_count': users_count,
                'messages_count': messages_count
            },
            'message': '數據獲取成功'
        })
    
    except Exception as e:
        print(f"獲取數據錯誤: {str(e)}")
        return jsonify({'success': False, 'message': f'獲取數據失敗: {str(e)}'}), 500
