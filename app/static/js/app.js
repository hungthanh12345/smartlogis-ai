// app/static/js/app.js - SmartLogis AI Global Frontend Utilities

function handleLogout(event) {
  if (event) {
    event.preventDefault();
  }
  try {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
    sessionStorage.clear();
  } catch (e) {
    console.error(e);
  }
  // Chuyển hướng tới route /logout để xóa Cookie access_token trên server và redirect về /login
  window.location.href = '/logout';
}
\n