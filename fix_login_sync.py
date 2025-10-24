import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("確保登入後立即同步...")

# 在登入成功後立即調用 loadFromCloud
if "loadContent('dashboard');" in content and "loadFromCloud()" not in content:
    content = content.replace(
        "loadContent('dashboard');",
        "loadFromCloud().then(() => {\\n                loadContent('dashboard');\\n            });"
    )
    print("✅ 登入後立即同步已添加")
else:
    print("✅ 登入後同步已存在")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("登入同步修復完成！")
