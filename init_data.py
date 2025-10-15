import json
import os

def init_data():
    """初始化數據文件"""
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    
    # 初始化用戶數據
    users_file = os.path.join(data_dir, 'users.json')
    if not os.path.exists(users_file):
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
    
    # 初始化學生數據
    student_data_file = os.path.join(data_dir, 'student_data.json')
    if not os.path.exists(student_data_file):
        with open(student_data_file, 'w', encoding='utf-8') as f:
            json.dump({
                'primary': [],
                'junior': [], 
                'high': [],
                'other': []
            }, f, ensure_ascii=False, indent=2)
    
    # 初始化其他數據文件
    files = {
        'messages.json': [],
        'pending_data.json': [],
        'announcements.json': [],
        'friends.json': {},
        'private_messages.json': {},
        'questions.json': []
    }
    
    for filename, default_data in files.items():
        file_path = os.path.join(data_dir, filename)
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
    
    print("✅ 數據文件初始化完成")

if __name__ == '__main__':
    init_data()