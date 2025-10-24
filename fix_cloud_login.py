import re

# 讀取 HTML 文件
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 添加雲端註冊函數（在 register 函數之前）
cloud_register_func = '''
// 雲端用戶註冊功能
async function registerToCloud(userData) {
    try {
        const response = await fetch('https://graduation-management.vercel.app/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('註冊失敗:', error);
        return {
            success: false,
            message: '網絡錯誤，請稍後重試'
        };
    }
}
'''

# 在 register 函數前插入
content = content.replace('function register() {', cloud_register_func + '\nfunction register() {')

# 2. 修改 register 函數使用雲端註冊
new_register_func = '''function register() {
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

    // 使用雲端註冊
    registerToCloud({
        name: name,
        school: school,
        email: email,
        username: username,
        password: password,
        intro: intro
    }).then(result => {
        if (result.success) {
            // 雲端註冊成功，也在本地保存
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
            showNotification(result.message, 'success');
            hideRegister();
        } else {
            showNotification(result.message, 'error');
        }
    });
}'''

# 替換 register 函數
pattern = r'function register\(\)\s*\{[^}]+\}'
content = re.sub(pattern, new_register_func, content)

# 保存文件
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 雲端註冊功能添加完成")
