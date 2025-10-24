import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("修復 loadFromCloud 數據結構...")

# 正確的 loadFromCloud 函數
correct_load = '''async function loadFromCloud() {
    try {
        const response = await fetch('https://graduation-management.vercel.app/api/get-all-data');
        const result = await response.json();
        
        if (result.success && result.data) {
            const cloudData = result.data;
            
            // 合併用戶數據（重要：確保用戶數據同步）
            if (cloudData.users) {
                // 合併到 backendData.users
                for (const [username, userData] of Object.entries(cloudData.users)) {
                    if (!backendData.users[username]) {
                        backendData.users[username] = userData;
                    }
                }
            }
            
            // 合併其他數據（與後端結構匹配）
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
            console.log('雲端數據加載並合併成功');
        }
    } catch (error) {
        console.log('雲端數據加載失敗，使用本地數據');
    }
}'''

# 替換 loadFromCloud 函數
if "async function loadFromCloud()" in content:
    pattern = r"async function loadFromCloud\\(\\) \\{[^}]+\\}"
    content = re.sub(pattern, correct_load, content, flags=re.DOTALL)
    print("✅ loadFromCloud 數據結構已修復")
else:
    print("❌ 找不到 loadFromCloud 函數")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("loadFromCloud 修復完成！")
