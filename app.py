import os
import re
from datetime import datetime
import uuid
from threading import Thread, Lock
import time
import logging
import secrets
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import json
from collections import defaultdict
from supabase import create_client

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))
CORS(app, supports_credentials=True)

# Supabase 配置
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# 線程鎖
data_lock = Lock()

# 全局變數追蹤最後活動時間和已讀狀態
last_activity = defaultdict(lambda: defaultdict(float))
last_update_check = defaultdict(float)

def load_json_file(table_name, default_data):
    """從 Supabase 載入數據"""
    try:
        if supabase:
            response = supabase.table(table_name).select('*').execute()
            return response.data if response.data else default_data
    except Exception as e:
        logger.error(f"Error loading from Supabase {table_name}: {e}")
    return default_data

def save_json_file(table_name, data):
    """保存數據到 Supabase"""
    try:
        if supabase:
            # 清空表並插入新數據
            supabase.table(table_name).delete().neq('id', '0').execute()
            if data:
                supabase.table(table_name).insert(data).execute()
            return True
    except Exception as e:
        logger.error(f"Error saving to Supabase {table_name}: {e}")
    return False

def load_all_data():
    """載入所有系統資料"""
    with data_lock:
        data = {
            'users': load_json_file('users', {}),
            'student_data': load_json_file('student_data', {
                'primary': [], 'junior': [], 'high': [], 'other': []
            }),
            'messages': load_json_file('messages', []),
            'pending_data': load_json_file('pending_data', []),
            'announcements': load_json_file('announcements', []),
            'friends': load_json_file('friends', {}),
            'private_messages': load_json_file('private_messages', {}),
            'questions': load_json_file('questions', [])
        }
        
        # 轉換 users 數據格式
        if data['users'] and isinstance(data['users'], list):
            users_dict = {}
            for user in data['users']:
                username = user.pop('username', None)
                if username:
                    users_dict[username] = user
            data['users'] = users_dict
        
        # 確保管理員帳號存在
        if 'Nick20130104' not in data['users']:
            data['users']['Nick20130104'] = {
                'password': 'Nick20130104',
                'name': '系統管理員',
                'school': '管理學校',
                'email': 'admin@system.com',
                'isAdmin': True,
                'intro': '我是系統管理員，負責管理畢業資料系統。',
                'anonymous': '管理員',
                'avatar': None,
                'personality': '認真負責、細心嚴謹',
                'hobbies': '系統管理、程式設計',
                'likes': '解決問題、學習新技術',
                'created_at': datetime.now().isoformat()
            }
            save_all_data(data)
            
        return data

def save_all_data(data):
    """儲存所有系統資料"""
    with data_lock:
        success = True
        
        # 轉換 users 為列表格式保存
        users_list = []
        for username, user_data in data['users'].items():
            user_data['username'] = username
            users_list.append(user_data)
        
        success &= save_json_file('users', users_list)
        success &= save_json_file('student_data', data['student_data'])
        success &= save_json_file('messages', data['messages'])
        success &= save_json_file('pending_data', data['pending_data'])
        success &= save_json_file('announcements', data['announcements'])
        success &= save_json_file('friends', data['friends'])
        success &= save_json_file('private_messages', data['private_messages'])
        success &= save_json_file('questions', data['questions'])
        return success

def save_all_data(data):
    """儲存所有系統資料"""
    with data_lock:
        success = True
        success &= save_json_file(USERS_FILE, data['users'])
        success &= save_json_file(STUDENT_DATA_FILE, data['student_data'])
        success &= save_json_file(MESSAGES_FILE, data['messages'])
        success &= save_json_file(PENDING_DATA_FILE, data['pending_data'])
        success &= save_json_file(ANNOUNCEMENTS_FILE, data['announcements'])
        success &= save_json_file(FRIENDS_FILE, data['friends'])
        success &= save_json_file(PRIVATE_MESSAGES_FILE, data['private_messages'])
        success &= save_json_file(QUESTIONS_FILE, data['questions'])
        return success

# 實時檢查 API - 修復版本
@app.route('/api/check_updates', methods=['GET'])
def check_updates():
    """檢查用戶是否有新消息或好友請求"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': '請先登入'}), 401
    
    username = session['username']
    current_time = time.time()
    
    # 防止過於頻繁的檢查（至少間隔2秒）
    if current_time - last_update_check[username] < 2:
        return jsonify({'success': True, 'no_updates': True}), 200
    
    last_update_check[username] = current_time
    system_data = load_all_data()
    
    # 檢查新私訊
    new_private_messages = 0
    user_friends = system_data['friends'].get(username, {'friends': []})
    
    for friend in user_friends.get('friends', []):
        chat_key = f"{min(username, friend['username'])}_{max(username, friend['username'])}"
        messages = system_data['private_messages'].get(chat_key, [])
        
        # 計算未讀消息（只計算對方發送且未讀的）
        for msg in messages:
            if (msg.get('from') != username and 
                not msg.get('read', False) and
                msg.get('timestamp', '') > last_activity[username].get('private_messages', '')):
                new_private_messages += 1
    
    # 檢查好友請求
    pending_requests = len(system_data['friends'].get(username, {}).get('received_requests', []))
    
    # 檢查公共聊天室新消息 - 修復邏輯
    new_public_messages = 0
    if system_data['messages']:
        last_message = system_data['messages'][-1]
        last_msg_time = last_message.get('timestamp', '')
        # 只檢查非自己發送且在自己最後活動時間之後的消息
        if (last_message.get('sender') != username and 
            last_msg_time > last_activity[username].get('public_messages', '')):
            new_public_messages = 1
    
    # 檢查新問題 - 修復邏輯
    new_questions = 0
    if system_data['questions']:
        # 找到最新問題
        latest_question = system_data['questions'][0] if system_data['questions'] else None
        if latest_question:
            last_q_time = latest_question.get('created_at', '')
            # 只檢查非自己發送且在自己最後活動時間之後的問題
            if (latest_question.get('author') != username and 
                last_q_time > last_activity[username].get('questions', '')):
                new_questions = 1
    
    # 如果有更新，更新最後活動時間
    if any([new_private_messages, pending_requests, new_public_messages, new_questions]):
        last_activity[username]['last_check'] = datetime.now().isoformat()
    
    return jsonify({
        'success': True,
        'new_private_messages': new_private_messages,
        'pending_friend_requests': pending_requests,
        'new_public_messages': new_public_messages,
        'new_questions': new_questions,
        'timestamp': current_time
    })

# 更新活動時間 API
@app.route('/api/update_activity', methods=['POST'])
def update_activity():
    """更新用戶最後活動時間"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': '請先登入'}), 401
    
    data = request.get_json()
    activity_type = data.get('type', 'general')
    
    # 更新對應類型的最後活動時間
    last_activity[session['username']][activity_type] = datetime.now().isoformat()
    
    return jsonify({'success': True})

# 修改私訊 API，添加已讀標記和實時同步
@app.route('/api/private_messages', methods=['POST'])
def send_private_message():
    """發送私訊（增強版本）"""
    try:
        if 'username' not in session:
            return jsonify({'success': False, 'message': '請先登入'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '無效的請求資料'}), 400
        
        friend_username = data.get('friend_username', '').strip()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'success': False, 'message': '請輸入訊息內容'}), 400
        
        system_data = load_all_data()
        
        # 檢查是否為好友
        friends_data = system_data.get('friends', {})
        current_user_friends = friends_data.get(session['username'], {'friends': []})
        
        if not any(friend.get('username') == friend_username for friend in current_user_friends.get('friends', [])):
            return jsonify({'success': False, 'message': '只能與好友私訊'}), 403
        
        # 初始化私訊數據
        chat_key = f"{min(session['username'], friend_username)}_{max(session['username'], friend_username)}"
        
        if chat_key not in system_data['private_messages']:
            system_data['private_messages'][chat_key] = []
        
        message = {
            'id': str(uuid.uuid4()),
            'from': session['username'],
            'from_name': system_data['users'][session['username']]['name'],
            'text': text,
            'time': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        
        system_data['private_messages'][chat_key].append(message)
        
        # 只保留最近200條訊息
        if len(system_data['private_messages'][chat_key]) > 200:
            system_data['private_messages'][chat_key] = system_data['private_messages'][chat_key][-200:]
        
        if save_all_data(system_data):
            # 更新發送者的活動時間
            last_activity[session['username']]['private_messages'] = datetime.now().isoformat()
            return jsonify({'success': True, 'message': '私訊已發送', 'message_data': message}), 200
        else:
            return jsonify({'success': False, 'message': '發送失敗'}), 500
            
    except Exception as e:
        logger.error(f"Private messages error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤'}), 500

# 獲取私訊 API - 增強版本
@app.route('/api/private_messages', methods=['GET'])
def get_private_messages():
    """取得私訊（增強版本）"""
    try:
        if 'username' not in session:
            return jsonify({'success': False, 'message': '請先登入'}), 401
        
        system_data = load_all_data()
        
        # 取得與特定好友的私訊
        friend_username = request.args.get('friend_username', '').strip()
        
        if not friend_username:
            return jsonify({'success': False, 'message': '請指定好友'}), 400
        
        # 檢查是否為好友
        friends_data = system_data.get('friends', {})
        current_user_friends = friends_data.get(session['username'], {'friends': []})
        
        if not any(friend.get('username') == friend_username for friend in current_user_friends.get('friends', [])):
            return jsonify({'success': False, 'message': '只能與好友私訊'}), 403
        
        # 取得私訊
        chat_key = f"{min(session['username'], friend_username)}_{max(session['username'], friend_username)}"
        messages = system_data['private_messages'].get(chat_key, [])
        
        # 標記對方發送的訊息為已讀
        updated = False
        for msg in messages:
            if msg.get('from') != session['username'] and not msg.get('read', False):
                msg['read'] = True
                updated = True
        
        if updated:
            save_all_data(system_data)
        
        return jsonify({
            'success': True,
            'messages': messages[-100:]  # 只返回最近100條
        }), 200
                
    except Exception as e:
        logger.error(f"Private messages error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤'}), 500

# 發送聊天訊息 API - 增強版本
@app.route('/api/send_message', methods=['POST'])
def send_message():
    """發送聊天訊息（增強版本）"""
    try:
        if 'username' not in session:
            return jsonify({'success': False, 'message': '請先登入'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '無效的請求資料'}), 400
        
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'success': False, 'message': '請輸入訊息內容'}), 400
        
        system_data = load_all_data()
        user = system_data['users'].get(session['username'])
        
        message = {
            'id': str(uuid.uuid4()),
            'sender': session['username'],
            'text': text,
            'time': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            'sender_name': user.get('anonymous', user.get('name', '匿名')) if user else '匿名',
            'is_admin': user.get('isAdmin', False) if user else False,
            'timestamp': datetime.now().isoformat()
        }
        
        system_data['messages'].append(message)
        
        # 只保留最近200條訊息
        if len(system_data['messages']) > 200:
            system_data['messages'] = system_data['messages'][-200:]
        
        if save_all_data(system_data):
            # 更新發送者的活動時間
            last_activity[session['username']]['public_messages'] = datetime.now().isoformat()
            return jsonify({'success': True, 'message': '訊息已發送', 'message_data': message}), 200
        else:
            return jsonify({'success': False, 'message': '發送失敗'}), 500
            
    except Exception as e:
        logger.error(f"Send message error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤'}), 500

# 獲取聊天訊息 API - 增強版本
@app.route('/api/messages', methods=['GET'])
def get_messages():
    """取得聊天訊息（增強版本）"""
    try:
        system_data = load_all_data()
        
        # 更新當前用戶的活動時間
        if 'username' in session:
            last_activity[session['username']]['public_messages'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'messages': system_data['messages'][-100:]  # 只返回最近100條
        }), 200
        
    except Exception as e:
        logger.error(f"Get messages error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤'}), 500

# 題目討論區 API - 修復點讚和刪除功能
@app.route('/api/questions', methods=['GET', 'POST', 'DELETE'])
def questions():
    """題目討論區（修復版本）"""
    try:
        if 'username' not in session:
            return jsonify({'success': False, 'message': '請先登入'}), 401
        
        system_data = load_all_data()
        questions_data = system_data.get('questions', [])
        
        if request.method == 'GET':
            # 更新活動時間
            last_activity[session['username']]['questions'] = datetime.now().isoformat()
            
            return jsonify({
                'success': True,
                'questions': questions_data
            }), 200
        
        elif request.method == 'POST':
            # 發表新問題
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': '無效的請求資料'}), 400
            
            text = data.get('text', '').strip()
            subject = data.get('subject', '').strip()
            grade = data.get('grade', '').strip()
            
            if not text or not subject or not grade:
                return jsonify({'success': False, 'message': '請填寫所有必填欄位'}), 400
            
            if len(text) > 150:
                return jsonify({'success': False, 'message': '問題內容不能超過150字'}), 400
            
            question = {
                'id': f"q_{int(time.time() * 1000)}",
                'text': text,
                'subject': subject,
                'grade': grade,
                'image': data.get('image'),
                'author': session['username'],
                'author_name': system_data['users'][session['username']]['name'],
                'created_at': datetime.now().isoformat(),
                'created_time': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
                'likes': 0,
                'liked_by': [],  # 記錄點讚用戶
                'comments': []
            }
            
            questions_data.insert(0, question)  # 新問題放在最前面
            system_data['questions'] = questions_data
            
            if save_all_data(system_data):
                # 更新活動時間
                last_activity[session['username']]['questions'] = datetime.now().isoformat()
                return jsonify({'success': True, 'message': '問題已發表', 'question': question}), 200
            else:
                return jsonify({'success': False, 'message': '發表失敗'}), 500
        
        elif request.method == 'DELETE':
            # 刪除問題 - 修復管理員權限
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': '無效的請求資料'}), 400
            
            question_id = data.get('question_id', '').strip()
            
            if not question_id:
                return jsonify({'success': False, 'message': '請指定問題'}), 400
            
            # 找到問題並檢查權限
            question_index = -1
            for i, q in enumerate(questions_data):
                if q['id'] == question_id:
                    # 允許管理員或問題作者刪除
                    if q['author'] != session['username'] and not session.get('is_admin'):
                        return jsonify({'success': False, 'message': '無權刪除此問題'}), 403
                    question_index = i
                    break
            
            if question_index == -1:
                return jsonify({'success': False, 'message': '問題不存在'}), 404
            
            deleted_question = questions_data.pop(question_index)
            system_data['questions'] = questions_data
            
            if save_all_data(system_data):
                return jsonify({'success': True, 'message': '問題已刪除'}), 200
            else:
                return jsonify({'success': False, 'message': '刪除失敗'}), 500
                
    except Exception as e:
        logger.error(f"Questions error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤'}), 500

# 點讚 API - 修復版本（一個帳號只能點一次）
@app.route('/api/questions/like', methods=['POST'])
def like_question():
    """點讚問題（修復版本）"""
    try:
        if 'username' not in session:
            return jsonify({'success': False, 'message': '請先登入'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '無效的請求資料'}), 400
        
        question_id = data.get('question_id', '').strip()
        
        if not question_id:
            return jsonify({'success': False, 'message': '請指定問題'}), 400
        
        system_data = load_all_data()
        questions_data = system_data.get('questions', [])
        
        # 找到問題
        question = None
        for q in questions_data:
            if q['id'] == question_id:
                question = q
                break
        
        if not question:
            return jsonify({'success': False, 'message': '問題不存在'}), 404
        
        # 初始化點讚數據
        if 'liked_by' not in question:
            question['liked_by'] = []
        
        username = session['username']
        
        # 檢查是否已經點讚
        if username in question['liked_by']:
            # 取消點讚
            question['liked_by'].remove(username)
            question['likes'] = max(0, question.get('likes', 0) - 1)
            message = '已取消點讚'
            liked = False
        else:
            # 點讚
            question['liked_by'].append(username)
            question['likes'] = question.get('likes', 0) + 1
            message = '已點讚'
            liked = True
        
        system_data['questions'] = questions_data
        
        if save_all_data(system_data):
            return jsonify({
                'success': True, 
                'message': message, 
                'likes': question['likes'],
                'liked': liked
            }), 200
        else:
            return jsonify({'success': False, 'message': '操作失敗'}), 500
            
    except Exception as e:
        logger.error(f"Like question error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤'}), 500

# 檢查點讚狀態 API
@app.route('/api/questions/check_like', methods=['GET'])
def check_like_status():
    """檢查用戶對問題的點讚狀態"""
    try:
        if 'username' not in session:
            return jsonify({'success': False, 'message': '請先登入'}), 401
        
        question_id = request.args.get('question_id', '').strip()
        
        if not question_id:
            return jsonify({'success': False, 'message': '請指定問題'}), 400
        
        system_data = load_all_data()
        questions_data = system_data.get('questions', [])
        
        # 找到問題
        question = None
        for q in questions_data:
            if q['id'] == question_id:
                question = q
                break
        
        if not question:
            return jsonify({'success': False, 'message': '問題不存在'}), 404
        
        # 檢查點讚狀態
        liked = session['username'] in question.get('liked_by', [])
        
        return jsonify({
            'success': True,
            'liked': liked,
            'likes': question.get('likes', 0)
        }), 200
            
    except Exception as e:
        logger.error(f"Check like status error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤'}), 500

# 登入 API
@app.route('/api/login', methods=['POST'])
def login():
    """使用者登入"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '無效的請求資料'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'message': '請輸入帳號和密碼'}), 400
        
        system_data = load_all_data()
        user = system_data['users'].get(username)
        
        if user:
            # 對於管理員帳號，保持原有密碼驗證
            if username == 'Nick20130104':
                if user['password'] == password:
                    session['username'] = username
                    session['is_admin'] = user.get('isAdmin', False)
                    
                    # 初始化活動時間
                    current_time = datetime.now().isoformat()
                    last_activity[username] = {
                        'login': current_time,
                        'public_messages': current_time,
                        'private_messages': current_time,
                        'questions': current_time,
                        'last_check': current_time
                    }
                    
                    return jsonify({
                        'success': True,
                        'message': '登入成功',
                        'user': {
                            'name': user['name'],
                            'isAdmin': user.get('isAdmin', False)
                        }
                    }), 200
            else:
                # 對於其他用戶，檢查是否為加密密碼
                if user['password'].startswith('pbkdf2:'):
                    # 加密密碼驗證
                    if check_password_hash(user['password'], password):
                        session['username'] = username
                        session['is_admin'] = user.get('isAdmin', False)
                        
                        # 初始化活動時間
                        current_time = datetime.now().isoformat()
                        last_activity[username] = {
                            'login': current_time,
                            'public_messages': current_time,
                            'private_messages': current_time,
                            'questions': current_time,
                            'last_check': current_time
                        }
                        
                        return jsonify({
                            'success': True,
                            'message': '登入成功',
                            'user': {
                                'name': user['name'],
                                'isAdmin': user.get('isAdmin', False)
                            }
                        }), 200
                else:
                    # 舊的明文密碼驗證（兼容現有用戶）
                    if user['password'] == password:
                        session['username'] = username
                        session['is_admin'] = user.get('isAdmin', False)
                        
                        # 初始化活動時間
                        current_time = datetime.now().isoformat()
                        last_activity[username] = {
                            'login': current_time,
                            'public_messages': current_time,
                            'private_messages': current_time,
                            'questions': current_time,
                            'last_check': current_time
                        }
                        
                        return jsonify({
                            'success': True,
                            'message': '登入成功',
                            'user': {
                                'name': user['name'],
                                'isAdmin': user.get('isAdmin', False)
                            }
                        }), 200
        
        return jsonify({'success': False, 'message': '帳號或密碼錯誤'}), 401
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤，請稍後再試'}), 500

# 註冊 API
@app.route('/api/register', methods=['POST'])
def register():
    """使用者註冊"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '無效的請求資料'}), 400
        
        name = data.get('name', '').strip()
        school = data.get('school', '').strip()
        email = data.get('email', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        intro = data.get('intro', '').strip()
        
        if not all([name, school, email, username, password]):
            return jsonify({'success': False, 'message': '請完整填寫所有欄位'}), 400
        
        if len(intro) < 50:
            return jsonify({'success': False, 'message': '個人介紹至少需要50字'}), 400
        
        system_data = load_all_data()
        
        if username in system_data['users']:
            return jsonify({'success': False, 'message': '此帳號已被使用，請選擇其他帳號'}), 400
        
        # 對新用戶密碼進行加密
        hashed_password = generate_password_hash(password)
        
        # 建立使用者資料
        system_data['users'][username] = {
            'password': hashed_password,
            'name': name,
            'school': school,
            'email': email,
            'isAdmin': False,
            'intro': intro,
            'anonymous': name,
            'avatar': None,
            'personality': '',
            'hobbies': '',
            'likes': '',
            'created_at': datetime.now().isoformat()
        }
        
        if save_all_data(system_data):
            return jsonify({'success': True, 'message': '註冊成功'}), 200
        else:
            return jsonify({'success': False, 'message': '註冊失敗，請稍後再試'}), 500
            
    except Exception as e:
        logger.error(f"Register error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤，請稍後再試'}), 500

# 刪除訊息 API
@app.route('/api/messages/<message_id>', methods=['DELETE'])
def delete_message(message_id):
    """刪除聊天訊息"""
    try:
        if 'username' not in session:
            return jsonify({'success': False, 'message': '請先登入'}), 401
        
        system_data = load_all_data()
        
        # 找到訊息
        message_index = -1
        for i, msg in enumerate(system_data['messages']):
            if msg['id'] == message_id:
                # 檢查權限：管理員或訊息發送者
                if msg['sender'] != session['username'] and not session.get('is_admin'):
                    return jsonify({'success': False, 'message': '無權刪除此訊息'}), 403
                message_index = i
                break
        
        if message_index == -1:
            return jsonify({'success': False, 'message': '訊息不存在'}), 404
        
        # 刪除訊息
        system_data['messages'].pop(message_index)
        
        if save_all_data(system_data):
            return jsonify({'success': True, 'message': '訊息已刪除'}), 200
        else:
            return jsonify({'success': False, 'message': '刪除失敗'}), 500
            
    except Exception as e:
        logger.error(f"Delete message error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤'}), 500

# 好友系統 API
@app.route('/api/friends', methods=['GET', 'POST', 'DELETE'])
def friends():
    """好友系統"""
    try:
        if 'username' not in session:
            return jsonify({'success': False, 'message': '請先登入'}), 401
        
        system_data = load_all_data()
        friends_data = system_data.get('friends', {})
        
        if request.method == 'GET':
            # 取得好友列表和申請
            user_friends = friends_data.get(session['username'], {})
            return jsonify({
                'success': True,
                'friends': user_friends.get('friends', []),
                'received_requests': user_friends.get('received_requests', []),
                'sent_requests': user_friends.get('sent_requests', [])
            }), 200
        
        elif request.method == 'POST':
            # 發送好友申請
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': '無效的請求資料'}), 400
            
            target_username = data.get('username', '').strip()
            
            if not target_username:
                return jsonify({'success': False, 'message': '請指定用戶'}), 400
            
            if target_username == session['username']:
                return jsonify({'success': False, 'message': '不能加自己為好友'}), 400
            
            if target_username not in system_data['users']:
                return jsonify({'success': False, 'message': '用戶不存在'}), 404
            
            # 初始化數據
            if session['username'] not in friends_data:
                friends_data[session['username']] = {'friends': [], 'received_requests': [], 'sent_requests': []}
            if target_username not in friends_data:
                friends_data[target_username] = {'friends': [], 'received_requests': [], 'sent_requests': []}
            
            # 檢查是否已經是好友
            if any(friend.get('username') == target_username for friend in friends_data[session['username']].get('friends', [])):
                return jsonify({'success': False, 'message': '已經是好友'}), 400
            
            # 檢查是否已經發送過申請
            if any(req.get('from') == session['username'] for req in friends_data[target_username].get('received_requests', [])):
                return jsonify({'success': False, 'message': '已經發送過好友申請'}), 400
            
            # 發送申請
            request_data = {
                'from': session['username'],
                'from_name': system_data['users'][session['username']]['name'],
                'to': target_username,
                'sent_at': datetime.now().isoformat(),
                'sent_time': datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            }
            
            friends_data[target_username].setdefault('received_requests', []).append(request_data)
            friends_data[session['username']].setdefault('sent_requests', []).append({
                'to': target_username,
                'to_name': system_data['users'][target_username]['name'],
                'sent_at': datetime.now().isoformat()
            })
            
            system_data['friends'] = friends_data
            
            if save_all_data(system_data):
                return jsonify({'success': True, 'message': '好友申請已發送'}), 200
            else:
                return jsonify({'success': False, 'message': '發送失敗'}), 500
        
        elif request.method == 'DELETE':
            # 刪除好友
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': '無效的請求資料'}), 400
            
            friend_username = data.get('username', '').strip()
            
            if not friend_username:
                return jsonify({'success': False, 'message': '請指定好友'}), 400
            
            # 從雙方好友列表中移除
            if session['username'] in friends_data and 'friends' in friends_data[session['username']]:
                friends_data[session['username']]['friends'] = [
                    friend for friend in friends_data[session['username']]['friends'] 
                    if friend.get('username') != friend_username
                ]
            
            if friend_username in friends_data and 'friends' in friends_data[friend_username]:
                friends_data[friend_username]['friends'] = [
                    friend for friend in friends_data[friend_username]['friends'] 
                    if friend.get('username') != session['username']
                ]
            
            # 刪除私訊記錄
            chat_key = f"{min(session['username'], friend_username)}_{max(session['username'], friend_username)}"
            if chat_key in system_data['private_messages']:
                del system_data['private_messages'][chat_key]
            
            system_data['friends'] = friends_data
            
            if save_all_data(system_data):
                return jsonify({'success': True, 'message': '好友已刪除'}), 200
            else:
                return jsonify({'success': False, 'message': '刪除失敗'}), 500
                
    except Exception as e:
        logger.error(f"Friends error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤'}), 500

# 處理好友申請 API
@app.route('/api/friends/respond', methods=['POST'])
def respond_friend_request():
    """處理好友申請"""
    try:
        if 'username' not in session:
            return jsonify({'success': False, 'message': '請先登入'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '無效的請求資料'}), 400
        
        from_username = data.get('from_username', '').strip()
        action = data.get('action', '').strip()  # 'accept' or 'reject'
        
        if not from_username or action not in ['accept', 'reject']:
            return jsonify({'success': False, 'message': '無效的參數'}), 400
        
        system_data = load_all_data()
        friends_data = system_data.get('friends', {})
        
        # 從申請列表中移除
        if session['username'] in friends_data and 'received_requests' in friends_data[session['username']]:
            friends_data[session['username']]['received_requests'] = [
                req for req in friends_data[session['username']]['received_requests'] 
                if req.get('from') != from_username
            ]
        
        if from_username in friends_data and 'sent_requests' in friends_data[from_username]:
            friends_data[from_username]['sent_requests'] = [
                req for req in friends_data[from_username]['sent_requests'] 
                if req.get('to') != session['username']
            ]
        
        if action == 'accept':
            # 成為好友
            current_user_info = system_data['users'][session['username']]
            from_user_info = system_data['users'][from_username]
            
            # 初始化好友列表
            if 'friends' not in friends_data[session['username']]:
                friends_data[session['username']]['friends'] = []
            if 'friends' not in friends_data[from_username]:
                friends_data[from_username]['friends'] = []
            
            # 添加好友
            friends_data[session['username']]['friends'].append({
                'username': from_username,
                'name': from_user_info['name'],
                'avatar': from_user_info.get('avatar'),
                'school': from_user_info['school'],
                'became_friends_at': datetime.now().isoformat()
            })
            
            friends_data[from_username]['friends'].append({
                'username': session['username'],
                'name': current_user_info['name'],
                'avatar': current_user_info.get('avatar'),
                'school': current_user_info['school'],
                'became_friends_at': datetime.now().isoformat()
            })
            
            message = '好友申請已接受'
        else:
            message = '好友申請已拒絕'
        
        system_data['friends'] = friends_data
        
        if save_all_data(system_data):
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': '處理失敗'}), 500
            
    except Exception as e:
        logger.error(f"Respond friend request error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤'}), 500

# 添加留言 API
@app.route('/api/questions/comment', methods=['POST'])
def add_comment():
    """添加問題留言"""
    try:
        if 'username' not in session:
            return jsonify({'success': False, 'message': '請先登入'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '無效的請求資料'}), 400
        
        question_id = data.get('question_id', '').strip()
        text = data.get('text', '').strip()
        
        if not question_id or not text:
            return jsonify({'success': False, 'message': '請填寫留言內容'}), 400
        
        system_data = load_all_data()
        questions_data = system_data.get('questions', [])
        
        # 找到問題
        question = None
        for q in questions_data:
            if q['id'] == question_id:
                question = q
                break
        
        if not question:
            return jsonify({'success': False, 'message': '問題不存在'}), 404
        
        # 添加留言
        comment = {
            'id': f"c_{int(time.time() * 1000)}",
            'author': session['username'],
            'text': text,
            'time': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            'timestamp': datetime.now().isoformat()
        }
        
        if 'comments' not in question:
            question['comments'] = []
        
        question['comments'].append(comment)
        system_data['questions'] = questions_data
        
        if save_all_data(system_data):
            return jsonify({'success': True, 'message': '留言已發布', 'comment': comment}), 200
        else:
            return jsonify({'success': False, 'message': '發布失敗'}), 500
            
    except Exception as e:
        logger.error(f"Add comment error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤'}), 500

# 公告系統 API
@app.route('/api/announcements', methods=['GET', 'POST', 'DELETE'])
def announcements():
    """公告系統"""
    try:
        system_data = load_all_data()
        announcements_data = system_data.get('announcements', [])
        
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'announcements': announcements_data
            }), 200
        
        elif request.method == 'POST':
            if 'username' not in session or not session.get('is_admin'):
                return jsonify({'success': False, 'message': '權限不足'}), 403
            
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': '無效的請求資料'}), 400
            
            title = data.get('title', '').strip()
            content = data.get('content', '').strip()
            
            if not title or not content:
                return jsonify({'success': False, 'message': '請填寫標題和內容'}), 400
            
            announcement = {
                'id': f"ann_{int(time.time() * 1000)}",
                'title': title,
                'content': content,
                'author': session['username'],
                'author_name': system_data['users'][session['username']]['name'],
                'created_at': datetime.now().isoformat(),
                'created_time': datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            }
            
            announcements_data.insert(0, announcement)  # 新公告放在最前面
            system_data['announcements'] = announcements_data
            
            if save_all_data(system_data):
                return jsonify({'success': True, 'message': '公告已發布', 'announcement': announcement}), 200
            else:
                return jsonify({'success': False, 'message': '發布失敗'}), 500
        
        elif request.method == 'DELETE':
            if 'username' not in session or not session.get('is_admin'):
                return jsonify({'success': False, 'message': '權限不足'}), 403
            
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': '無效的請求資料'}), 400
            
            announcement_id = data.get('announcement_id', '').strip()
            
            if not announcement_id:
                return jsonify({'success': False, 'message': '請指定公告'}), 400
            
            # 找到公告並刪除
            announcement_index = -1
            for i, ann in enumerate(announcements_data):
                if ann['id'] == announcement_id:
                    announcement_index = i
                    break
            
            if announcement_index == -1:
                return jsonify({'success': False, 'message': '公告不存在'}), 404
            
            announcements_data.pop(announcement_index)
            system_data['announcements'] = announcements_data
            
            if save_all_data(system_data):
                return jsonify({'success': True, 'message': '公告已刪除'}), 200
            else:
                return jsonify({'success': False, 'message': '刪除失敗'}), 500
                
    except Exception as e:
        logger.error(f"Announcements error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤'}), 500

# 心跳 API
@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    """心跳檢測"""
    try:
        if 'username' in session:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'message': '未登入'}), 401
    except Exception as e:
        logger.error(f"Heartbeat error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤'}), 500

# 檢查登入狀態 API
@app.route('/api/check_auth', methods=['GET'])
def check_auth():
    """檢查登入狀態"""
    try:
        if 'username' in session:
            system_data = load_all_data()
            user = system_data['users'].get(session['username'])
            
            if user:
                return jsonify({
                    'success': True,
                    'authenticated': True,
                    'user': {
                        'name': user['name'],
                        'isAdmin': user.get('isAdmin', False)
                    }
                }), 200
        
        return jsonify({
            'success': True,
            'authenticated': False
        }), 200
        
    except Exception as e:
        logger.error(f"Check auth error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤'}), 500

# 登出 API
@app.route('/api/logout', methods=['POST'])
def logout():
    """使用者登出"""
    try:
        username = session.get('username')
        if username in last_activity:
            del last_activity[username]
        if username in last_update_check:
            del last_update_check[username]
        session.clear()
        return jsonify({'success': True, 'message': '已登出'}), 200
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤'}), 500

# 獲取用戶個人資料 API
@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """獲取用戶個人資料"""
    try:
        if 'username' not in session:
            return jsonify({'success': False, 'message': '請先登入'}), 401
        
        system_data = load_all_data()
        user = system_data['users'].get(session['username'])
        
        if not user:
            return jsonify({'success': False, 'message': '用戶不存在'}), 404
        
        return jsonify({
            'success': True,
            'profile': {
                'name': user['name'],
                'school': user['school'],
                'email': user['email'],
                'intro': user.get('intro', ''),
                'anonymous': user.get('anonymous', user['name']),
                'avatar': user.get('avatar'),
                'personality': user.get('personality', ''),
                'hobbies': user.get('hobbies', ''),
                'likes': user.get('likes', '')
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get user profile error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤'}), 500

# 更新用戶個人資料 API
@app.route('/api/user/profile', methods=['PUT'])
def update_user_profile():
    """更新用戶個人資料"""
    try:
        if 'username' not in session:
            return jsonify({'success': False, 'message': '請先登入'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '無效的請求資料'}), 400
        
        system_data = load_all_data()
        user = system_data['users'].get(session['username'])
        
        if not user:
            return jsonify({'success': False, 'message': '用戶不存在'}), 404
        
        # 更新個人資料
        if 'intro' in data:
            if len(data['intro']) < 50:
                return jsonify({'success': False, 'message': '個人介紹至少需要50字'}), 400
            user['intro'] = data['intro']
        
        if 'anonymous' in data:
            user['anonymous'] = data['anonymous']
        
        if 'personality' in data:
            user['personality'] = data['personality']
        
        if 'hobbies' in data:
            user['hobbies'] = data['hobbies']
        
        if 'likes' in data:
            user['likes'] = data['likes']
        
        if 'avatar' in data:
            user['avatar'] = data['avatar']
        
        # 處理密碼變更
        if 'current_password' in data and 'new_password' in data:
            # 對於管理員帳號，保持原有密碼驗證
            if session['username'] == 'Nick20130104':
                if data['current_password'] != user['password']:
                    return jsonify({'success': False, 'message': '當前密碼不正確'}), 400
            else:
                # 對於其他用戶，檢查是否為加密密碼
                if user['password'].startswith('pbkdf2:'):
                    if not check_password_hash(user['password'], data['current_password']):
                        return jsonify({'success': False, 'message': '當前密碼不正確'}), 400
                else:
                    if data['current_password'] != user['password']:
                        return jsonify({'success': False, 'message': '當前密碼不正確'}), 400
            
            if len(data['new_password']) < 6:
                return jsonify({'success': False, 'message': '新密碼長度至少需要6個字符'}), 400
            
            # 對新密碼進行加密（管理員除外）
            if session['username'] == 'Nick20130104':
                user['password'] = data['new_password']
            else:
                user['password'] = generate_password_hash(data['new_password'])
        
        system_data['users'][session['username']] = user
        
        if save_all_data(system_data):
            return jsonify({'success': True, 'message': '個人資料已更新'}), 200
        else:
            return jsonify({'success': False, 'message': '更新失敗'}), 500
            
    except Exception as e:
        logger.error(f"Update user profile error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤'}), 500

# 獲取所有用戶列表 API
@app.route('/api/users', methods=['GET'])
def get_all_users():
    """獲取所有用戶列表"""
    try:
        if 'username' not in session:
            return jsonify({'success': False, 'message': '請先登入'}), 401
        
        system_data = load_all_data()
        
        # 過濾掉當前用戶和密碼等敏感信息
        users_list = []
        for username, user_data in system_data['users'].items():
            if username != session['username']:  # 排除自己
                users_list.append({
                    'username': username,
                    'name': user_data['name'],
                    'school': user_data['school'],
                    'avatar': user_data.get('avatar'),
                    'intro': user_data.get('intro', '')[:100]
                })
        
        return jsonify({
            'success': True,
            'users': users_list
        }), 200
        
    except Exception as e:
        logger.error(f"Get all users error: {e}")
        return jsonify({'success': False, 'message': '系統錯誤'}), 500

# 根路由 - 提供前端頁面
@app.route('/')
def index():
    return app.send_static_file('index.html')

# 靜態文件路由
@app.route('/<path:path>')
def serve_static(path):
    return app.send_static_file(path)

# 數據同步 API
@app.route('/api/sync_data', methods=['GET', 'POST'])
def sync_data():
    """同步前端和後端數據"""
    if request.method == 'GET':
        # 前端獲取所有數據
        system_data = load_all_data()
        return jsonify({
            'success': True,
            'data': system_data
        })
    else:
        # 前端保存數據
        data = request.get_json()
        if save_all_data(data):
            return jsonify({'success': True, 'message': '數據已保存'})
        return jsonify({'success': False, 'message': '保存失敗'})
if __name__ == '__main__':
    # 初始化資料
    load_all_data()
    
    # 啟動伺服器
    logger.info("Starting Flask server...")
    app.run(
        host='0.0.0.0',
        port=int(PORT),
        debug=False
    )