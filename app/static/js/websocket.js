// app/static/js/websocket.js
/**
 * SmartLogis AI - Realtime Client WebSocket & Multi-Device Sync Engine
 * Tự động kết nối, duy trì heartbeat, hiển thị thông báo tức thời và
 * phát sự kiện đồng bộ dữ liệu giữa các thiết bị (PC, Laptop, Mobile) mà không cần F5.
 */

class SmartLogisWebSocketClient {
  constructor() {
    this.socket = null;
    this.reconnectInterval = 3000;
    this.pingInterval = 25000;
    this.pingTimer = null;
    this.isConnected = false;
    this.init();
  }

  init() {
    this.connect();
  }

  getWebSocketUrl() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    return `${protocol}//${host}/ws/inventory`;
  }

  connect() {
    const wsUrl = this.getWebSocketUrl();
    console.log(`[WebSocket] Đang kết nối tới máy chủ tập trung: ${wsUrl}...`);
    this.updateStatusUI('connecting');

    try {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        this.isConnected = true;
        console.log('[WebSocket] Đã kết nối thành công tới SmartLogis Realtime Server.');
        this.updateStatusUI('connected');
        this.startHeartbeat();
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleIncomingMessage(data);
        } catch (err) {
          console.error('[WebSocket] Lỗi giải mã gói tin JSON:', err);
        }
      };

      this.socket.onclose = (event) => {
        this.isConnected = false;
        this.stopHeartbeat();
        console.warn(`[WebSocket] Đã mất kết nối máy chủ (Code: ${event.code}). Đang thử kết nối lại sau 3s...`);
        this.updateStatusUI('disconnected');
        setTimeout(() => this.connect(), this.reconnectInterval);
      };

      this.socket.onerror = (error) => {
        console.error('[WebSocket] Gặp lỗi đường truyền:', error);
        this.socket.close();
      };

    } catch (e) {
      console.error('[WebSocket] Không thể khởi tạo kết nối:', e);
      setTimeout(() => this.connect(), this.reconnectInterval);
    }
  }

  startHeartbeat() {
    this.stopHeartbeat();
    this.pingTimer = setInterval(() => {
      if (this.isConnected && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send('ping');
      }
    }, this.pingInterval);
  }

  stopHeartbeat() {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }

  handleIncomingMessage(data) {
    if (data.type === 'PONG') {
      if (data.active_clients !== undefined) {
        this.updateActiveClientsCount(data.active_clients);
      }
      return;
    }

    if (data.type === 'CONNECTION_ESTABLISHED') {
      if (data.active_clients !== undefined) {
        this.updateActiveClientsCount(data.active_clients);
      }
      return;
    }

    if (data.type === 'INVENTORY_UPDATED') {
      console.log('[WebSocket Realtime Event]', data);
      
      // 1. Hiển thị Toast thông báo nổi cho người dùng
      this.showRealtimeToast(data);

      // 2. Bắn Custom Event cho toàn bộ trang web
      window.dispatchEvent(new CustomEvent('smartlogis:inventory_updated', { detail: data }));

      // 3. Tự động đồng bộ các thành phần theo từng trang đang mở
      this.syncActivePage(data);
    }
  }

  syncActivePage(data) {
    const path = window.location.pathname;

    // A. Nếu đang mở Dashboard: làm mới toàn bộ 4 KPI và bảng cảnh báo tồn min
    if (path === '/dashboard' || path === '/') {
      this.refreshDashboardData();
    }

    // B. Nếu đang mở màn hình Tra cứu Thẻ kho: nạp lại thẻ kho ngay
    if (path === '/the-kho' && typeof window.loadTheKho === 'function') {
      console.log('[Realtime] Đang tự động cập nhật Sổ Thẻ Kho...');
      window.loadTheKho();
    }

    // C. Nếu đang mở màn hình Lập Phiếu Xuất: làm mới tồn khả dụng để chống tồn âm tức thời
    if (path === '/outbound' && typeof window.reloadStockValidation === 'function') {
      console.log('[Realtime] Đang thẩm định lại số dư tồn khả dụng trên phiếu xuất...');
      window.reloadStockValidation();
    }

    // D. Nếu đang mở màn hình Danh Mục Hàng Hóa: làm mới bảng SKU
    if (path === '/hang-hoa' && typeof window.reloadSkuTable === 'function') {
      console.log('[Realtime] Đang cập nhật lại danh mục mặt hàng...');
      window.reloadSkuTable();
    }
  }

  async refreshDashboardData() {
    try {
      console.log('[Realtime] Đang tự động cập nhật số liệu Dashboard...');
      const resKpi = await fetch('/api/v1/kho/kpis');
      if (resKpi.ok) {
        const kpis = await resKpi.json();
        
        // Cập nhật các thẻ chỉ số KPI
        const elSkus = document.getElementById('kpi_tong_sku');
        const elAlerts = document.getElementById('kpi_canh_bao');
        const elTx = document.getElementById('kpi_giao_dich');

        if (elSkus && kpis.tong_sku !== undefined) elSkus.innerText = kpis.tong_sku;
        if (elAlerts && kpis.canh_bao_ton_min !== undefined) elAlerts.innerText = kpis.canh_bao_ton_min;
        if (elTx && kpis.tong_giao_dich_thang !== undefined) elTx.innerText = kpis.tong_giao_dich_thang;
      }

      // Làm mới danh sách cảnh báo tồn tối thiểu nếu có hàm riêng
      if (typeof window.refreshStockAlertsTable === 'function') {
        window.refreshStockAlertsTable();
      }
    } catch (e) {
      console.error('[Realtime] Lỗi khi cập nhật Dashboard:', e);
    }
  }

  updateStatusUI(status) {
    const badge = document.getElementById('realtimeBadge');
    const dot = document.getElementById('realtimeDot');
    const text = document.getElementById('realtimeText');

    if (!badge || !dot || !text) return;

    if (status === 'connected') {
      badge.className = 'flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 transition-all';
      dot.className = 'w-2 h-2 rounded-full bg-emerald-500 animate-pulse';
      text.innerText = 'Realtime Sync: Online';
    } else if (status === 'connecting') {
      badge.className = 'flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-50 text-amber-700 border border-amber-200 transition-all';
      dot.className = 'w-2 h-2 rounded-full bg-amber-400 animate-ping';
      text.innerText = 'Đang kết nối...';
    } else {
      badge.className = 'flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200 transition-all';
      dot.className = 'w-2 h-2 rounded-full bg-rose-500';
      text.innerText = 'Mất kết nối (Đang reconnect)';
    }
  }

  updateActiveClientsCount(count) {
    const text = document.getElementById('realtimeText');
    if (text && this.isConnected) {
      text.innerText = `Realtime Online (${count} thiết bị)`;
    }
  }

  showRealtimeToast(data) {
    const container = document.getElementById('realtimeToastContainer');
    if (!container) return;

    const toastId = 'toast-' + Date.now();
    const isOutbound = data.action === 'OUTBOUND';
    const borderClass = isOutbound ? 'border-amber-400 bg-amber-50/95' : 'border-sky-400 bg-sky-50/95';
    const iconClass = isOutbound ? 'fa-dolly text-amber-600' : 'fa-box-archive text-sky-600';
    const tagText = isOutbound ? 'XUẤT KHO REALTIME' : 'NHẬP KHO REALTIME';

    const toastHtml = `
      <div id="${toastId}" class="max-w-md w-full bg-white shadow-xl rounded-xl border-l-4 ${borderClass} p-3.5 flex items-start gap-3 pointer-events-auto transform transition-all duration-300 translate-y-2 opacity-0 animate-in fade-in slide-in-from-top-4">
        <div class="w-8 h-8 rounded-lg bg-white shadow-xs border border-slate-200 flex items-center justify-center flex-shrink-0 mt-0.5">
          <i class="fa-solid ${iconClass}"></i>
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-2">
            <span class="text-[10px] font-bold uppercase tracking-wider text-slate-500">${tagText}</span>
            <span class="text-[10px] text-slate-400 font-mono">${data.timestamp || 'Vừa xong'}</span>
          </div>
          <p class="text-xs font-semibold text-slate-800 mt-0.5 leading-snug">${data.message || 'Dữ liệu kho vừa được cập nhật'}</p>
          <div class="text-[10px] text-slate-500 mt-1 flex items-center gap-2">
            <span>Mã CT: <b class="font-mono text-slate-700">${data.ma_chung_tu || '--'}</b></span>
            <span>•</span>
            <span class="text-emerald-700 font-semibold"><i class="fa-solid fa-arrows-rotate"></i> Đã đồng bộ ngay</span>
          </div>
        </div>
        <button onclick="document.getElementById('${toastId}').remove()" class="text-slate-400 hover:text-slate-600 text-xs p-1">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
    `;

    container.insertAdjacentHTML('beforeend', toastHtml);

    // Kích hoạt animation hiện
    setTimeout(() => {
      const el = document.getElementById(toastId);
      if (el) {
        el.classList.remove('opacity-0', 'translate-y-2');
      }
    }, 50);

    // Tự động biến mất sau 6 giây
    setTimeout(() => {
      const el = document.getElementById(toastId);
      if (el) {
        el.classList.add('opacity-0', 'scale-95');
        setTimeout(() => el.remove(), 300);
      }
    }, 6000);
  }

  async refreshDashboardData() {
    try {
      console.log('[Realtime] Đang tự động cập nhật số liệu Dashboard...');
      const resKpi = await fetch('/api/v1/kho/kpis');
      if (resKpi.ok) {
        const kpis = await resKpi.json();
        
        // Cập nhật 4 thẻ KPI nếu có ID
        const elSkus = document.getElementById('kpi_tong_sku');
        const elAlerts = document.getElementById('kpi_canh_bao');
        const elTx = document.getElementById('kpi_giao_dich');

        if (elSkus && kpis.tong_sku !== undefined) elSkus.innerText = kpis.tong_sku;
        if (elAlerts && kpis.so_luong_canh_bao !== undefined) elAlerts.innerText = kpis.so_luong_canh_bao;
        if (elTx && kpis.tong_giao_dich_30_ngay !== undefined) elTx.innerText = kpis.tong_giao_dich_30_ngay;
      }
    } catch (e) {
      console.error('[Realtime] Lỗi khi cập nhật Dashboard:', e);
    }
  }
}

// Khởi chạy WebSocket Client ngay khi trang tải xong
document.addEventListener('DOMContentLoaded', () => {
  window.smartLogisWS = new SmartLogisWebSocketClient();
});
