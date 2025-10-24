import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("修復 syncToCloud 數據結構...")

# 正確的 syncToCloud 函數
correct_sync = '''async function syncToCloud() {
    if (!syncEnabled) return;
    
    try {
        // 準備要同步的數據（與後端結構匹配）
        const syncData = {
            student_data: backendData.studentData,
            pending_data: backendData.pendingData,
            announcements: backendData.announcements,
            messages: backendData.chatMessages,
            friends: backendData.friends,
            private_messages: backendData.privateMessages,
            questions: backendData.questions,
            system_config: backendData.systemConfig
        };

        // 發送到雲端
        const response = await fetch('https://graduation-management.vercel.app/api/sync-all-data', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(syncData)
        });
        
        const result = await response.json();
        if (result.success) {
            console.log('數據同步成功');
        }
    } catch (error) {
        console.log('同步失敗，但本地功能正常運作');
    }
}'''

# 替換 syncToCloud 函數
if "async function syncToCloud()" in content:
    pattern = r"async function syncToCloud\\(\\) \\{[^}]+\\}"
    content = re.sub(pattern, correct_sync, content, flags=re.DOTALL)
    print("✅ syncToCloud 數據結構已修復")
else:
    print("❌ 找不到 syncToCloud 函數")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("syncToCloud 修復完成！")
