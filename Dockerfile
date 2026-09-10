# Dockerfile - Đóng gói ứng dụng SmartLogis AI
# Base image Python 3.12 Slim tối ưu dung lượng và hiệu năng
FROM python:3.12-slim

# Thiết lập biến môi trường
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

WORKDIR /app

# Cài đặt các gói hệ thống cần thiết (curl phục vụ healthcheck, gcc cho dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt thư viện Python từ requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Mở cổng dịch vụ 8000
EXPOSE 8000

# Khởi chạy ứng dụng thông qua Uvicorn ASGI Server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
