import re

# 讀取文件
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 修復被截斷的 register 函數
# 找到不完整的 register 函數並修復
if 'hideRegister();\n    }\n\n    // 載入內容' in content:
    # 修復被截斷的代碼
    content = content.replace(
        'hideRegister();\n    }\n\n    // 載入內容',
        'hideRegister();\n    }\n}\n\n    // 載入內容'
    )

# 確保所有函數都有正確的結束括號
# 檢查 register 函數是否完整
register_pattern = r'function register\(\)\s*\{[^}]+\}'
if not re.search(register_pattern, content):
    print("⚠️  register 函數不完整，需要修復")
    
    # 添加完整的 register 函數
    complete_register = '''function register() {
    const name = document.getElementById('reg-name').value.trim();
    const school = document.getElementById('reg-school').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const username = document.getElementById('reg-username').value.trim();
    const password = document.getElementById('reg-password').value.trim();
    const intro = document.getElementById('reg-intro').value.trim();

    if (!name || !school || !email || !username || !password) {
        showNotification('請完整填寫所有欄位', 'error');
        return;
    }
    
    if (!email.includes('@gmail.com')) {
        showNotification('請輸入正確的 Gmail', 'error');
        return;
    }
    
    if (intro.length < 50) {
        showNotification('個人介紹至少需要50字', 'error');
        return;
    }
    
    if (backendData.users[username]) {
        showNotification('此帳號已被使用，請選擇其他帳號', 'error');
        return;
    }

    // 儲存使用者資料
    backendData.users[username] = {
        password: password,
        name: name,
        school: school,
        email: email,
        isAdmin: false,
        intro: intro,
        anonymous: name,
        avatar: null,
        personality: '',
        hobbies: '',
        likes: ''
    };
    
    saveBackendData();
    showNotification('註冊成功，請登入', 'success');
    hideRegister();
}'''
    
    # 替換不完整的 register 函數
    content = re.sub(r'function register\(\)\s*\{[^}]*$', complete_register, content)

# 保存修復後的文件
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 代碼修復完成")
