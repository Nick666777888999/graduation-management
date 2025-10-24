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
