# Sử dụng Python 3.9 làm base image
FROM python:3.9-slim

# Cài đặt các gói cần thiết
RUN apt update \
    && apt install --no-install-recommends -y python3-pip git zip curl htop libgl1 libglib2.0-0 libpython3-dev gnupg g++ libusb-1.0-0 \
    && apt clean

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép file requirements.txt vào container
COPY requirements.txt .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Expose cổng mà Flask sẽ chạy
EXPOSE 5000

# Chạy ứng dụng Flask
CMD ["python", "be_RSTP.py"]