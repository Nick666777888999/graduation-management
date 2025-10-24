import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("修復 loadFromCloud 數據合併...")

# 正確的 loadFromCloud 函數
new_load_function = '''async function loadFromCloud() {
    try {
        const response = await fetch('https://graduation-management.vercel.app/api/get-all-data');
        const result = await response.json();
        
        if (result.success && result.data) {
            // 合併所有雲端數據到本地
            const data = result.data;
            
            // 合併用戶數據（保留本地密碼）
            if (data.users) {
                for (const [username, userData] of Object.entries(data.users)) {
                    if (!backendData.users[username]) {
                        backendData.users[username] = {
                            ...userData,
                            password: userData.password || 'default'
                        };
                    }
                }
            }
            
            // 合併其他數據（雲端優先）
            if (data.student_data) backendData.studentData = data.student_data;
            if (data.pending_data) backendData.pendingData = data.pending_data;
            if (data.announcements) backendData.announcements = data.announcements;
            if (data.messages) backendData.chatMessages = data.messages;
            if (data.friends) backendData.friends = data.friends;
            if (data.private_messages) backendData.privateMessages = data.private_messages;
            if (data.questions) backendData.questions = data.questions;
            if (data.system_config) backendData.systemConfig = data.system_config;
            
            // 保存到本地存儲
            saveBackendData();
            console.log('雲端數據加載並合併成功');
        }
    } catch (error) {
        console.log('雲端數據加載失敗，使用本地數據');
    }
}'''

# 替換 loadFromCloud 函數
if "async function loadFromCloud()" in content:
    pattern = r"async function loadFromCloud\\(\\) \\{[^}]+\\}"
    content = re.sub(pattern, new_load_function, content, flags=re.DOTALL)
    print("✅ loadFromCloud 數據合併已修復")
else:
    print("❌ 找不到 loadFromCloud 函數")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("loadFromCloud 修復完成！")
