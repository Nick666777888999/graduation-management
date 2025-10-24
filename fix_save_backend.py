import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("修復 saveBackendData 調用 syncToCloud...")

# 在 saveBackendData 末尾添加 syncToCloud 調用
if "function saveBackendData()" in content and "syncToCloud();" not in content:
    content = content.replace(
        "    localStorage.setItem('chat_messages', JSON.stringify(backendData.chatMessages));",
        "    localStorage.setItem('chat_messages', JSON.stringify(backendData.chatMessages));\n    \n    // 自動同步到雲端\n    syncToCloud();"
    )
    print("✅ 已添加 syncToCloud 調用到 saveBackendData")
else:
    print("✅ saveBackendData 已經調用 syncToCloud")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("saveBackendData 修復完成！")
