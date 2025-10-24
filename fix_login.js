// 修复登录函数
function login() {
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
            
            // 切换到主界面
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
}
