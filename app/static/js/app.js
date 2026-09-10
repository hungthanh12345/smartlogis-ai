// app/static/js/app.js - SmartLogis AI Global Frontend Utilities & Dark Mode Engine

/**
 * Khởi tạo Theme (Dark / Light Mode)
 * Đọc từ localStorage hoặc ưu tiên chế độ sáng mặc định phong cách KiotViet
 */
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

/**
 * Chuyển đổi qua lại giữa Dark Mode và Light Mode
 */
function toggleDarkMode() {
  const isDark = document.documentElement.classList.toggle('dark');
  localStorage.setItem('smartlogis_theme', isDark ? 'dark' : 'light');
  updateThemeToggleUI(isDark);
  window.dispatchEvent(new CustomEvent('smartlogis:theme_changed', { detail: { isDark } }));
}

/**
 * Cập nhật biểu tượng và giao diện tất cả các nút Theme Switcher trên trang
 */
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

/**
 * Đăng xuất an toàn: Xóa token phía client và gọi API /logout xóa HTTPOnly Cookie
 */
function handleLogout(event) {
  if (event) {
    event.preventDefault();
  }
  try {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
    sessionStorage.clear();
  } catch (e) {
    console.error('[Logout] Lỗi xóa session client:', e);
  }
  window.location.href = '/logout';
}

// Khởi tạo ngay khi tài liệu tải xong
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
});