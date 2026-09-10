# HƯỚNG DẪN TRIỂN KHAI TÊN MIỀN `smartlogis-ai.com` & CẤU HÌNH NGINX REVERSE PROXY SSL

Tài liệu này cung cấp hướng dẫn toàn diện từ mức kiến trúc đến từng câu lệnh thực tế để triển khai hệ thống **SmartLogis AI** dưới tên miền chính thức `smartlogis-ai.com` kết hợp **Nginx Reverse Proxy** và chứng chỉ bảo mật **SSL/TLS Let's Encrypt (Certbot)** miễn phí tự động gia hạn.

---

## 1. Sơ Đồ Kiến Trúc Điều Hướng (Reverse Proxy Traffic Flow)

```mermaid
flowchart TD
    Client[Client: PC, Laptop, Mobile] -->|HTTPS 443 / WSS| Nginx[Nginx Reverse Proxy :80/:443]
    
    subgraph Routing_Rules [Luật Điều Hướng Nginx]
        Nginx -->|/api/* & /docs| Backend[FastAPI Backend :8000]
        Nginx -->|/ws/* (WebSocket Upgrade)| WS_Engine[Realtime WebSocket Engine :8000]
        Nginx -->|/ (Root & Assets)| Frontend[Frontend App :3000 / SSR Fallback]
    end

    subgraph Database_Layer [Tầng Dữ Liệu]
        Backend --> Postgres[(PostgreSQL 15 :5432)]
        Backend --> Redis[(Redis Cache / PubSub)]
    end

    subgraph Security_Layer [Bảo Mật Tự Động]
        Certbot[Certbot Let's Encrypt] -->|ACME Challenge :80| Nginx
        Certbot -->|Auto Renew 12h| SSL_Certs[(SSL Certs /etc/letsencrypt)]
        SSL_Certs -.->|Mounted| Nginx
    end
```

---

## 2. Thiết Lập Môi Trường Thử Nghiệm Local / LAN (File `hosts`)

Khi chưa đăng ký tên miền thật trên Internet hoặc muốn kiểm thử hệ thống trước khi Go-Live, bạn có thể ánh xạ tên miền `smartlogis-ai.com` trỏ thẳng về máy chủ nội bộ thông qua file `hosts`.

### 2.1. Cấu hình trên Windows (Máy tính thử nghiệm)
1. Bấm phím `Windows`, gõ `Notepad`.
2. Nhấp chuột phải vào **Notepad** -> Chọn **"Run as administrator"** (Chạy với quyền Quản trị viên).
3. Trong Notepad, chọn `File` -> `Open...` và mở đường dẫn:
   ```text
   C:\Windows\System32\drivers\etc\hosts
   ```
   *(Lưu ý chọn bộ lọc file là "All Files (*.*)" ở góc dưới bên phải để thấy file `hosts`)*.
4. Thêm các dòng sau vào cuối file:
   - **Nếu test ngay trên chính máy chủ:**
     ```text
     127.0.0.1       smartlogis-ai.com
     127.0.0.1       www.smartlogis-ai.com
     ```
   - **Nếu test từ một máy tính / laptop khác trong cùng mạng WiFi / LAN:**
     *(Thay `192.168.1.15` bằng địa chỉ IP LAN của máy chủ do `start_server.bat` in ra)*
     ```text
     192.168.1.15    smartlogis-ai.com
     192.168.1.15    www.smartlogis-ai.com
     ```
5. Lưu file (`Ctrl + S`).
6. Mở Command Prompt (`cmd`) và xóa bộ nhớ cache DNS:
   ```cmd
   ipconfig /flushdns
   ```

### 2.2. Cấu hình trên Linux / macOS
Mở terminal và chỉnh sửa file `/etc/hosts`:
```bash
sudo nano /etc/hosts
```
Thêm dòng sau:
```text
127.0.0.1       smartlogis-ai.com www.smartlogis-ai.com
```
Lưu file (`Ctrl + O`, `Enter`, `Ctrl + X`). Xóa cache DNS:
- Trên macOS: `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`
- Trên Linux: `sudo systemd-resolve --flush-caches`

### 2.3. Cấu hình trên Thiết Bị Di Động (Android / iOS)
- **Cách 1 (Khuyên dùng):** Sử dụng Router Wi-Fi hỗ trợ tính năng **Local DNS Records / Static DNS Mapping** (như Asus, OpenWrt, Mikrotik, TP-Link Archer): Gán domain `smartlogis-ai.com` trỏ về IP LAN của máy chủ (ví dụ `192.168.1.15`).
- **Cách 2:** Sử dụng công cụ nội bộ như **AdGuard Home** hoặc **Pi-hole** trong mạng gia đình/văn phòng và thêm một dòng DNS Rewrite.

---

## 3. Cấu Hình Tên Miền Thực Tế Trên Internet (DNS Records)

Khi triển khai hệ thống lên máy chủ Cloud (VPS như DigitalOcean, AWS EC2, Google Cloud, Linode, Viettel IDC, BKHOST):

### 3.1. Tạo bản ghi DNS tại Nhà Cung Cấp Domain (Cloudflare, Namecheap, v.v.)
Truy cập trang quản trị DNS của tên miền `smartlogis-ai.com` và thêm 2 bản ghi sau:

| Loại Bản Ghi (Type) | Tên (Name / Host) | Giá Trị (Value / Points to) | TTL | Proxy Status (Cloudflare) |
| :--- | :--- | :--- | :--- | :--- |
| **A Record** | `@` | `<IPv4_Public_Của_VPS>` *(VD: 103.20.144.50)* | Auto / 300s | DNS Only (hoặc Proxied) |
| **A Record** / **CNAME** | `www` | `smartlogis-ai.com` *(hoặc IP VPS)* | Auto / 300s | DNS Only (hoặc Proxied) |

> [!IMPORTANT]
> Nếu bạn sử dụng **Cloudflare**, ở bước khởi tạo chứng chỉ SSL Certbot đầu tiên, hãy tạm thời để **Proxy status = DNS Only** (đám mây xám) để Certbot xác thực qua cổng 80 thành công. Sau khi có chứng chỉ, bạn có thể bật lại chế độ **Full (Strict) SSL** trên Cloudflare.

### 3.2. Mở Cổng Tường Lửa (Firewall Port 80 & 443)
Trên máy chủ Linux (Ubuntu/Debian):
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```
Nếu dùng AWS / GCP: Hãy đảm bảo Inbound Rules của Security Group đã mở port `80 (HTTP)` và `443 (HTTPS)` cho `0.0.0.0/0`.

---

## 4. Hướng Dẫn Cấp Phát Chứng Chỉ SSL Tự Động Với Certbot

### 4.1. Tạo Chứng Chỉ Tự Ký (Self-Signed) Tạm Thời Cho Môi Trường Local / Khởi Động Ban Đầu
Để Nginx có thể khởi động ngay mà không báo lỗi thiếu file `.pem`, bạn có thể tạo chứng chỉ tự ký tạm thời trong thư mục `certbot/conf`:

#### Trên Windows (PowerShell):
```powershell
# Tạo thư mục lưu chứng chỉ nếu chưa có
New-Item -ItemType Directory -Force -Path "certbot/conf/live/smartlogis-ai.com"

# Sinh cặp key và chứng chỉ tự ký bằng OpenSSL (nếu có cài OpenSSL)
openssl req -x509 -nodes -newkey rsa:2048 -days 365 `
  -keyout "certbot/conf/live/smartlogis-ai.com/privkey.pem" `
  -out "certbot/conf/live/smartlogis-ai.com/fullchain.pem" `
  -subj "/CN=smartlogis-ai.com"
```

#### Trên Linux / macOS:
```bash
mkdir -p certbot/conf/live/smartlogis-ai.com
openssl req -x509 -nodes -newkey rsa:2048 -days 365 \
  -keyout certbot/conf/live/smartlogis-ai.com/privkey.pem \
  -out certbot/conf/live/smartlogis-ai.com/fullchain.pem \
  -subj "/CN=smartlogis-ai.com"
```

### 4.2. Cấp Phát Chứng Chỉ SSL Let's Encrypt Chính Thức (Production)
Khi tên miền đã trỏ về IP công khai của máy chủ VPS:

1. **Khởi động Nginx để mở cổng 80 tiếp nhận ACME challenge:**
   ```bash
   docker compose up -d nginx
   ```

2. **Chạy lệnh Certbot yêu cầu cấp phát chứng chỉ SSL thật:**
   ```bash
   docker compose run --rm certbot certonly --webroot \
     -w /var/www/certbot \
     -d smartlogis-ai.com \
     -d www.smartlogis-ai.com \
     --email admin@smartlogis-ai.com \
     --agree-tos \
     --no-eff-email \
     --force-renewal
   ```

3. **Tải lại cấu hình Nginx để áp dụng chứng chỉ mới:**
   ```bash
   docker compose exec nginx nginx -s reload
   ```

### 4.3. Cơ Chế Tự Động Gia Hạn (Automatic Renewal)
- Container `smartlogis_certbot` trong `docker-compose.yml` được cấu hình vòng lặp tự động kiểm tra gia hạn mỗi **12 giờ**:
  ```yaml
  entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
  ```
- Khi chứng chỉ còn dưới 30 ngày sử dụng, Certbot sẽ tự động gia hạn với Let's Encrypt hoàn toàn miễn phí mà không cần can thiệp thủ công.

---

## 5. Khởi Chạy Toàn Bộ Hệ Thống Với Docker Compose

Chạy toàn bộ cụm dịch vụ (PostgreSQL + PgAdmin + Backend FastAPI + WebSocket + Nginx Reverse Proxy + Certbot):

```bash
docker compose up -d --build
```

Kiểm tra trạng thái các container:
```bash
docker compose ps
```

Kết quả mong đợi:
```text
NAME                 IMAGE                  STATUS         PORTS
smartlogis_postgres  postgres:15-alpine     Up (healthy)   0.0.0.0:5432->5432/tcp
smartlogis_pgadmin   dpage/pgadmin4:latest  Up             0.0.0.0:5050->80/tcp
smartlogis_web       smartlogis-ai-web      Up (healthy)   0.0.0.0:8000->8000/tcp
smartlogis_nginx     nginx:1.25-alpine      Up             0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
smartlogis_certbot   certbot/certbot:latest Up             
```

---

## 6. Kiểm Thử & Nghiệm Thu Kết Nối

### 6.1. Kiểm Tra HTTP Redirect sang HTTPS:
```bash
curl -I http://smartlogis-ai.com
```
*Kết quả:* Trả về mã `301 Moved Permanently` với header `Location: https://smartlogis-ai.com/`.

### 6.2. Kiểm Tra Endpoint API Backend qua Domain:
```bash
curl -k https://smartlogis-ai.com/api/v1/kho/kpis
```
*(Thêm cờ `-k` nếu đang dùng chứng chỉ tự ký trên môi trường local)*.

### 6.3. Kiểm Tra Bắt Tay WebSocket Realtime (WSS):
- Mở trình duyệt truy cập: `https://smartlogis-ai.com`.
- Mở `DevTools (F12)` -> Chọn tab **Console** hoặc **Network (WS)**.
- Quan sát thông điệp kết nối:
  ```text
  [WebSocket] Đang kết nối tới: wss://smartlogis-ai.com/ws/inventory
  [WebSocket] Kết nối máy chủ thời gian thực SmartLogis AI thành công.
  ```
- Đèn trạng thái trên Topbar chuyển sang chấm xanh: **"Realtime: Đang kết nối"**.
