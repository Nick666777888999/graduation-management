import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("修復登入邏輯，使用雲端驗證...")

# 新的 login 函數 - 完全使用雲端驗證
new_login_function = '''function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMsg = document.getElementById('error-msg');
    
    if (!username || !password) {
        errorMsg.textContent = '請輸入帳號和密碼';
        return;
    }
    
    // 使用雲端 API 驗證登入
    fetch('https://graduation-management.vercel.app/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            // 登入成功
            currentUser = username;
            isAdmin = result.user.isAdmin;
            
            document.getElementById('login-screen').style.display = 'none';
            document.getElementById('main-screen').style.display = 'block';
            document.getElementById('current-user-name').textContent = result.user.name;
            
            if (isAdmin) {
                document.getElementById('admin-badge').style.display = 'inline-block';
                document.getElementById('admin-tools').style.display = 'block';
                document.getElementById('review-btn').style.display = 'block';
                document.getElementById('statistics-btn').style.display = 'block';
            }
            
            // 從雲端加載所有數據
            loadFromCloud().then(() => {
                loadContent('dashboard');
                showNotification(`歡迎回來，${result.user.name}！`, 'success');
                startRealTimeUpdates();
            });
            
        } else {
            errorMsg.textContent = result.message;
        }
    })
    .catch(error => {
        errorMsg.textContent = '網絡錯誤，請稍後重試';
    });
}'''

# 替換 login 函數
if "function login()" in content:
    pattern = r"function login\\(\\) \\{[^}]+\\}"
    content = re.sub(pattern, new_login_function, content, flags=re.DOTALL)
    print("✅ 登入邏輯已修復為雲端驗證")
else:
    print("❌ 找不到 login 函數")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("登入修復完成！")
