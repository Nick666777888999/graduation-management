import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 將 get-sync-data 替換為 get-all-data
content = content.replace(
    "fetch('https://graduation-management.vercel.app/api/get-sync-data')",
    "fetch('https://graduation-management.vercel.app/api/get-all-data')"
)

# 修復 sync-all-data 的調用
content = content.replace(
    "fetch('/api/sync-data')",
    "fetch('https://graduation-management.vercel.app/api/sync-all-data')"
)

content = content.replace(
    "fetch('/api/get-sync-data')", 
    "fetch('https://graduation-management.vercel.app/api/get-all-data')"
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 前端 API 端點已修復")
