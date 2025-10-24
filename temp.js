    // 全域變數
    let currentUser = null;
    let isAdmin = false;
    let currentPage = 'dashboard';
    let captchaVerified = false;
    
    // 實時更新相關變數
    let updateInterval = null;
    let lastUpdateCheck = 0;
    let isCheckingUpdates = false;

    // 模擬後端數據庫
    const backendData = {
      users: JSON.parse(localStorage.getItem('backend_users') || '{}'),
      studentData: {
        primary: JSON.parse(localStorage.getItem('backend_primary') || '[]'),
        junior: JSON.parse(localStorage.getItem('backend_junior') || '[]'),
        high: JSON.parse(localStorage.getItem('backend_high') || '[]'),
        other: JSON.parse(localStorage.getItem('backend_other') || '[]')
      },
      pendingData: JSON.parse(localStorage.getItem('backend_pending') || '[]'),
      announcements: JSON.parse(localStorage.getItem('announcements') || '[]'),
      systemConfig: JSON.parse(localStorage.getItem('system_config') || '{}'),
      friends: JSON.parse(localStorage.getItem('friends_data') || '{}'),
      privateMessages: JSON.parse(localStorage.getItem('private_messages') || '{}'),
      questions: JSON.parse(localStorage.getItem('questions_data') || '[]'),
      chatMessages: JSON.parse(localStorage.getItem('chat_messages') || '[]')
    };

    // 初始化
    document.addEventListener('DOMContentLoaded', function() {
      // 檢查是否有預設管理員帳號
      if (!backendData.users['Nick20130104']) {
        backendData.users['Nick20130104'] = {
          password: 'Nick20130104',
          name: '系統管理員',
          school: '管理學校',
          email: 'admin@system.com',
          isAdmin: true,
          intro: '我是系統管理員，負責管理畢業資料系統。',
          anonymous: '管理員',
          avatar: null,
          personality: '認真負責、細心嚴謹',
          hobbies: '系統管理、程式設計',
          likes: '解決問題、學習新技術'
        };
        saveBackendData();
      }

      // 初始化科目選擇
      initSubjectTags();
    });

    // 初始化科目標籤
    function initSubjectTags() {
      const tags = document.querySelectorAll('.subject-tag');
      tags.forEach(tag => {
        tag.addEventListener('click', function() {
          tags.forEach(t => t.classList.remove('selected'));
          this.classList.add('selected');
          document.getElementById('selected-subject').value = this.dataset.subject;
        });
      });
    }

    // 保存後端數據
    function saveBackendData() {
      localStorage.setItem('backend_users', JSON.stringify(backendData.users));
      localStorage.setItem('backend_primary', JSON.stringify(backendData.studentData.primary));
      localStorage.setItem('backend_junior', JSON.stringify(backendData.studentData.junior));
      localStorage.setItem('backend_high', JSON.stringify(backendData.studentData.high));
      localStorage.setItem('backend_other', JSON.stringify(backendData.studentData.other));
      localStorage.setItem('backend_pending', JSON.stringify(backendData.pendingData));
      localStorage.setItem('announcements', JSON.stringify(backendData.announcements));
      localStorage.setItem('system_config', JSON.stringify(backendData.systemConfig));
      localStorage.setItem('friends_data', JSON.stringify(backendData.friends));
      localStorage.setItem('private_messages', JSON.stringify(backendData.privateMessages));
      localStorage.setItem('questions_data', JSON.stringify(backendData.questions));
      localStorage.setItem('chat_messages', JSON.stringify(backendData.chatMessages));
    }

    // 顯示通知
    function showNotification(message, type = 'info') {
      const notification = document.getElementById('notification');
      notification.textContent = message;
      notification.className = `notification ${type}`;
      notification.classList.add('show');
      
      setTimeout(() => {
        notification.classList.remove('show');
      }, 3000);
    }

    // 字數計數器
    function countChars(textareaId, counterId) {
      const textarea = document.getElementById(textareaId);
      const counter = document.getElementById(counterId);
      const count = textarea.value.length;
      counter.textContent = `${count}/${textareaId === 'question-text' ? '150' : '50'}`;
      
      if ((textareaId === 'question-text' && count > 150) || 
          (textareaId !== 'question-text' && count < 50)) {
        counter.classList.add('warning');
      } else {
        counter.classList.remove('warning');
      }
    }

    // 顯示管理員登入
    function showAdminLogin() {
      document.getElementById('login-screen').style.display = 'none';
      document.getElementById('admin-login-screen').style.display = 'flex';
    }

    // 隱藏管理員登入
    function hideAdminLogin() {
      document.getElementById('admin-login-screen').style.display = 'none';
      document.getElementById('login-screen').style.display = 'flex';
      document.getElementById('captcha-check').checked = false;
      captchaVerified = false;
    }

    // 機器人驗證切換
    function toggleCaptcha() {
      const captchaCheck = document.getElementById('captcha-check');
      captchaCheck.checked = !captchaCheck.checked;
      captchaVerified = captchaCheck.checked;
    }

    // 管理員登入
    function adminLogin() {
      const username = document.getElementById('admin-username').value;
      const password = document.getElementById('admin-password').value;
      const errorMsg = document.getElementById('admin-error-msg');
      
      if (!username || !password) {
        errorMsg.textContent = '請輸入帳號和密碼';
        return;
      }
      
      if (!captchaVerified) {
        errorMsg.textContent = '請確認您不是機器人';
        return;
      }
      
      const user = backendData.users[username];
      
      if (user && user.password === password && user.isAdmin) {
        currentUser = username;
        isAdmin = true;
        
        document.getElementById('admin-login-screen').style.display = 'none';
        document.getElementById('main-screen').style.display = 'block';
        document.getElementById('current-user-name').textContent = user.name;
        document.getElementById('admin-badge').style.display = 'inline-block';
        document.getElementById('admin-tools').style.display = 'block';
        document.getElementById('review-btn').style.display = 'block';
        document.getElementById('statistics-btn').style.display = 'block';
        
        loadContent('dashboard');
        
        
        // 開始實時更新
        startRealTimeUpdates();
      } else {
        errorMsg.textContent = '管理員帳號或密碼錯誤';
      }
    }

    // 登入功能
    
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
\nfunction login() {
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
    }

    // 實時通訊修復 - 開始實時更新
    function startRealTimeUpdates() {
      if (updateInterval) clearInterval(updateInterval);
      
      // 每5秒檢查一次更新（降低頻率）
      updateInterval = setInterval(checkForUpdates, 5000);
      console.log('實時更新已啟動');
    }

    // 檢查更新 - 修復版本
    async function checkForUpdates() {
      if (!currentUser || isCheckingUpdates) return;
      
      isCheckingUpdates = true;
      try {
        const updates = await simulateCheckUpdates();
        if (updates && !updates.no_updates) {
          handleUpdates(updates);
        }
      } catch (error) {
        console.error('檢查更新失敗:', error);
      } finally {
        isCheckingUpdates = false;
      }
    }

    // 模擬檢查更新API - 修復版本
    function simulateCheckUpdates() {
      return new Promise((resolve) => {
        setTimeout(() => {
          const updates = {
            success: true,
            new_private_messages: checkNewPrivateMessages(),
            pending_friend_requests: checkNewFriendRequests(),
            new_public_messages: checkNewPublicMessages(),
            new_questions: checkNewQuestions(),
            timestamp: Date.now()
          };
          
          // 如果沒有任何更新，標記為無更新
          if (updates.new_private_messages === 0 && 
              updates.pending_friend_requests === 0 && 
              updates.new_public_messages === 0 && 
              updates.new_questions === 0) {
            updates.no_updates = true;
          }
          
          resolve(updates);
        }, 500);
      });
    }

    // 檢查新私訊
    function checkNewPrivateMessages() {
      if (!currentUser) return 0;
      
      const userFriends = backendData.friends[currentUser] || { friends: [] };
      let newMessages = 0;
      
      userFriends.friends?.forEach(friend => {
        const chatKey = getChatKey(currentUser, friend.username);
        const messages = backendData.privateMessages[chatKey] || [];
        
        // 計算未讀消息
        messages.forEach(msg => {
          if (msg.from !== currentUser && !msg.read) {
            newMessages++;
          }
        });
      });
      
      return newMessages;
    }

    // 檢查新好友申請
    function checkNewFriendRequests() {
      if (!currentUser) return 0;
      const userData = backendData.friends[currentUser] || {};
      return userData.received_requests?.length || 0;
    }

    // 檢查新公共消息 - 修復版本
    function checkNewPublicMessages() {
      const messages = backendData.chatMessages;
      if (messages.length === 0) return 0;
      
      // 檢查最後一條消息是否來自其他用戶且是新的
      const lastMessage = messages[messages.length - 1];
      const isNewMessage = lastMessage.sender !== currentUser && 
                          (!lastMessage.timestamp || lastMessage.timestamp > lastUpdateCheck);
      
      return isNewMessage ? 1 : 0;
    }

    // 檢查新問題 - 修復版本
    function checkNewQuestions() {
      const questions = backendData.questions;
      if (questions.length === 0) return 0;
      
      // 檢查最新問題是否來自其他用戶且是新的
      const latestQuestion = questions[0];
      const isNewQuestion = latestQuestion.author !== currentUser && 
                           (!latestQuestion.created_at || latestQuestion.created_at > lastUpdateCheck);
      
      return isNewQuestion ? 1 : 0;
    }

    // 處理更新 - 修復版本
    function handleUpdates(updateData) {
      if (!updateData.success) return;
      
      // 更新最後檢查時間
      lastUpdateCheck = updateData.timestamp;
      
      // 處理新私訊
      if (updateData.new_private_messages > 0 && currentPage !== 'friends') {
        
      }
      
      // 處理好友申請
      if (updateData.pending_friend_requests > 0 && currentPage !== 'friends') {
        
      }
      
      // 處理公共聊天室新消息
      if (updateData.new_public_messages > 0 && currentPage !== 'chat') {
        
      }
      
      // 處理新問題 - 修復：管理員不會收到自己問題的通知
      if (updateData.new_questions > 0 && currentPage !== 'questions') {
        
      }
      
      // 如果當前在相關頁面，自動刷新內容
      if (currentPage === 'friends') {
        loadFriendRequests();
        loadFriendsList();
        const friendSelect = document.getElementById('private-chat-friend');
        if (friendSelect && friendSelect.value) {
          loadPrivateMessages(friendSelect.value);
        }
      } else if (currentPage === 'chat') {
        loadChat();
      } else if (currentPage === 'questions') {
        loadQuestions();
      }
    }

    // 更新活動時間
    function updateActivity(type) {
      console.log(`更新活動時間: ${type}`);
    }

    // 登出功能
    function logout() {
      // 清除輪詢
      if (updateInterval) clearInterval(updateInterval);
      
      document.getElementById('login-screen').style.display = 'flex';
      document.getElementById('main-screen').style.display = 'none';
      document.getElementById('username').value = '';
      document.getElementById('password').value = '';
      document.getElementById('error-msg').textContent = '';
      document.getElementById('admin-badge').style.display = 'none';
      document.getElementById('admin-tools').style.display = 'none';
      document.getElementById('review-btn').style.display = 'none';
      document.getElementById('statistics-btn').style.display = 'none';
      document.getElementById('floating-action-btn').style.display = 'none';
      currentUser = null;
      isAdmin = false;
    }

    // 顯示註冊頁面
    function showRegister() {
      document.getElementById('login-screen').style.display = 'none';
      document.getElementById('register-screen').style.display = 'flex';
    }

    // 隱藏註冊頁面
    function hideRegister() {
      document.getElementById('register-screen').style.display = 'none';
      document.getElementById('login-screen').style.display = 'flex';
    }

    // 註冊功能
    
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
\nfunction register() {
      const name = document.getElementById('reg-name').value.trim();
      const school = document.getElementById('reg-school').value.trim();
      const email = document.getElementById('reg-email').value.trim();
      const username = document.getElementById('reg-username').value.trim();
      const password = document.getElementById('reg-password').value.trim();
      const intro = document.getElementById('reg-intro').value.trim();

      if (!name || !school || !email || !username || !password) {
        
        return;
      }
      
      if (!email.includes('@gmail.com')) {
        
        return;
      }
      
      if (intro.length < 50) {
        
        return;
      }
      
      if (backendData.users[username]) {
        
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
      
      hideRegister();
    }

    // 載入內容
    function loadContent(page) {
      currentPage = page;
      
      // 更新側邊欄按鈕狀態
      document.querySelectorAll('.side-bar button').forEach(btn => {
        btn.classList.remove('active');
      });
      event.currentTarget.classList.add('active');
      
      // 顯示/隱藏浮動按鈕
      const fab = document.getElementById('floating-action-btn');
      if (page === 'questions') {
        fab.style.display = 'flex';
      } else {
        fab.style.display = 'none';
      }
      
      const content = document.getElementById('content-area');
      
      switch(page) {
        case 'dashboard':
          renderDashboard();
          break;
        case 'announcements':
          renderAnnouncements();
          break;
        case 'primary':
          renderStudentData('primary', '國小學生');
          break;
        case 'junior':
          renderStudentData('junior', '國中學生');
          break;
        case 'high':
          renderStudentData('high', '高中學生');
          break;
        case 'data-entry':
          renderDataForm();
          break;
        case 'other':
          renderStudentData('other', '其他年級');
          break;
        case 'search':
          renderSearch();
          break;
        case 'review':
          renderReview();
          break;
        case 'statistics':
          renderStatistics();
          break;
        case 'chat':
          renderChat();
          break;
        case 'questions':
          renderQuestions();
          break;
        case 'friends':
          renderFriends();
          break;
        case 'system_config':
          renderSystemConfig();
          break;
      }
    }

    // 儀表板
    function renderDashboard() {
      const content = document.getElementById('content-area');
      const user = backendData.users[currentUser];
      
      // 計算統計數據
      const totalStudents = 
        backendData.studentData.primary.length + 
        backendData.studentData.junior.length + 
        backendData.studentData.high.length + 
        backendData.studentData.other.length;
      
      content.innerHTML = `
        <div class="content-card">
          <h2><i class="fas fa-tachometer-alt"></i> 系統儀表板</h2>
          
          <div class="stats-container">
            <div class="stat-card">
              <i class="fas fa-user-graduate"></i>
              <div class="number">${totalStudents}</div>
              <div class="label">總學生數</div>
            </div>
            <div class="stat-card">
              <i class="fas fa-child"></i>
              <div class="number">${backendData.studentData.primary.length}</div>
              <div class="label">國小學生</div>
            </div>
            <div class="stat-card">
              <i class="fas fa-user-graduate"></i>
              <div class="number">${backendData.studentData.junior.length}</div>
              <div class="label">國中學生</div>
            </div>
            <div class="stat-card">
              <i class="fas fa-user-tie"></i>
              <div class="number">${backendData.studentData.high.length}</div>
              <div class="label">高中學生</div>
            </div>
          </div>
          
          <!-- 個人介紹區域 -->
          <div class="personal-intro">
            <h4><i class="fas fa-user"></i> 個人介紹</h4>
            <div class="intro-text">${user.intro || '您還沒有填寫個人介紹，請點擊編輯按鈕新增。'}</div>
            <button class="edit-intro-btn" onclick="showProfileModal()"><i class="fas fa-edit"></i> 編輯個人資料</button>
          </div>
          
          <div class="announcement">
            <h3><i class="fas fa-bullhorn"></i> 最新公告</h3>
            ${backendData.announcements.length > 0 ? 
              `<p><strong>${backendData.announcements[0].title}</strong></p>
               <p>${backendData.announcements[0].content}</p>
               <p style="color:#666; font-size:14px;">發布時間: ${backendData.announcements[0].created_time}</p>` :
              '<p>目前沒有任何公告</p>'
            }
            ${isAdmin ? '<p style="color:#ff9800; font-weight:bold;">您目前以管理員身份登入，擁有系統管理權限。</p>' : ''}
          </div>
        </div>
      `;
    }

    // 系統公告
    function renderAnnouncements() {
      const content = document.getElementById('content-area');
      
      let adminControls = '';
      if (isAdmin) {
        adminControls = `
          <div class="content-card">
            <h2><i class="fas fa-edit"></i> 發布新公告</h2>
            <div class="form-group">
              <label for="announcement-title">標題</label>
              <input type="text" id="announcement-title" class="form-control" placeholder="輸入公告標題">
            </div>
            <div class="form-group">
              <label for="announcement-content">內容</label>
              <textarea id="announcement-content" class="form-control" rows="4" placeholder="輸入公告內容"></textarea>
            </div>
            <button onclick="publishAnnouncement()" class="login-box button">
              <i class="fas fa-paper-plane"></i> 發布公告
            </button>
          </div>
        `;
      }
      
      content.innerHTML = `
        <div class="content-card">
          <h2><i class="fas fa-bullhorn"></i> 系統公告</h2>
        </div>
        ${adminControls}
        <div class="content-card">
          <h3><i class="fas fa-list"></i> 公告列表</h3>
          <div id="announcements-list"></div>
        </div>
      `;
      
      loadAnnouncements();
    }

    // 載入公告
    function loadAnnouncements() {
      const announcements = backendData.announcements;
      displayAnnouncements(announcements);
    }

    // 顯示公告
    function displayAnnouncements(announcements) {
      const container = document.getElementById('announcements-list');
      
      if (announcements.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-bullhorn"></i><h3>目前沒有任何公告</h3><p>管理員發布公告後會顯示在這裡</p></div>';
        return;
      }
      
      container.innerHTML = announcements.map((announcement, index) => `
        <div class="announcement">
          ${isAdmin ? `
            <div class="announcement-actions">
              <button class="delete-announcement" onclick="deleteAnnouncement(${index})">
                <i class="fas fa-trash"></i> 刪除
              </button>
            </div>
          ` : ''}
          <h3>${announcement.title}</h3>
          <p>${announcement.content}</p>
          <div style="display:flex; justify-content:space-between; margin-top:10px; color:#666; font-size:14px;">
            <span>發布者: ${announcement.author_name}</span>
            <span>時間: ${announcement.created_time}</span>
          </div>
        </div>
      `).join('');
    }

    // 發布公告
    function publishAnnouncement() {
      const title = document.getElementById('announcement-title').value.trim();
      const content = document.getElementById('announcement-content').value.trim();
      
      if (!title || !content) {
        
        return;
      }
      
      const user = backendData.users[currentUser];
      
      const announcement = {
        id: Date.now(),
        title: title,
        content: content,
        author: currentUser,
        author_name: user.name,
        created_at: new Date().toISOString(),
        created_time: new Date().toLocaleString('zh-TW')
      };
      
      backendData.announcements.unshift(announcement);
      saveBackendData();
      
      
      document.getElementById('announcement-title').value = '';
      document.getElementById('announcement-content').value = '';
      loadAnnouncements();
    }

    // 刪除公告
    function deleteAnnouncement(index) {
      if (confirm('確定要刪除這則公告嗎？')) {
        backendData.announcements.splice(index, 1);
        saveBackendData();
        
        loadAnnouncements();
      }
    }

    // 資料填寫表單
    function renderDataForm() {
      const content = document.getElementById('content-area');
      content.innerHTML = `
        <div class="content-card">
          <h2><i class="fas fa-edit"></i> 資料填寫</h2>
          <p>請填寫以下畢業生資料，所有欄位皆為必填。</p>
          
          <div class="form-group">
            <label for="form-name">姓名</label>
            <input type="text" id="form-name" class="form-control" placeholder="請輸入姓名">
          </div>
          
          <div class="form-group">
            <label for="form-school">學校</label>
            <input type="text" id="form-school" class="form-control" placeholder="請輸入學校名稱">
          </div>
          
          <div class="form-group">
            <label for="form-gmail">Gmail</label>
            <input type="email" id="form-gmail" class="form-control" placeholder="請輸入Gmail">
          </div>
          
          <div class="form-group">
            <label for="form-level">教育階段</label>
            <select id="form-level" class="form-control">
              <option value="primary">國小</option>
              <option value="junior">國中</option>
              <option value="high">高中</option>
              <option value="other">大學/研究所/博士</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="form-grade">年級</label>
            <input type="text" id="form-grade" class="form-control" placeholder="請輸入年級（例如：六年級）">
          </div>
          
          <div class="form-group">
            <label for="form-personality">個性特質</label>
            <input type="text" id="form-personality" class="form-control" placeholder="例如：活潑開朗、細心負責">
          </div>
          
          <div class="form-group">
            <label for="form-hobbies">興趣愛好</label>
            <input type="text" id="form-hobbies" class="form-control" placeholder="例如：閱讀、運動、音樂">
          </div>
          
          <div class="form-group">
            <label for="form-likes">喜歡的事物</label>
            <input type="text" id="form-likes" class="form-control" placeholder="例如：貓咪、旅行、美食">
          </div>
          
          <div class="form-group">
            <label for="form-intro">個人介紹 (至少50字)</label>
            <textarea id="form-intro" class="form-control" rows="4" placeholder="請詳細介紹自己..." oninput="countChars('form-intro', 'form-char-count')"></textarea>
            <div id="form-char-count" class="char-counter">0/50</div>
          </div>
          
          <div class="form-group">
            <label for="form-avatar">上傳頭像</label>
            <input type="file" id="form-avatar" class="form-control" accept="image/*">
          </div>
          
          <div class="checkbox-group">
            <input type="checkbox" id="agree-checkbox">
            <label for="agree-checkbox">我同意提供所有填寫資料公開</label>
          </div>
          
          <button onclick="submitFormData()" class="login-box button" style="width:auto; padding:10px 20px;"><i class="fas fa-paper-plane"></i> 送出資料</button>
        </div>
      `;
    }

    // 提交表單資料
    function submitFormData() {
      const name = document.getElementById('form-name').value.trim();
      const school = document.getElementById('form-school').value.trim();
      const gmail = document.getElementById('form-gmail').value.trim();
      const level = document.getElementById('form-level').value;
      const grade = document.getElementById('form-grade').value.trim();
      const personality = document.getElementById('form-personality').value.trim();
      const hobbies = document.getElementById('form-hobbies').value.trim();
      const likes = document.getElementById('form-likes').value.trim();
      const intro = document.getElementById('form-intro').value.trim();
      const agreed = document.getElementById('agree-checkbox').checked;

      if (!name || !school || !gmail || !grade || !personality || !hobbies || !likes) {
        
        return;
      }
      
      if (/\d/.test(name)) {
        
        return;
      }
      
      if (/\d/.test(school)) {
        
        return;
      }
      
      if (!gmail.endsWith('@gmail.com')) {
        
        return;
      }
      
      if (intro.length < 50) {
        
        return;
      }
      
      if (!agreed) {
        
        return;
      }

      // 處理頭像上傳
      let avatar = null;
      const avatarUpload = document.getElementById('form-avatar');
      if (avatarUpload.files && avatarUpload.files[0]) {
        const file = avatarUpload.files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
          avatar = e.target.result;
          completeSubmission();
        };
        reader.readAsDataURL(file);
      } else {
        completeSubmission();
      }

      function completeSubmission() {
        const data = { 
          name, 
          school, 
          gmail, 
          grade, 
          personality,
          hobbies,
          likes,
          intro,
          avatar,
          time: new Date().toLocaleString('zh-TW'),
          status: 'pending',
          submittedBy: currentUser
        };

        // 儲存到待審核資料
        backendData.pendingData.push(data);
        saveBackendData();

        
        renderDataForm();
      }
    }

    // 資料查詢功能
    function renderSearch() {
      const content = document.getElementById('content-area');
      content.innerHTML = `
        <div class="content-card">
          <h2><i class="fas fa-search"></i> 資料查詢</h2>
          <p>使用以下條件查詢學生資料：</p>
          
          <div class="search-box">
            <div class="search-form">
              <div class="form-group">
                <label>姓名</label>
                <input type="text" id="search-name" class="form-control" placeholder="輸入姓名">
              </div>
              
              <div class="form-group">
                <label>學校</label>
                <input type="text" id="search-school" class="form-control" placeholder="輸入學校名稱">
              </div>
              
              <div class="form-group">
                <label>教育階段</label>
                <select id="search-level" class="form-control">
                  <option value="">全部</option>
                  <option value="primary">國小</option>
                  <option value="junior">國中</option>
                  <option value="high">高中</option>
                  <option value="other">其他</option>
                </select>
              </div>
              
              <div class="form-group">
                <label>年級</label>
                <input type="text" id="search-grade" class="form-control" placeholder="輸入年級">
              </div>
            </div>
            
            <button onclick="performSearch()" class="search-btn" style="margin-top:15px;">
              <i class="fas fa-search"></i> 開始查詢
            </button>
          </div>
          
          <div id="search-results"></div>
        </div>
      `;
    }

    // 執行查詢
    function performSearch() {
      const name = document.getElementById('search-name').value.trim().toLowerCase();
      const school = document.getElementById('search-school').value.trim().toLowerCase();
      const level = document.getElementById('search-level').value;
      const grade = document.getElementById('search-grade').value.trim().toLowerCase();
      
      let results = [];
      
      // 根據選擇的級別查詢資料
      if (level) {
        results = backendData.studentData[level].filter(item => {
          return (!name || item.name.toLowerCase().includes(name)) &&
                 (!school || item.school.toLowerCase().includes(school)) &&
                 (!grade || item.grade.toLowerCase().includes(grade));
        });
      } else {
        // 查詢所有級別
        Object.keys(backendData.studentData).forEach(key => {
          const levelResults = backendData.studentData[key].filter(item => {
            return (!name || item.name.toLowerCase().includes(name)) &&
                   (!school || item.school.toLowerCase().includes(school)) &&
                   (!grade || item.grade.toLowerCase().includes(grade));
          });
          results = results.concat(levelResults);
        });
      }
      
      displaySearchResults(results);
    }

    // 顯示查詢結果
    function displaySearchResults(results) {
      const resultsContainer = document.getElementById('search-results');
      
      if (results.length === 0) {
        resultsContainer.innerHTML = '<div class="announcement"><p>沒有找到符合條件的資料</p></div>';
        return;
      }
      
      let resultsHTML = `
        <div class="announcement">
          <h3>查詢結果 (共 ${results.length} 筆)</h3>
          <table class="data-table">
            <thead>
              <tr>
                <th>姓名</th>
                <th>學校</th>
                <th>Gmail</th>
                <th>年級</th>
                <th>教育階段</th>
                <th>填寫時間</th>
              </tr>
            </thead>
            <tbody>
      `;
      
      results.forEach(item => {
        // 找出項目屬於哪個教育階段
        let itemLevel = '';
        Object.keys(backendData.studentData).forEach(level => {
          if (backendData.studentData[level].includes(item)) {
            itemLevel = getLevelName(level);
          }
        });
        
        resultsHTML += `
          <tr>
            <td>${item.name}</td>
            <td>${item.school}</td>
            <td>${item.gmail}</td>
            <td>${item.grade}</td>
            <td>${itemLevel}</td>
            <td>${item.time}</td>
          </tr>
        `;
      });
      
      resultsHTML += `
            </tbody>
          </table>
        </div>
      `;
      
      resultsContainer.innerHTML = resultsHTML;
    }

    // 審核頁面
    function renderReview() {
      if (!isAdmin) {
        
        loadContent('dashboard');
        return;
      }
      
      const content = document.getElementById('content-area');
      const pendingData = backendData.pendingData.filter(item => item.status === 'pending');
      const approvedData = backendData.pendingData.filter(item => item.status === 'approved');
      const rejectedData = backendData.pendingData.filter(item => item.status === 'rejected');
      
      content.innerHTML = `
        <div class="content-card">
          <h2><i class="fas fa-clipboard-check"></i> 資料審核</h2>
          <p>審核使用者提交的學生資料</p>
          
          <div class="filter-tabs">
            <button class="filter-tab active" onclick="showReviewTab('pending')">
              待審核 <span class="status-badge status-pending">${pendingData.length}</span>
            </button>
            <button class="filter-tab" onclick="showReviewTab('approved')">
              已通過 <span class="status-badge status-approved">${approvedData.length}</span>
            </button>
            <button class="filter-tab" onclick="showReviewTab('rejected')">
              已拒絕 <span class="status-badge status-rejected">${rejectedData.length}</span>
            </button>
          </div>
          
          <div id="review-content">
            ${renderPendingData(pendingData)}
          </div>
        </div>
      `;
    }

    // 顯示審核標籤頁
    function showReviewTab(tab) {
      document.querySelectorAll('.filter-tab').forEach(btn => {
        btn.classList.remove('active');
      });
      event.currentTarget.classList.add('active');
      
      const reviewContent = document.getElementById('review-content');
      let data = [];
      
      switch(tab) {
        case 'pending':
          data = backendData.pendingData.filter(item => item.status === 'pending');
          reviewContent.innerHTML = renderPendingData(data);
          break;
        case 'approved':
          data = backendData.pendingData.filter(item => item.status === 'approved');
          reviewContent.innerHTML = renderReviewedData(data, 'approved');
          break;
        case 'rejected':
          data = backendData.pendingData.filter(item => item.status === 'rejected');
          reviewContent.innerHTML = renderReviewedData(data, 'rejected');
          break;
      }
    }

    // 渲染待審核資料
    function renderPendingData(data) {
      if (data.length === 0) {
        return '<div class="announcement"><p>目前沒有待審核的資料</p></div>';
      }
      
      return data.map((item, index) => `
        <div class="student-card">
          <div class="student-header">
            <img src="${item.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(item.name)}&background=008B8B&color=fff`}" class="student-avatar">
            <div class="student-basic-info">
              <h3>${item.name} <span class="status-badge status-pending">待審核</span></h3>
              <p><i class="fas fa-school"></i> ${item.school}</p>
              <p><i class="fas fa-envelope"></i> ${item.gmail}</p>
              <p><i class="fas fa-graduation-cap"></i> ${item.grade}</p>
              <p><i class="fas fa-user"></i> 提交者: ${backendData.users[item.submittedBy]?.name || '未知'}</p>
            </div>
          </div>
          
          <div class="student-details">
            <div class="detail-group">
              <h4><i class="fas fa-heart"></i> 個性特質</h4>
              <p>${item.personality}</p>
            </div>
            <div class="detail-group">
              <h4><i class="fas fa-star"></i> 興趣愛好</h4>
              <p>${item.hobbies}</p>
            </div>
            <div class="detail-group">
              <h4><i class="fas fa-thumbs-up"></i> 喜歡的事物</h4>
              <p>${item.likes}</p>
            </div>
          </div>
          
          <div class="student-intro">
            <h4><i class="fas fa-comment"></i> 個人介紹</h4>
            <p>${item.intro}</p>
          </div>
          
          <div class="student-actions">
            <button class="approve-btn" onclick="approveData(${index})">
              <i class="fas fa-check"></i> 通過審核
            </button>
            <button class="reject-btn" onclick="rejectData(${index})">
              <i class="fas fa-times"></i> 拒絕
            </button>
          </div>
        </div>
      `).join('');
    }

    // 渲染已審核資料
    function renderReviewedData(data, status) {
      if (data.length === 0) {
        return '<div class="announcement"><p>目前沒有相關資料</p></div>';
      }
      
      const statusText = status === 'approved' ? '已通過' : '已拒絕';
      const statusClass = status === 'approved' ? 'status-approved' : 'status-rejected';
      
      return data.map((item, index) => `
        <div class="student-card">
          <div class="student-header">
            <img src="${item.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(item.name)}&background=008B8B&color=fff`}" class="student-avatar">
            <div class="student-basic-info">
              <h3>${item.name} <span class="status-badge ${statusClass}">${statusText}</span></h3>
              <p><i class="fas fa-school"></i> ${item.school}</p>
              <p><i class="fas fa-envelope"></i> ${item.gmail}</p>
              <p><i class="fas fa-graduation-cap"></i> ${item.grade}</p>
              <p><i class="fas fa-user"></i> 提交者: ${backendData.users[item.submittedBy]?.name || '未知'}</p>
            </div>
          </div>
          
          <div class="student-details">
            <div class="detail-group">
              <h4><i class="fas fa-heart"></i> 個性特質</h4>
              <p>${item.personality}</p>
            </div>
            <div class="detail-group">
              <h4><i class="fas fa-star"></i> 興趣愛好</h4>
              <p>${item.hobbies}</p>
            </div>
            <div class="detail-group">
              <h4><i class="fas fa-thumbs-up"></i> 喜歡的事物</h4>
              <p>${item.likes}</p>
            </div>
          </div>
          
          <div class="student-intro">
            <h4><i class="fas fa-comment"></i> 個人介紹</h4>
            <p>${item.intro}</p>
          </div>
        </div>
      `).join('');
    }

    // 通過審核
    function approveData(index) {
      const data = backendData.pendingData[index];
      data.status = 'approved';
      
      // 根據教育階段添加到對應的資料庫
      const level = determineLevel(data.grade);
      backendData.studentData[level].push(data);
      
      // 從待審核列表中移除
      backendData.pendingData.splice(index, 1);
      
      saveBackendData();
      
      renderReview(); // 重新渲染整個審核頁面
    }

    // 拒絕資料
    function rejectData(index) {
      backendData.pendingData[index].status = 'rejected';
      saveBackendData();
      
      renderReview(); // 重新渲染整個審核頁面
    }

    // 根據年級判斷教育階段
    function determineLevel(grade) {
      if (grade.includes('小') || grade.includes('國小')) return 'primary';
      if (grade.includes('國中')) return 'junior';
      if (grade.includes('高中')) return 'high';
      return 'other';
    }

    // 顯示學生資料（美化版）
    function renderStudentData(level, title) {
      const content = document.getElementById('content-area');
      const data = backendData.studentData[level];
      
      if (data.length === 0) {
        content.innerHTML = `
          <div class="content-card">
            <h2><i class="fas fa-user-graduate"></i> ${title}資料</h2>
            <p>目前沒有資料</p>
          </div>
        `;
        return;
      }
      
      content.innerHTML = `
        <div class="content-card">
          <h2><i class="fas fa-user-graduate"></i> ${title}資料</h2>
          <p>共 ${data.length} 位學生</p>
          ${data.map(item => {
            // 檢查是否已經是好友
            const userFriends = backendData.friends[currentUser] || { friends: [] };
            const isFriend = userFriends.friends && userFriends.friends.some(friend => friend.username === item.submittedBy);
            const hasSentRequest = userFriends.sent_requests && userFriends.sent_requests.some(req => req.to === item.submittedBy);
            
            let friendButton = '';
            if (currentUser && item.submittedBy && item.submittedBy !== currentUser && !isFriend) {
              if (hasSentRequest) {
                friendButton = `<button class="friend-action-btn" style="background:#f39c12;" disabled>
                  <i class="fas fa-clock"></i> 申請中
                </button>`;
              } else {
                friendButton = `<button class="friend-action-btn" onclick="sendFriendRequest('${item.submittedBy}')">
                  <i class="fas fa-user-plus"></i> 加好友
                </button>`;
              }
            } else if (isFriend) {
              friendButton = `<button class="friend-action-btn" style="background:#2ecc71;" disabled>
                <i class="fas fa-check"></i> 已是好友
              </button>`;
            }
            
            return `
              <div class="student-card">
                <div class="student-header">
                  <img src="${item.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(item.name)}&background=008B8B&color=fff`}" class="student-avatar">
                  <div class="student-basic-info">
                    <h3>${item.name}</h3>
                    <p><i class="fas fa-school"></i> ${item.school}</p>
                    <p><i class="fas fa-envelope"></i> ${item.gmail}</p>
                    <p><i class="fas fa-graduation-cap"></i> ${item.grade}</p>
                    ${friendButton}
                  </div>
                </div>
                
                <div class="student-details">
                  <div class="detail-group">
                    <h4><i class="fas fa-heart"></i> 個性特質</h4>
                    <p>${item.personality}</p>
                  </div>
                  <div class="detail-group">
                    <h4><i class="fas fa-star"></i> 興趣愛好</h4>
                    <p>${item.hobbies}</p>
                  </div>
                  <div class="detail-group">
                    <h4><i class="fas fa-thumbs-up"></i> 喜歡的事物</h4>
                    <p>${item.likes}</p>
                  </div>
                </div>
                
                <div class="student-intro">
                  <h4><i class="fas fa-comment"></i> 個人介紹</h4>
                  <p>${item.intro}</p>
                </div>
                
                ${isAdmin ? `
                  <div class="student-actions">
                    <button class="delete-btn" onclick="deleteStudentData('${level}', ${backendData.studentData[level].indexOf(item)})">
                      <i class="fas fa-trash"></i> 刪除
                    </button>
                  </div>
                ` : ''}
              </div>
            `;
          }).join('')}
        </div>
      `;
    }

    // 刪除學生資料（僅管理員）
    function deleteStudentData(level, index) {
      if (!isAdmin) {
        
        return;
      }
      
      if (confirm('確定要刪除這筆資料嗎？此操作無法復原。')) {
        backendData.studentData[level].splice(index, 1);
        saveBackendData();
        renderStudentData(level, getLevelName(level));
        
      }
    }
    
    // 獲取級別名稱
    function getLevelName(level) {
      const names = {
        'primary': '國小學生',
        'junior': '國中學生',
        'high': '高中學生',
        'other': '其他年級'
      };
      return names[level] || '未知級別';
    }

    // 數據統計功能 (僅管理員)
    function renderStatistics() {
      if (!isAdmin) {
        
        loadContent('dashboard');
        return;
      }
      
      const content = document.getElementById('content-area');
      
      // 計算各級別人數
      const primaryCount = backendData.studentData.primary.length;
      const juniorCount = backendData.studentData.junior.length;
      const highCount = backendData.studentData.high.length;
      const otherCount = backendData.studentData.other.length;
      const totalCount = primaryCount + juniorCount + highCount + otherCount;
      
      // 計算學校統計
      const schoolStats = {};
      Object.keys(backendData.studentData).forEach(level => {
        backendData.studentData[level].forEach(student => {
          const school = student.school;
          schoolStats[school] = (schoolStats[school] || 0) + 1;
        });
      });
      
      // 轉換為陣列並排序
      const schoolArray = Object.entries(schoolStats)
        .map(([school, count]) => ({ school, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10); // 取前10名
      
      content.innerHTML = `
        <div class="content-card">
          <h2><i class="fas fa-chart-bar"></i> 數據統計</h2>
          <p>系統資料統計分析 (僅管理員可見)</p>
          
          <div class="stats-container">
            <div class="stat-card">
              <i class="fas fa-users"></i>
              <div class="number">${totalCount}</div>
              <div class="label">總學生數</div>
            </div>
            <div class="stat-card">
              <i class="fas fa-child"></i>
              <div class="number">${primaryCount}</div>
              <div class="label">國小學生</div>
            </div>
            <div class="stat-card">
              <i class="fas fa-user-graduate"></i>
              <div class="number">${juniorCount}</div>
              <div class="label">國中學生</div>
            </div>
            <div class="stat-card">
              <i class="fas fa-user-tie"></i>
              <div class="number">${highCount}</div>
              <div class="label">高中學生</div>
            </div>
          </div>
          
          <div class="announcement">
            <h3><i class="fas fa-school"></i> 學校統計 (前10名)</h3>
            <table class="data-table">
              <thead>
                <tr>
                  <th>排名</th>
                  <th>學校名稱</th>
                  <th>學生人數</th>
                </tr>
              </thead>
              <tbody>
                ${schoolArray.map((item, index) => `
                  <tr>
                    <td>${index + 1}</td>
                    <td>${item.school}</td>
                    <td>${item.count}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
          
          <div class="announcement">
            <h3><i class="fas fa-chart-pie"></i> 教育階段分佈</h3>
            <p>國小學生: ${primaryCount} 人 (${totalCount > 0 ? Math.round(primaryCount/totalCount*100) : 0}%)</p>
            <p>國中學生: ${juniorCount} 人 (${totalCount > 0 ? Math.round(juniorCount/totalCount*100) : 0}%)</p>
            <p>高中學生: ${highCount} 人 (${totalCount > 0 ? Math.round(highCount/totalCount*100) : 0}%)</p>
            <p>其他年級: ${otherCount} 人 (${totalCount > 0 ? Math.round(otherCount/totalCount*100) : 0}%)</p>
          </div>
        </div>
      `;
    }

    // 聊天室 - Line風格
    function renderChat() {
      const content = document.getElementById('content-area');
      content.innerHTML = `
        <div class="content-card">
          <h2><i class="fas fa-comments"></i> 八卦聊天室</h2>
          
          <div id="chat-box" style="max-height: 500px; overflow-y: auto; margin: 20px 0; padding: 10px; border: 1px solid #eee; border-radius: 8px; background: #f0f8ff;"></div>
          
          <div class="chat-input">
            <input type="text" id="chat-input" placeholder="輸入訊息..." onkeypress="if(event.key==='Enter') sendMessage()">
            <input type="file" id="media-upload" accept="image/*,video/*" style="display:none;">
            <button onclick="document.getElementById('media-upload').click()" class="media-upload-btn">
              <i class="fas fa-paperclip"></i>
            </button>
            <button onclick="sendMessage()"><i class="fas fa-paper-plane"></i> 送出</button>
          </div>
          
          ${isAdmin ? '<p style="color:#ff9800; margin-top:10px;"><i class="fas fa-shield-alt"></i> 您以管理員身份登入，可以刪除任何訊息。</p>' : ''}
        </div>
      `;
      
      // 監聽媒體上傳
      document.getElementById('media-upload').addEventListener('change', handleMediaUpload);
      
      loadChat();
    }

    // 處理媒體上傳
    function handleMediaUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      const reader = new FileReader();
      reader.onload = function(e) {
        const mediaType = file.type.startsWith('image/') ? 'image' : 'video';
        sendMessage(null, mediaType, e.target.result);
      };
      reader.readAsDataURL(file);
      
      // 清空檔案輸入
      event.target.value = '';
    }

    // 載入聊天訊息
    function loadChat() {
      const box = document.getElementById('chat-box');
      if (!box) return;
      
      const chatMessages = backendData.chatMessages;
      
      if (chatMessages.length === 0) {
        box.innerHTML = '<div class="empty-state"><i class="fas fa-comments"></i><h3>還沒有任何訊息</h3><p>快來發送第一條訊息吧！</p></div>';
        return;
      }
      
      box.innerHTML = chatMessages.map((msg, index) => {
        const isCurrentUser = msg.sender === currentUser;
        const user = backendData.users[msg.sender];
        const isMsgAdmin = user && user.isAdmin;
        const displayName = user ? (user.anonymous || user.name) : '匿名';
        
        let mediaContent = '';
        if (msg.mediaType && msg.mediaData) {
          if (msg.mediaType === 'image') {
            mediaContent = `<img src="${msg.mediaData}" class="chat-media" alt="傳送的圖片">`;
          } else if (msg.mediaType === 'video') {
            mediaContent = `<video src="${msg.mediaData}" class="chat-media" controls></video>`;
          }
        }
        
        return `
          <div class="chat-message ${isCurrentUser ? 'own' : 'other'} ${isMsgAdmin ? 'admin' : ''}">
            ${!isCurrentUser ? `
              <div class="sender-name">${displayName}${isMsgAdmin ? ' 👑' : ''}</div>
            ` : ''}
            <div>${msg.text || ''}</div>
            ${mediaContent}
            <div class="time">
              ${msg.time}
              ${(isAdmin || isCurrentUser) ? ` <a href="#" onclick="deleteMessage(${index})" style="color:#e74c3c; margin-left:10px;"><i class="fas fa-trash"></i> 刪除</a>` : ''}
            </div>
          </div>
        `;
      }).join('');
      
      box.scrollTop = box.scrollHeight;
    }

    // 發送訊息
    function sendMessage(text = null, mediaType = null, mediaData = null) {
      const input = document.getElementById('chat-input');
      const textContent = text || input.value.trim();
      
      if (!textContent && !mediaData) {
        
        return;
      }
      
      const user = backendData.users[currentUser];
      
      backendData.chatMessages.push({
        sender: currentUser,
        text: textContent,
        mediaType: mediaType,
        mediaData: mediaData,
        time: new Date().toLocaleString('zh-TW'),
        timestamp: new Date().getTime()
      });
      
      saveBackendData();
      if (input) input.value = '';
      loadChat();
      
      
      // 通知其他用戶有新消息
      updateActivity('public_messages');
    }

    // 刪除訊息
    function deleteMessage(index) {
      if (!isAdmin && backendData.chatMessages[index].sender !== currentUser) {
        
        return;
      }
      
      if (confirm('確定要刪除這條訊息嗎？')) {
        backendData.chatMessages.splice(index, 1);
        saveBackendData();
        loadChat();
        
      }
    }

    // 題目討論區
    function renderQuestions() {
      const content = document.getElementById('content-area');
      content.innerHTML = `
        <div class="content-card">
          <h2><i class="fas fa-question-circle"></i> 題目討論區</h2>
          <p>在這裡可以查看和討論其他同學提出的問題</p>
        </div>
        <div id="questions-list"></div>
      `;
      
      loadQuestions();
    }

    // 載入題目 - 修復版本（添加點讚狀態檢查）
    function loadQuestions() {
      const container = document.getElementById('questions-list');
      const questions = backendData.questions;
      
      if (questions.length === 0) {
        container.innerHTML = `
          <div class="content-card">
            <div class="empty-state">
              <i class="fas fa-question-circle"></i>
              <h3>還沒有任何問題</h3>
              <p>點擊右下角的 + 按鈕來發表第一個問題吧！</p>
            </div>
          </div>
        `;
        return;
      }
      
      // 按時間倒序排列
      const sortedQuestions = [...questions].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      
      container.innerHTML = sortedQuestions.map(question => {
        const author = backendData.users[question.author];
        const isAuthor = question.author === currentUser;
        
        // 檢查點讚狀態
        const liked = question.liked_by && question.liked_by.includes(currentUser);
        
        // 檢查是否已經是好友
        const userFriends = backendData.friends[currentUser] || { friends: [] };
        const isFriend = userFriends.friends && userFriends.friends.some(friend => friend.username === question.author);
        const hasSentRequest = userFriends.sent_requests && userFriends.sent_requests.some(req => req.to === question.author);
        
        let friendButton = '';
        if (currentUser && question.author && question.author !== currentUser && !isFriend) {
          if (hasSentRequest) {
            friendButton = `<button class="action-btn" style="color:#f39c12;" disabled>
              <i class="fas fa-clock"></i> 申請中
            </button>`;
          } else {
            friendButton = `<button class="action-btn" onclick="sendFriendRequest('${question.author}')">
              <i class="fas fa-user-plus"></i> 加好友
            </button>`;
          }
        }
        
        return `
          <div class="question-card">
            <div class="question-header">
              <img src="${author?.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(author?.name || '匿名')}&background=3498db&color=fff`}" 
                   class="question-avatar">
              <div class="question-meta">
                <h4>${author?.name || '匿名'}</h4>
                <div class="grade-subject">
                  <span>${question.grade} • ${question.subject}</span>
                  <span style="margin-left: 10px; color: #888;">${question.created_time}</span>
                </div>
              </div>
              ${friendButton}
            </div>
            
            <div class="question-content">
              <div class="question-text">${question.text}</div>
              ${question.image ? `<img src="${question.image}" class="question-image" alt="問題圖片">` : ''}
            </div>
            
            <div class="question-actions">
              <button class="action-btn ${liked ? 'liked' : ''}" onclick="likeQuestion('${question.id}')">
                <i class="fas fa-thumbs-up"></i> 讚 (${question.likes || 0})
              </button>
              <button class="action-btn" onclick="focusCommentInput('${question.id}')">
                <i class="fas fa-comment"></i> 留言
              </button>
              ${(isAuthor || isAdmin) ? `
                <button class="action-btn" onclick="deleteQuestion('${question.id}')" style="color:#e74c3c;">
                  <i class="fas fa-trash"></i> 刪除
                </button>
              ` : ''}
            </div>
            
            <div class="comments-section">
              <h5>留言 (${question.comments ? question.comments.length : 0})</h5>
              ${question.comments ? question.comments.map(comment => {
                const commentAuthor = backendData.users[comment.author];
                return `
                  <div class="comment">
                    <div class="comment-header">
                      <img src="${commentAuthor?.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(commentAuthor?.name || '匿名')}&background=27ae60&color=fff`}" 
                           class="comment-avatar">
                      <strong>${commentAuthor?.name || '匿名'}</strong>
                      <span style="margin-left: 10px; color: #888; font-size: 12px;">${comment.time}</span>
                    </div>
                    <div class="comment-content">${comment.text}</div>
                  </div>
                `;
              }).join('') : ''}
              
              <div class="add-comment">
                <input type="text" id="comment-${question.id}" placeholder="輸入留言..." onkeypress="if(event.key==='Enter') addComment('${question.id}')">
                <button onclick="addComment('${question.id}')" class="friend-action-btn chat">
                  <i class="fas fa-paper-plane"></i>
                </button>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    // 打開發表題目表單
    function openQuestionForm() {
      document.getElementById('question-form-modal').style.display = 'flex';
    }

    // 關閉發表題目表單
    function closeQuestionForm() {
      document.getElementById('question-form-modal').style.display = 'none';
      // 重置表單
      document.getElementById('question-text').value = '';
      document.getElementById('question-image').value = '';
      document.getElementById('selected-subject').value = '';
      document.getElementById('question-grade').value = '';
      document.querySelectorAll('.subject-tag').forEach(tag => tag.classList.remove('selected'));
    }

    // 發表問題
    function submitQuestion() {
      const text = document.getElementById('question-text').value.trim();
      const subject = document.getElementById('selected-subject').value;
      const grade = document.getElementById('question-grade').value.trim();
      
      if (!text) {
        
        return;
      }
      
      if (text.length > 150) {
        
        return;
      }
      
      if (!subject) {
        
        return;
      }
      
      if (!grade) {
        
        return;
      }
      
      // 處理圖片上傳
      let image = null;
      const imageUpload = document.getElementById('question-image');
      if (imageUpload.files && imageUpload.files[0]) {
        const file = imageUpload.files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
          image = e.target.result;
          completeQuestionSubmission();
        };
        reader.readAsDataURL(file);
      } else {
        completeQuestionSubmission();
      }

      function completeQuestionSubmission() {
        const question = {
          id: 'q_' + Date.now(),
          text: text,
          subject: subject,
          grade: grade,
          image: image,
          author: currentUser,
          author_name: backendData.users[currentUser].name,
          created_at: new Date().toISOString(),
          created_time: new Date().toLocaleString('zh-TW'),
          likes: 0,
          liked_by: [],  // 初始化點讚記錄
          comments: []
        };
        
        backendData.questions.unshift(question);
        saveBackendData();
        
        
        closeQuestionForm();
        loadQuestions();
        
        // 通知其他用戶有新問題
        updateActivity('questions');
      }
    }

    // 點讚問題 - 修復版本（一個帳號只能點一次）
    function likeQuestion(questionId) {
      const question = backendData.questions.find(q => q.id === questionId);
      if (question) {
        // 初始化點讚數據
        if (!question.liked_by) {
          question.liked_by = [];
        }
        
        // 檢查是否已經點讚
        const userIndex = question.liked_by.indexOf(currentUser);
        
        if (userIndex === -1) {
          // 點讚
          question.liked_by.push(currentUser);
          question.likes = (question.likes || 0) + 1;
          
        } else {
          // 取消點讚
          question.liked_by.splice(userIndex, 1);
          question.likes = Math.max(0, (question.likes || 1) - 1);
          
        }
        
        saveBackendData();
        loadQuestions(); // 重新載入以更新顯示
      }
    }

    // 聚焦留言輸入框
    function focusCommentInput(questionId) {
      const commentInput = document.getElementById(`comment-${questionId}`);
      if (commentInput) {
        commentInput.focus();
      }
    }

    // 添加留言
    function addComment(questionId) {
      const commentInput = document.getElementById(`comment-${questionId}`);
      const text = commentInput.value.trim();
      
      if (!text) {
        
        return;
      }
      
      const question = backendData.questions.find(q => q.id === questionId);
      if (question) {
        if (!question.comments) question.comments = [];
        
        question.comments.push({
          author: currentUser,
          text: text,
          time: new Date().toLocaleString('zh-TW')
        });
        
        saveBackendData();
        commentInput.value = '';
        loadQuestions();
        
      }
    }

    // 刪除問題 - 修復版本（管理員可以刪除任何問題）
    function deleteQuestion(questionId) {
      const question = backendData.questions.find(q => q.id === questionId);
      if (!question) return;
      
      // 檢查權限：管理員或問題作者
      if (question.author !== currentUser && !isAdmin) {
        
        return;
      }
      
      if (confirm('確定要刪除這個問題嗎？所有相關留言也會被刪除。')) {
        backendData.questions = backendData.questions.filter(q => q.id !== questionId);
        saveBackendData();
        loadQuestions();
        
      }
    }

    // 顯示個人簡介彈窗
    function showProfileModal() {
      const user = backendData.users[currentUser];
      document.getElementById('profile-name').textContent = user.name;
      document.getElementById('profile-school').textContent = user.school;
      document.getElementById('profile-email').textContent = user.email;
      document.getElementById('profile-intro').value = user.intro || '';
      document.getElementById('profile-anonymous').value = user.anonymous || user.name;
      document.getElementById('profile-personality').value = user.personality || '';
      document.getElementById('profile-hobbies').value = user.hobbies || '';
      document.getElementById('profile-likes').value = user.likes || '';
      
      // 設定頭像
      const avatarImg = document.getElementById('profile-avatar');
      if (user.avatar) {
        avatarImg.src = user.avatar;
      } else {
        avatarImg.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=008B8B&color=fff`;
      }
      
      // 更新字數計數器
      countChars('profile-intro', 'profile-char-count');
      
      document.getElementById('profile-modal').style.display = 'flex';
    }

    // 關閉個人簡介彈窗
    function closeProfileModal() {
      document.getElementById('profile-modal').style.display = 'none';
    }

    // 更新個人資料
    function updateProfile() {
      const user = backendData.users[currentUser];
      const intro = document.getElementById('profile-intro').value;
      const anonymous = document.getElementById('profile-anonymous').value;
      const personality = document.getElementById('profile-personality').value;
      const hobbies = document.getElementById('profile-hobbies').value;
      const likes = document.getElementById('profile-likes').value;
      const currentPassword = document.getElementById('profile-current-password').value;
      const newPassword = document.getElementById('profile-new-password').value;
      const confirmPassword = document.getElementById('profile-confirm-password').value;
      
      if (intro.length < 50) {
        
        return;
      }
      
      // 更新個人資料
      user.intro = intro;
      user.anonymous = anonymous;
      user.personality = personality;
      user.hobbies = hobbies;
      user.likes = likes;
      
      // 處理密碼變更
      if (currentPassword || newPassword || confirmPassword) {
        if (!currentPassword) {
          
          return;
        }
        
        if (currentPassword !== user.password) {
          
          return;
        }
        
        if (newPassword !== confirmPassword) {
          
          return;
        }
        
        if (newPassword.length < 6) {
          
          return;
        }
        
        user.password = newPassword;
        
        
        // 清空密碼欄位
        document.getElementById('profile-current-password').value = '';
        document.getElementById('profile-new-password').value = '';
        document.getElementById('profile-confirm-password').value = '';
      }
      
      // 處理頭像上傳
      const avatarUpload = document.getElementById('avatar-upload');
      if (avatarUpload.files && avatarUpload.files[0]) {
        const file = avatarUpload.files[0];
        const reader = new FileReader();
        
        reader.onload = function(e) {
          user.avatar = e.target.result;
          document.getElementById('profile-avatar').src = e.target.result;
          
        };
        
        reader.readAsDataURL(file);
      }
      
      saveBackendData();
      
      
      // 重新載入當前頁面以更新顯示
      loadContent(currentPage);
    }

    // 好友系統 - Instagram風格UI
    function renderFriends() {
      const content = document.getElementById('content-area');
      
      content.innerHTML = `
        <div class="friend-section">
          <h2 class="friend-section-title"><i class="fas fa-user-friends"></i> 好友系統</h2>
          <div class="friend-container">
            <p>管理您的好友和私訊，享受完整的社交體驗！</p>
          </div>
        </div>
        
        <div class="friend-section">
          <h3 class="friend-section-title"><i class="fas fa-user-plus"></i> 好友申請</h3>
          <div class="friend-container">
            <div id="friend-requests"></div>
          </div>
        </div>
        
        <div class="friend-section">
          <h3 class="friend-section-title"><i class="fas fa-users"></i> 我的好友</h3>
          <div class="friend-container">
            <div id="friends-list"></div>
          </div>
        </div>
        
        <div class="friend-section">
          <h3 class="friend-section-title"><i class="fas fa-comments"></i> 私訊聊天</h3>
          <div class="friend-container">
            <div id="private-chat"></div>
          </div>
        </div>
      `;
      
      loadFriendRequests();
      loadFriendsList();
      renderPrivateChat();
    }

    // 載入好友申請
    function loadFriendRequests() {
      const userRequests = backendData.friends[currentUser] || { received_requests: [] };
      displayFriendRequests(userRequests.received_requests || []);
    }

    // 顯示好友申請
    function displayFriendRequests(requests) {
      const container = document.getElementById('friend-requests');
      
      if (requests.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-inbox"></i><h3>目前沒有好友申請</h3><p>當有人傳送好友申請時，會顯示在這裡</p></div>';
        return;
      }
      
      container.innerHTML = requests.map(request => {
        const user = backendData.users[request.from];
        return `
          <div class="friend-request-card">
            <div class="friend-header">
              <img src="${user?.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(request.from_name)}&background=008B8B&color=fff`}" 
                   class="friend-avatar">
              <div class="friend-info">
                <h4>${request.from_name}</h4>
                <p>想要加您為好友</p>
                <div style="color:#666; font-size:12px;">時間: ${request.sent_time}</div>
              </div>
            </div>
            <div class="request-actions">
              <button class="friend-action-btn chat" onclick="handleFriendRequest('${request.from}', 'accept')">
                <i class="fas fa-check"></i> 接受
              </button>
              <button class="friend-action-btn remove" onclick="handleFriendRequest('${request.from}', 'reject')">
                <i class="fas fa-times"></i> 拒絕
              </button>
            </div>
          </div>
        `;
      }).join('');
    }

    // 處理好友申請
    function handleFriendRequest(fromUser, action) {
      // 從接收方的申請列表中移除
      if (!backendData.friends[currentUser]) {
        backendData.friends[currentUser] = { received_requests: [] };
      }
      backendData.friends[currentUser].received_requests = backendData.friends[currentUser].received_requests.filter(req => req.from !== fromUser);
      
      // 從發送方的已發送申請中移除
      if (!backendData.friends[fromUser]) {
        backendData.friends[fromUser] = { sent_requests: [] };
      }
      backendData.friends[fromUser].sent_requests = backendData.friends[fromUser].sent_requests.filter(req => req.to !== currentUser);
      
      if (action === 'accept') {
        // 成為好友
        const currentUserInfo = backendData.users[currentUser];
        const fromUserInfo = backendData.users[fromUser];
        
        // 初始化好友列表
        if (!backendData.friends[currentUser].friends) backendData.friends[currentUser].friends = [];
        if (!backendData.friends[fromUser].friends) backendData.friends[fromUser].friends = [];
        
        backendData.friends[currentUser].friends.push({
          username: fromUser,
          name: fromUserInfo.name,
          avatar: fromUserInfo.avatar,
          school: fromUserInfo.school,
          became_friends_at: new Date().toISOString()
        });
        
        backendData.friends[fromUser].friends.push({
          username: currentUser,
          name: currentUserInfo.name,
          avatar: currentUserInfo.avatar,
          school: currentUserInfo.school,
          became_friends_at: new Date().toISOString()
        });
        
        
      } else {
        
      }
      
      saveBackendData();
      loadFriendRequests();
      loadFriendsList();
    }

    // 載入好友列表
    function loadFriendsList() {
      const userFriends = backendData.friends[currentUser] || { friends: [] };
      displayFriendsList(userFriends.friends || []);
    }

    // 顯示好友列表
    function displayFriendsList(friends) {
      const container = document.getElementById('friends-list');
      
      if (friends.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-users"></i><h3>您還沒有好友</h3><p>快去加好友吧！</p></div>';
        return;
      }
      
      container.innerHTML = `
        <div class="friend-list">
          ${friends.map(friend => {
            // 隨機在線狀態
            const isOnline = Math.random() > 0.3;
            
            return `
              <div class="friend-card ${isOnline ? 'online' : 'offline'}">
                <div class="friend-header">
                  <img src="${friend.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(friend.name)}&background=008B8B&color=fff`}" 
                       class="friend-avatar">
                  <div class="friend-info">
                    <h4>${friend.name}</h4>
                    <p>${friend.school}</p>
                  </div>
                </div>
                <div class="friend-stats">
                  <span>${isOnline ? '🟢 在線' : '⚫ 離線'}</span>
                  <span>好友 since ${new Date(friend.became_friends_at).toLocaleDateString()}</span>
                </div>
                <div class="friend-actions">
                  <button class="friend-action-btn chat" onclick="startPrivateChat('${friend.username}')">
                    <i class="fas fa-comment"></i> 聊天
                  </button>
                  <button class="friend-action-btn remove" onclick="removeFriend('${friend.username}')">
                    <i class="fas fa-user-minus"></i> 刪除
                  </button>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      `;
    }

    // 發送好友申請
    function sendFriendRequest(targetUser) {
      const currentUserInfo = backendData.users[currentUser];
      const targetUserInfo = backendData.users[targetUser];
      
      // 初始化數據
      if (!backendData.friends[currentUser]) {
        backendData.friends[currentUser] = { sent_requests: [], received_requests: [], friends: [] };
      }
      if (!backendData.friends[targetUser]) {
        backendData.friends[targetUser] = { sent_requests: [], received_requests: [], friends: [] };
      }
      
      // 檢查是否已經發送過申請
      const hasSentRequest = backendData.friends[currentUser].sent_requests?.some(req => req.to === targetUser);
      if (hasSentRequest) {
        
        return;
      }
      
      // 檢查是否已經是好友
      const isFriend = backendData.friends[currentUser].friends?.some(friend => friend.username === targetUser);
      if (isFriend) {
        
        return;
      }
      
      // 發送申請
      const requestData = {
        from: currentUser,
        from_name: currentUserInfo.name,
        to: targetUser,
        sent_at: new Date().toISOString(),
        sent_time: new Date().toLocaleString('zh-TW')
      };
      
      // 添加到發送方的已發送申請
      if (!backendData.friends[currentUser].sent_requests) backendData.friends[currentUser].sent_requests = [];
      backendData.friends[currentUser].sent_requests.push({
        to: targetUser,
        to_name: targetUserInfo.name,
        sent_at: new Date().toISOString(),
        sent_time: new Date().toLocaleString('zh-TW')
      });
      
      // 添加到接收方的接收申請
      if (!backendData.friends[targetUser].received_requests) backendData.friends[targetUser].received_requests = [];
      backendData.friends[targetUser].received_requests.push(requestData);
      
      saveBackendData();
      
      
      // 重新載入當前頁面以更新按鈕狀態
      if (currentPage.startsWith('primary') || currentPage.startsWith('junior') || 
          currentPage.startsWith('high') || currentPage.startsWith('other') ||
          currentPage === 'questions') {
        loadContent(currentPage);
      }
    }

    // 刪除好友
    function removeFriend(friendUsername) {
      if (!confirm('確定要刪除這位好友嗎？所有聊天記錄也會被刪除。')) {
        return;
      }
      
      // 從雙方好友列表中移除
      if (backendData.friends[currentUser] && backendData.friends[currentUser].friends) {
        backendData.friends[currentUser].friends = backendData.friends[currentUser].friends.filter(friend => friend.username !== friendUsername);
      }
      
      if (backendData.friends[friendUsername] && backendData.friends[friendUsername].friends) {
        backendData.friends[friendUsername].friends = backendData.friends[friendUsername].friends.filter(friend => friend.username !== currentUser);
      }
      
      // 刪除私訊記錄
      const chatKey = getChatKey(currentUser, friendUsername);
      delete backendData.privateMessages[chatKey];
      
      saveBackendData();
      
      loadFriendsList();
      renderPrivateChat();
    }

    // 私訊聊天
    function renderPrivateChat() {
      const container = document.getElementById('private-chat');
      container.innerHTML = `
        <div class="form-group">
          <label>選擇好友進行私訊</label>
          <select id="private-chat-friend" class="form-control" onchange="loadPrivateMessages(this.value)">
            <option value="">請選擇好友</option>
          </select>
        </div>
        <div id="private-chat-messages" class="private-chat-container"></div>
        <div class="chat-input" id="private-chat-input" style="display:none;">
          <input type="text" id="private-message-input" placeholder="輸入私訊..." onkeypress="if(event.key==='Enter') sendPrivateMessage()">
          <input type="file" id="private-media-upload" accept="image/*,video/*" style="display:none;">
          <button onclick="document.getElementById('private-media-upload').click()" class="media-upload-btn">
            <i class="fas fa-paperclip"></i>
          </button>
          <button onclick="sendPrivateMessage()"><i class="fas fa-paper-plane"></i> 送出</button>
        </div>
      `;
      
      // 監聽私訊媒體上傳
      document.getElementById('private-media-upload').addEventListener('change', handlePrivateMediaUpload);
      
      loadFriendsForChat();
    }

    // 處理私訊媒體上傳
    function handlePrivateMediaUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      const friendUsername = document.getElementById('private-chat-friend').value;
      if (!friendUsername) {
        
        return;
      }
      
      const reader = new FileReader();
      reader.onload = function(e) {
        const mediaType = file.type.startsWith('image/') ? 'image' : 'video';
        sendPrivateMessage(null, mediaType, e.target.result);
      };
      reader.readAsDataURL(file);
      
      // 清空檔案輸入
      event.target.value = '';
    }

    // 載入好友列表用於私訊
    function loadFriendsForChat() {
      const userFriends = backendData.friends[currentUser] || { friends: [] };
      const select = document.getElementById('private-chat-friend');
      
      select.innerHTML = '<option value="">請選擇好友</option>';
      userFriends.friends?.forEach(friend => {
        select.innerHTML += `<option value="${friend.username}">${friend.name}</option>`;
      });
    }

    // 開始私訊 - 修復版本
    function startPrivateChat(friendUsername) {
      document.getElementById('private-chat-friend').value = friendUsername;
      
      // 確保聊天金鑰存在
      const chatKey = getChatKey(currentUser, friendUsername);
      if (!backendData.privateMessages[chatKey]) {
        backendData.privateMessages[chatKey] = [];
      }
      
      loadPrivateMessages(friendUsername);
      
      // 聚焦輸入框
      setTimeout(() => {
        const input = document.getElementById('private-message-input');
        if (input) input.focus();
      }, 100);
    }

    // 載入私訊 - 修復版本
    function loadPrivateMessages(friendUsername) {
      if (!friendUsername) {
        document.getElementById('private-chat-messages').innerHTML = '';
        document.getElementById('private-chat-input').style.display = 'none';
        return;
      }
      
      const chatKey = getChatKey(currentUser, friendUsername);
      const messages = backendData.privateMessages[chatKey] || [];
      
      displayPrivateMessages(messages, friendUsername);
      document.getElementById('private-chat-input').style.display = 'flex';
    }

    // 顯示私訊 - 修復版本
    function displayPrivateMessages(messages, friendUsername) {
      const container = document.getElementById('private-chat-messages');
      
      if (messages.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-comments"></i><h3>還沒有任何訊息</h3><p>開始對話吧！</p></div>';
        return;
      }
      
      // 按時間排序
      const sortedMessages = [...messages].sort((a, b) => new Date(a.timestamp || a.time) - new Date(b.timestamp || b.time));
      
      container.innerHTML = sortedMessages.map(msg => {
        const isOwn = msg.from === currentUser;
        
        let mediaContent = '';
        if (msg.mediaType && msg.mediaData) {
          if (msg.mediaType === 'image') {
            mediaContent = `<img src="${msg.mediaData}" style="max-width:200px; max-height:200px; border-radius:8px; margin:5px 0;" alt="傳送的圖片">`;
          } else if (msg.mediaType === 'video') {
            mediaContent = `<video src="${msg.mediaData}" style="max-width:200px; max-height:200px; border-radius:8px; margin:5px 0;" controls></video>`;
          }
        }
        
        return `
          <div class="private-message ${isOwn ? 'own' : 'other'}">
            ${!isOwn ? `<div class="sender">${msg.from_name}</div>` : ''}
            <div>${msg.text || ''}</div>
            ${mediaContent}
            <div class="time">${msg.time}</div>
          </div>
        `;
      }).join('');
      
      container.scrollTop = container.scrollHeight;
    }

    // 統一的聊天金鑰生成函數
    function getChatKey(user1, user2) {
      return [user1, user2].sort().join('_');
    }

    // 發送私訊 - 修復版本
    function sendPrivateMessage(text = null, mediaType = null, mediaData = null) {
      const friendUsername = document.getElementById('private-chat-friend').value;
      const input = document.getElementById('private-message-input');
      const textContent = text || input.value.trim();
      
      if (!friendUsername) {
        
        return;
      }
      
      if (!textContent && !mediaData) {
        
        return;
      }
      
      // 使用統一的聊天金鑰
      const chatKey = getChatKey(currentUser, friendUsername);
      
      if (!backendData.privateMessages[chatKey]) {
        backendData.privateMessages[chatKey] = [];
      }
      
      const message = {
        id: 'msg_' + Date.now(),
        from: currentUser,
        from_name: backendData.users[currentUser].name,
        text: textContent,
        mediaType: mediaType,
        mediaData: mediaData,
        time: new Date().toLocaleString('zh-TW'),
        timestamp: new Date().getTime(),
        read: false
      };
      
      backendData.privateMessages[chatKey].push(message);
      
      // 只保留最近200條訊息
      if (backendData.privateMessages[chatKey].length > 200) {
        backendData.privateMessages[chatKey] = backendData.privateMessages[chatKey].slice(-200);
      }
      
      saveBackendData();
      if (input) input.value = '';
      
      // 立即更新顯示
      loadPrivateMessages(friendUsername);
      
      
      // 通知對方有新消息
      updateActivity('private_messages');
    }

    // 系統設定
    function renderSystemConfig() {
      if (!isAdmin) {
        
        loadContent('dashboard');
        return;
      }
      
      const config = backendData.systemConfig;
      
      const content = document.getElementById('content-area');
      content.innerHTML = `
        <div class="content-card">
          <h2><i class="fas fa-cogs"></i> 系統設定</h2>
          <p>管理系統的各種設定選項</p>
          
          <div class="form-group">
            <label for="site-title">網站標題</label>
            <input type="text" id="site-title" class="form-control" value="${config.siteTitle || '畢業資料管理系統'}">
          </div>
          
          <div class="form-group">
            <label for="theme-color">主題顏色</label>
            <input type="color" id="theme-color" class="form-control" value="${config.themeColor || '#008B8B'}">
          </div>
          
          <div class="form-group">
            <label for="welcome-message">歡迎訊息</label>
            <textarea id="welcome-message" class="form-control" rows="3">${config.welcomeMessage || '歡迎使用畢業資料管理系統'}</textarea>
          </div>
          
          <div class="form-group">
            <label for="max-file-size">最大檔案大小 (MB)</label>
            <input type="number" id="max-file-size" class="form-control" value="${config.maxFileSize || 5}" min="1" max="50">
          </div>
          
          <div class="checkbox-group">
            <input type="checkbox" id="allow-registration" ${config.allowRegistration !== false ? 'checked' : ''}>
            <label for="allow-registration">允許新使用者註冊</label>
          </div>
          
          <div class="checkbox-group">
            <input type="checkbox" id="maintenance-mode" ${config.maintenanceMode ? 'checked' : ''}>
            <label for="maintenance-mode">維護模式</label>
          </div>
          
          <button onclick="saveSystemConfig()" class="login-box button">
            <i class="fas fa-save"></i> 儲存設定
          </button>
        </div>
      `;
    }

    // 儲存系統設定
    function saveSystemConfig() {
      backendData.systemConfig = {
        siteTitle: document.getElementById('site-title').value,
        themeColor: document.getElementById('theme-color').value,
        welcomeMessage: document.getElementById('welcome-message').value,
        maxFileSize: parseInt(document.getElementById('max-file-size').value),
        allowRegistration: document.getElementById('allow-registration').checked,
        maintenanceMode: document.getElementById('maintenance-mode').checked
      };
      
      saveBackendData();
      
      
      // 更新網站標題
      document.title = backendData.systemConfig.siteTitle || '畢業資料管理系統';
      document.querySelector('.top-bar .title').innerHTML = `<i class="fas fa-graduation-cap"></i> ${backendData.systemConfig.siteTitle || '畢業資料管理系統'}`;
    }

    // 管理員選單
    function toggleAdminMenu() {
      const menu = document.getElementById('admin-menu');
      menu.classList.toggle('show');
    }

    // 關閉管理員選單
    function closeAdminMenu() {
      document.getElementById('admin-menu').classList.remove('show');
    }

    // 點擊其他地方關閉管理員選單
    document.addEventListener('click', function(event) {
      if (!event.target.closest('.admin-tools')) {
        closeAdminMenu();
      }
    });

    // 系統編輯器
    function openSystemEditor() {
      
      closeAdminMenu();
    }

    // 系統備份
    function backupSystem() {
      const backupData = {
        users: backendData.users,
        studentData: backendData.studentData,
        pendingData: backendData.pendingData,
        announcements: backendData.announcements,
        systemConfig: backendData.systemConfig,
        friends: backendData.friends,
        privateMessages: backendData.privateMessages,
        questions: backendData.questions,
        chatMessages: backendData.chatMessages,
        timestamp: new Date().toISOString()
      };
      
      const dataStr = JSON.stringify(backupData, null, 2);
      const dataBlob = new Blob([dataStr], {type: 'application/json'});
      
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `system_backup_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      
      closeAdminMenu();
    }

    // 系統還原
    function restoreSystem() {
      
      closeAdminMenu();
    }
  // ==================== 雲端同步功能 ====================
let syncEnabled = true;

// 自動同步功能
async function syncToCloud() {
    if (!syncEnabled) return;
    
    try {
        // 準備要同步的數據
        const syncData = {
            users: JSON.parse(localStorage.getItem('backend_users') || '{}'),
            messages: JSON.parse(localStorage.getItem('chat_messages') || '[]'),
            friends: JSON.parse(localStorage.getItem('friends_data') || '{}'),
            questions: JSON.parse(localStorage.getItem('questions_data') || '[]'),
            announcements: JSON.parse(localStorage.getItem('announcements') || '[]'),
            studentData: JSON.parse(localStorage.getItem('backend_primary') || '[]').concat(
                JSON.parse(localStorage.getItem('backend_junior') || '[]'),
                JSON.parse(localStorage.getItem('backend_high') || '[]'),
                JSON.parse(localStorage.getItem('backend_other') || '[]')
            )
        };

        // 發送到雲端
        const response = await fetch('/api/sync-data', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(syncData)
        });
        
        const result = await response.json();
        if (result.success) {
            console.log('數據同步成功');
        }
    } catch (error) {
        console.log('同步失敗，但本地功能正常運作');
    }
}

// 從雲端加載數據
async function loadFromCloud() {
    try {
        const response = await fetch('/api/get-sync-data');
        const result = await response.json();
        
        if (result.success) {
            // 合併雲端數據到本地
            if (result.users) {
                const localUsers = JSON.parse(localStorage.getItem('backend_users') || '{}');
                const mergedUsers = {...localUsers, ...result.users};
                localStorage.setItem('backend_users', JSON.stringify(mergedUsers));
            }
            
            if (result.messages && result.messages.length > 0) {
                localStorage.setItem('chat_messages', JSON.stringify(result.messages));
            }
            
            console.log('雲端數據加載成功');
        }
    } catch (error) {
        console.log('雲端數據加載失敗，使用本地數據');
    }
}

// 啟動同步系統
function startSyncSystem() {
    // 頁面載入時從雲端加載數據
    loadFromCloud();
    
    // 每30秒同步一次到雲端
    setInterval(syncToCloud, 30000);
    
    // 用戶操作時也同步
    const originalSendMessage = window.sendMessage;
    window.sendMessage = function() {
        const result = originalSendMessage?.apply(this, arguments);
        setTimeout(syncToCloud, 1000); // 1秒後同步
        return result;
    };
    
    console.log('雲端同步系統已啟動');
}

// 頁面載入完成後啟動同步
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startSyncSystem);
} else {
    startSyncSystem();
}

// 添加同步狀態指示器
