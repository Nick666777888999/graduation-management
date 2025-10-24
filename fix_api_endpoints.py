import re

# 1. 修復前端使用正確的 API 端點
print("修復前端 API 端點...")
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# 替換所有錯誤的 API 端點
html_content = html_content.replace(
    "fetch('https://graduation-management.vercel.app/api/get-sync-data')",
    "fetch('https://graduation-management.vercel.app/api/get-all-data')"
)

html_content = html_content.replace(
    "fetch('/api/sync-data')",
    "fetch('https://graduation-management.vercel.app/api/sync-all-data')"
)

html_content = html_content.replace(
    "fetch('/api/get-sync-data')", 
    "fetch('https://graduation-management.vercel.app/api/get-all-data')"
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ 前端 API 端點已修復")

# 2. 檢查後端路由
print("檢查後端路由...")
with open('api/index.py', 'r', encoding='utf-8') as f:
    api_content = f.read()

# 檢查必要的路由是否存在
if '/api/sync-all-data' in api_content:
    print("✅ 後端 sync-all-data 路由存在")
else:
    print("❌ 後端缺少 sync-all-data 路由")

if '/api/get-all-data' in api_content:
    print("✅ 後端 get-all-data 路由存在")
else:
    print("❌ 後端缺少 get-all-data 路由")

print("🎉 修復完成")
