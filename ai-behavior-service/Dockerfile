FROM python:3.11-slim

# Cài đặt system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements trước (tận dụng Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code
COPY . .

# Tạo thư mục models
RUN mkdir -p models

# Expose port
EXPOSE 8020

# Startup: train model (nếu chưa có) + build KB + start API
CMD ["python", "-m", "uvicorn", "module4_api.main:app", "--host", "0.0.0.0", "--port", "8020"]
