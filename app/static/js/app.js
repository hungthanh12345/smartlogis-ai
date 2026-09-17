// app/static/js/app.js - SmartLogis AI Global Frontend Utilities & Tab Session Guard
/**
 * SmartLogis AI - Bộ Tiện ích Toàn cục, Theme Switcher & Bảo vệ Phiên Đa Thẻ (Tab Session Guard)
 * - Tự động phát hiện và đá phiên cũ (Kick-out) khi tài khoản khác đăng nhập ở tab mới.
 * - Cô lập phiên từng tab qua sessionStorage & kiểm tra tính toàn vẹn với localStorage.
 * - Global Fetch Interceptor gắn header X-Session-User và tự động bắt lỗi 401 đẩy về /login.
 */

// =============================================================================
// 1. THEME SWITCHER (DARK / LIGHT MODE)
// =============================================================================

function initTheme() {
  const savedTheme = localStorage.getItem('smartlogis_theme');
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
    document.documentElement.classList.add('dark');
    updateThemeToggleUI(true);
  } else {
    document.documentElement.classList.remove('dark');
    updateThemeToggleUI(false);
  }
}

function toggleDarkMode() {
  const isDark = document.documentElement.classList.toggle('dark');
  localStorage.setItem('smartlogis_theme', isDark ? 'dark' : 'light');
  updateThemeToggleUI(isDark);
  window.dispatchEvent(new CustomEvent('smartlogis:theme_changed', { detail: { isDark } }));
}

function updateThemeToggleUI(isDark) {
  const btns = document.querySelectorAll('.theme-toggle-btn, #themeToggleBtn');
  btns.forEach(btn => {
    if (isDark) {
      btn.innerHTML = '<i class="fa-solid fa-sun text-amber-400 text-sm"></i><span class="text-xs font-semibold text-amber-300">Giao diện Sáng</span>';
      btn.setAttribute('title', 'Chuyển sang chế độ Giao diện Sáng (Light Mode)');
      btn.classList.add('bg-slate-800', 'text-amber-300', 'border-slate-700');
      btn.classList.remove('bg-slate-100', 'text-slate-700', 'border-slate-200');
    } else {
      btn.innerHTML = '<i class="fa-solid fa-moon text-sky-600 text-sm"></i><span class="text-xs font-semibold text-slate-700">Giao diện Tối</span>';
      btn.setAttribute('title', 'Chuyển sang chế độ Giao diện Tối (Dark Mode)');
      btn.classList.add('bg-slate-100', 'text-slate-700', 'border-slate-200');
      btn.classList.remove('bg-slate-800', 'text-amber-300', 'border-slate-700');
    }
  });
}

// =============================================================================
// 2. TAB SESSION MANAGER & ISOLATION (HỖ TRỢ ĐA TAB & ĐỘC LẬP PHIÊN)
// =============================================================================

window.__IS_KICKED_OUT = false;

/**
 * Hiển thị Modal Cảnh báo khi phiên làm việc thực sự bị hết hạn 401
 */
function triggerKickOut(reason, message) {
  if (window.__IS_KICKED_OUT) return;
  window.__IS_KICKED_OUT = true;

  console.warn(`[SessionGuard] KICK-OUT TRIGGERED: ${reason} - ${message}`);

  // Ngắt kết nối WebSocket nếu đang mở
  if (window.smartLogisWS && window.smartLogisWS.socket) {
    try {
      window.smartLogisWS.socket.close();
    } catch (e) {}
  }

  // Xóa sessionStorage của tab này
  try {
    sessionStorage.clear();
  } catch (e) {}

  // Tạo và hiển thị Modal Khóa Thao Tác
  let existingModal = document.getElementById('sessionKickoutModal');
  if (!existingModal) {
    const modalHtml = `
      <div id="sessionKickoutModal" class="fixed inset-0 z-[999999] bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-300">
        <div class="bg-white dark:bg-slate-900 border-2 border-rose-500 rounded-2xl shadow-2xl max-w-md w-full p-6 text-center space-y-4">
          <div class="w-16 h-16 rounded-full bg-rose-100 dark:bg-rose-950/80 text-rose-600 dark:text-rose-400 mx-auto flex items-center justify-center text-3xl shadow-inner animate-bounce">
            <i class="fa-solid fa-triangle-exclamation"></i>
          </div>
          <h3 class="text-lg font-black text-slate-900 dark:text-white uppercase tracking-tight">
            Phiên Làm Việc Đã Hết Hạn
          </h3>
          <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed font-medium" id="kickoutMessageText">
            ${message || 'Phiên làm việc của bạn đã kết thúc. Vui lòng đăng nhập lại để tiếp tục.'}
          </p>
          <button onclick="window.location.replace('/login')"
            class="w-full py-2.5 px-4 bg-sky-600 hover:bg-sky-500 active:bg-sky-700 text-white font-bold rounded-xl text-xs transition shadow-md flex items-center justify-center gap-2 cursor-pointer">
            <i class="fa-solid fa-right-to-bracket"></i>
            <span>Đăng Nhập Lại Ngay</span>
          </button>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
  }
}

/**
 * Đồng bộ và khởi tạo thông tin phiên cho tab
 */
function initTabSessionGuard() {
  const isLoginPage = window.location.pathname === '/login';
  if (isLoginPage) return;

  const serverUser = (window.__CURRENT_USER__ && window.__CURRENT_USER__.username) ? window.__CURRENT_USER__.username : null;

  // Nếu trên trang quản trị kho SSR mà serverUser trống -> Chuyển về /login
  if (!serverUser) {
    console.warn('[SessionGuard] Không tìm thấy user hợp lệ trên trang SSR. Đang chuyển về /login...');
    window.location.replace('/login');
    return;
  }

  // Khởi tạo thông tin cho tab nếu chưa có
  let tabUser = sessionStorage.getItem('smartlogis_tab_user');
  if (!tabUser) {
    sessionStorage.setItem('smartlogis_tab_user', serverUser);
    if (window.__CURRENT_USER__.role) sessionStorage.setItem('smartlogis_tab_role', window.__CURRENT_USER__.role);
    if (window.__CURRENT_USER__.fullName) sessionStorage.setItem('smartlogis_tab_fullname', window.__CURRENT_USER__.fullName);
    const token = localStorage.getItem('access_token');
    if (token) sessionStorage.setItem('access_token', token);
  }

  // Luôn đồng bộ cookie của tab này
  syncTabSessionCookie();
}

/**
 * Đồng bộ cookie theo phiên riêng của tab này khi tab được focus hoặc click
 */
function syncTabSessionCookie() {
  const isLoginPage = window.location.pathname === '/login';
  if (isLoginPage || window.__IS_KICKED_OUT) return;

  const tabToken = sessionStorage.getItem('access_token') || localStorage.getItem('access_token');
  if (tabToken) {
    document.cookie = `access_token=Bearer ${tabToken}; path=/; SameSite=Lax; max-age=86400`;
  }
}

window.addEventListener('focus', syncTabSessionCookie);
window.addEventListener('click', syncTabSessionCookie);
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') {
    syncTabSessionCookie();
  }
});

// =============================================================================
// 3. GLOBAL FETCH INTERCEPTOR (GẮN TAB AUTHORIZATION & XỬ LÝ 401)
// =============================================================================

const originalFetch = window.fetch;
window.fetch = async function(resource, init = {}) {
  const url = typeof resource === 'string' ? resource : (resource && resource.url ? resource.url : '');

  if (url.includes('/api/v1/')) {
    if (window.__IS_KICKED_OUT) {
      return Promise.reject(new Error('Phiên làm việc trên tab này đã bị vô hiệu hóa.'));
    }

    const tabUser = sessionStorage.getItem('smartlogis_tab_user') || (window.__CURRENT_USER__ ? window.__CURRENT_USER__.username : null);
    const tabToken = sessionStorage.getItem('access_token') || localStorage.getItem('access_token');
    const sid = sessionStorage.getItem('smartlogis_tab_session_id') || localStorage.getItem('smartlogis_active_session_id');

    // Gắn token của riêng tab này vào header Authorization và X-Session-User
    init = init || {};
    init.headers = init.headers || {};
    if (init.headers instanceof Headers) {
      if (tabToken) init.headers.set('Authorization', `Bearer ${tabToken}`);
      if (tabUser) init.headers.set('X-Session-User', tabUser);
      if (sid) init.headers.set('X-Session-Id', sid);
    } else if (typeof init.headers === 'object') {
      if (tabToken) init.headers['Authorization'] = `Bearer ${tabToken}`;
      if (tabUser) init.headers['X-Session-User'] = tabUser;
      if (sid) init.headers['X-Session-Id'] = sid;
    }
  }

  const response = await originalFetch(resource, init);

  // Xử lý khi API trả về 401 Unauthorized
  if (response.status === 401 && url.includes('/api/v1/')) {
    if (!url.includes('/auth/login') && !url.includes('/auth/token')) {
      triggerKickOut('UNAUTHORIZED_401', 'Phiên làm việc của bạn đã hết hạn hoặc không có quyền truy cập. Vui lòng đăng nhập lại.');
    }
  }

  return response;
};

// =============================================================================
// 4. LOGOUT XỬ LÝ SẠCH SẼ CLIENT & SERVER
// =============================================================================

function handleLogout(event) {
  if (event) {
    event.preventDefault();
  }
  try {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
    localStorage.removeItem('smartlogis_active_user');
    localStorage.removeItem('smartlogis_active_role');
    localStorage.removeItem('smartlogis_active_session_id');
    sessionStorage.clear();
  } catch (e) {
    console.error('[Logout] Lỗi xóa session client:', e);
  }
  window.location.href = '/logout';
}

// =============================================================================
// 5. KHỞI CHẠY KHI TRANG TẢI XONG
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initTabSessionGuard();
});