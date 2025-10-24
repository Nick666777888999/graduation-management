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
