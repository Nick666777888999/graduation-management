import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 修復第4092行的錯誤端點
content = content.replace(
    "fetch('/api/sync-data', {",
    "fetch('https://graduation-management.vercel.app/api/sync-all-data', {"
)

# 檢查是否還有其他錯誤端點
sync_data_count = content.count("'/api/sync-data'")
get_sync_data_count = content.count("'/api/get-sync-data'")

print(f"剩餘 sync-data 端點: {sync_data_count}")
print(f"剩餘 get-sync-data 端點: {get_sync_data_count}")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 所有 API 端點已修復")
