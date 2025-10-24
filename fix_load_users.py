import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("修復 loadFromCloud 用戶數據加載...")

# 新的 loadFromCloud 函數 - 確保用戶數據正確加載
new_load_function = '''async function loadFromCloud() {
    try {
        const response = await fetch('https://graduation-management.vercel.app/api/get-all-data');
        const result = await response.json();
        
        if (result.success && result.data) {
            const cloudData = result.data;
            
            // 重要：合併用戶數據到 backendData.users
            if (cloudData.users) {
                // 保留本地用戶的密碼，合併雲端用戶
                for (const [username, userData] of Object.entries(cloudData.users)) {
                    if (!backendData.users[username]) {
                        // 新用戶從雲端加載
                        backendData.users[username] = userData;
                    } else {
                        // 現有用戶更新信息（保留密碼）
                        const existingUser = backendData.users[username];
                        backendData.users[username] = {
                            ...userData,
                            password: existingUser.password // 保留本地密碼
                        };
                    }
                }
            }
            
            // 合併其他數據
            if (cloudData.student_data) backendData.studentData = cloudData.student_data;
            if (cloudData.pending_data) backendData.pendingData = cloudData.pending_data;
            if (cloudData.announcements) backendData.announcements = cloudData.announcements;
            if (cloudData.messages) backendData.chatMessages = cloudData.messages;
            if (cloudData.friends) backendData.friends = cloudData.friends;
            if (cloudData.private_messages) backendData.privateMessages = cloudData.private_messages;
            if (cloudData.questions) backendData.questions = cloudData.questions;
            if (cloudData.system_config) backendData.systemConfig = cloudData.system_config;
            
            // 保存到本地
            saveBackendData();
            console.log('雲端用戶數據加載成功');
        }
    } catch (error) {
        console.log('雲端數據加載失敗，使用本地數據');
    }
}'''

# 替換 loadFromCloud 函數
if "async function loadFromCloud()" in content:
    pattern = r"async function loadFromCloud\\(\\) \\{[^}]+\\}"
    content = re.sub(pattern, new_load_function, content, flags=re.DOTALL)
    print("✅ 用戶數據加載邏輯已修復")
else:
    print("❌ 找不到 loadFromCloud 函數")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("用戶數據加載修復完成！")
