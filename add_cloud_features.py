import re

# 讀取備份文件
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("開始安全添加雲端功能...")

# 1. 在 register 函數前添加雲端註冊輔助函數
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

# 找到 register 函數的位置並在前面插入
register_pos = content.find('function register() {')
if register_pos != -1:
    content = content[:register_pos] + cloud_register_func + '\\n' + content[register_pos:]
    print("✅ 已添加雲端註冊函數")
else:
    print("❌ 找不到 register 函數")

# 2. 修改現有的 register 函數使用雲端註冊
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
    
    if (backendData.users[username]) {
        showNotification('此帳號已被使用，請選擇其他帳號', 'error');
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
old_register_pattern = r'function register\\(\\) \\{[^}]+\\}'
if re.search(old_register_pattern, content):
    content = re.sub(old_register_pattern, new_register_func, content)
    print("✅ 已修改 register 函數使用雲端註冊")
else:
    print("❌ 替換 register 函數失敗")

# 3. 添加雲端數據加載函數（在合適位置）
cloud_load_func = '''
// 從雲端加載數據
async function loadCloudData() {
    try {
        const response = await fetch('https://graduation-management.vercel.app/api/get-all-data');
        const result = await response.json();
        
        if (result.success) {
            // 合併雲端數據到本地
            if (result.data.users) {
                backendData.users = { ...backendData.users, ...result.data.users };
            }
            console.log('雲端數據加載成功');
        }
    } catch (error) {
        console.log('雲端數據加載失敗，使用本地數據');
    }
}
'''

# 在 login 函數前插入雲端加載函數
login_pos = content.find('function login() {')
if login_pos != -1:
    content = content[:login_pos] + cloud_load_func + '\\n' + content[login_pos:]
    print("✅ 已添加雲端數據加載函數")
else:
    print("❌ 找不到 login 函數")

# 保存修改後的文件
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("🎉 雲端功能添加完成！")
print("📁 文件已保存，請檢查修改結果")
