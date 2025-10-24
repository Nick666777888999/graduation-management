import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 修復 register 函數中的 showNotification 調用
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

# 替換 register 函數
pattern = r'function register\\(\\) \\{[^}]+\\}'
content = re.sub(pattern, new_register_func, content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ register 函數已修復")
