import os
import json
from supabase import create_client
from datetime import datetime

def migrate_to_supabase():
    # 獲取環境變數
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("錯誤：請設置 SUPABASE_URL 和 SUPABASE_KEY 環境變數")
        return
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("開始遷移數據到 Supabase...")
        
        # 遷移聊天訊息（跳過用戶數據，因為已經存在）
        if os.path.exists('data/messages.json'):
            with open('data/messages.json', 'r', encoding='utf-8') as f:
                messages_data = json.load(f)
                if messages_data:
                    supabase.table('messages').insert(messages_data).execute()
                    print(f"✅ 遷移 {len(messages_data)} 條聊天訊息")
        
        # 遷移公告
        if os.path.exists('data/announcements.json'):
            with open('data/announcements.json', 'r', encoding='utf-8') as f:
                announcements_data = json.load(f)
                if announcements_data:
                    supabase.table('announcements').insert(announcements_data).execute()
                    print(f"✅ 遷移 {len(announcements_data)} 條公告")
        
        # 遷移問題
        if os.path.exists('data/questions.json'):
            with open('data/questions.json', 'r', encoding='utf-8') as f:
                questions_data = json.load(f)
                if questions_data:
                    supabase.table('questions').insert(questions_data).execute()
                    print(f"✅ 遷移 {len(questions_data)} 個問題")
        
        print("🎉 數據遷移完成！")
        
    except Exception as e:
        print(f"❌ 遷移失敗: {e}")

if __name__ == '__main__':
    migrate_to_supabase()
