import re

# 读取原始HTML文件
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到并替换登录函数
old_login_function = '''function login() {
      const username = document.getElementById('username').value;
      const password = document.getElementById('password').value;
      const errorMsg = document.getElementById('error-msg');
      
      if (!username || !password) {
        errorMsg.textContent = '請輸入帳號和密碼';
        return;
      }
      
      const user = backendData.users[username];
      
      if (user && user.password === password) {
        currentUser = username;
        isAdmin = user.isAdmin || false;
        
        document.getElementById('login-screen').style.display = 'none';
        document.getElementById('main-screen').style.display = 'block';
        document.getElementById('current-user-name').textContent = user.name;
        
        if (isAdmin) {
          document.getElementById('admin-badge').style.display = 'inline-block';
          document.getElementById('admin-tools').style.display = 'block';
          document.getElementById('review-btn').style.display = 'block';
          document.getElementById('statistics-btn').style.display = 'block';
        }
        
        loadContent('dashboard');
        
        
        // 開始實時更新
        startRealTimeUpdates();
      } else {
        errorMsg.textContent = '帳號或密碼錯誤';
      }
    }'''

new_login_function = '''function login() {
      const username = document.getElementById('username').value;
      const password = document.getElementById('password').value;
      const errorMsg = document.getElementById('error-msg');
      
      if (!username || !password) {
        errorMsg.textContent = '請輸入帳號和密碼';
        return;
      }
      
      // 显示加载状态
      errorMsg.textContent = '登入中...';
      errorMsg.style.color = '#008B8B';
      
      // 调用云端API登录
      fetch('https://graduation-management.vercel.app/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // 登录成功
          errorMsg.textContent = '';
          
          // 保存用户信息到本地
          if (!backendData.users[username]) {
            backendData.users[username] = {
              password: password,
              name: data.user.name,
              school: '未知学校',
              email: username + '@gmail.com',
              isAdmin: data.user.isAdmin || false
            };
            saveBackendData();
          }
          
          currentUser = username;
          isAdmin = data.user.isAdmin || false;
          
          document.getElementById('login-screen').style.display = 'none';
          document.getElementById('main-screen').style.display = 'block';
          document.getElementById('current-user-name').textContent = data.user.name;
          
          if (isAdmin) {
            document.getElementById('admin-badge').style.display = 'inline-block';
            document.getElementById('admin-tools').style.display = 'block';
            document.getElementById('review-btn').style.display = 'block';
            document.getElementById('statistics-btn').style.display = 'block';
          }
          
          loadContent('dashboard');
          startRealTimeUpdates();
          
        } else {
          // 登录失败
          errorMsg.textContent = data.message || '登入失敗';
          errorMsg.style.color = '#e74c3c';
        }
      })
      .catch(error => {
        console.error('登入錯誤:', error);
        errorMsg.textContent = '網絡錯誤，請稍後再試';
        errorMsg.style.color = '#e74c3c';
      });
    }'''

# 替换登录函数
content = content.replace(old_login_function, new_login_function)

# 保存修复后的文件
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 前端登录函数已修复")
