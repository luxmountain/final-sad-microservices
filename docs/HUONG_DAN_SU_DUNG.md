# Hướng dẫn sử dụng — Bookstore Microservices

Tài liệu này mô tả cách chạy dự án, các trang/chức năng theo router, và cách gọi API qua Nginx / API Gateway.

> **Tài liệu liên quan**
> - [API Documentation](./API_Documentation.md) — chi tiết endpoint REST
> - [Luồng hoạt động AI](./AI_LUONG_HOAT_DONG.md) — cơ chế xử lý AI Behavior & RAG

---

## 1. Tổng quan kiến trúc

Hệ thống là **monorepo microservices** cho nền tảng thương mại điện tử (sách, quần áo và nhiều loại sản phẩm khác). Luồng truy cập chuẩn:

```
Trình duyệt / Client
        │
        ▼
   Nginx (:80)          ← điểm vào chính khi chạy Docker
        │
        ├── /api/*  ──► Microservice tương ứng (REST JSON)
        │
        └── /*      ──► api-gateway (:8000) — giao diện HTML + proxy nội bộ
```

| Thành phần | Vai trò |
|---|---|
| **nginx** | Reverse proxy, phân luồng `/api/*` tới từng service |
| **api-gateway** | Giao diện web (Django), proxy API, tracking hành vi, gợi ý cá nhân hóa |
| **auth-service** | Đăng ký, đăng nhập JWT |
| **user-service** | Khách hàng, nhân viên, báo cáo quản trị (gộp customer/staff/manager) |
| **product-service** | Sản phẩm: sách, quần áo và 8 loại khác |
| **cart / order / pay / ship** | Giỏ hàng, đơn hàng, thanh toán, vận chuyển |
| **catalog-service** | Danh mục / thể loại |
| **comment-rate-service** | Đánh giá & bình luận |
| **recommender-ai-service** | Gợi ý sách theo lịch sử review (collaborative filtering) |
| **ai-behavior-service** | Phân tích hành vi LSTM, graph Neo4j, GNN, chatbot RAG |
| **postgres-db** | Cơ sở dữ liệu chính |
| **redis** | Cache session chat & behavior profile |
| **neo4j** | Đồ thị tương tác User→Product |
| **rabbitmq** | Message broker cho order/pay/ship workers |

---

## 2. Yêu cầu & cài đặt

### 2.1. Chạy bằng Docker (khuyến nghị)

**Yêu cầu:** Git, Docker, Docker Compose.

```bash
git clone <repo-url>
cd final-sad-microservices
docker-compose up --build -d
```

**Truy cập sau khi khởi động:**

| Dịch vụ | URL |
|---|---|
| Website (qua Nginx) | http://localhost |
| API Gateway trực tiếp (dev) | http://localhost:8000 *(nếu expose)* |
| Swagger UI | http://localhost/api/docs/ |
| ReDoc | http://localhost/api/redoc/ |
| Neo4j Browser | http://localhost:7474 *(user: `neo4j`, pass: `lux123`)* |
| RabbitMQ Management | http://localhost:15673 *(guest/guest)* |
| Redis | localhost:6380 |

**Dừng hệ thống:**

```bash
docker-compose down
```

**Monitoring (tùy chọn):**

```bash
docker-compose --profile monitoring up -d
# Prometheus :9090, Grafana :3000, Kibana :5601
```

### 2.2. Cấu hình AI Behavior Service

Service AI cần file `ai-behavior-service/.env`. Các biến quan trọng:

| Biến | Mô tả |
|---|---|
| `API_KEY` | Khóa xác thực API (mặc định khớp gateway: `bookstore-ai-secret-key-2024`) |
| `DEEPSEEK_API_KEY` | Khóa DeepSeek cho chatbot RAG (không có → chế độ mock) |
| `NEO4J_URI` | `bolt://neo4j:7687` (Docker) |
| `REDIS_HOST` / `REDIS_PORT` | Cache hội thoại & profile |

### 2.3. Chạy từng service thủ công (dev)

Mỗi service Django:

```bash
cd <service-folder>
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver 8000
```

AI Behavior Service (FastAPI):

```bash
cd ai-behavior-service
pip install -r requirements.txt
uvicorn module4_api.main:app --host 0.0.0.0 --port 8020 --reload
```

---

## 3. Router giao diện web (API Gateway)

Các route HTML do **api-gateway** phục vụ (qua Nginx tại `http://localhost/...`).

| Route | Phương thức | Chức năng |
|---|---|---|
| `/` | GET | Trang chủ — danh sách sản phẩm, gợi ý AI |
| `/health/` | GET | Health check gateway |
| `/login/` | GET | Trang đăng nhập |
| `/logout/` | GET/POST | Đăng xuất (xóa cookie JWT) |
| `/auth/` | GET | Trang xác thực |
| `/listing/` | GET | Danh sách / lọc sản phẩm |
| `/product/<product_id>/` | GET | Chi tiết sản phẩm (vd: `P01`, `book_5`) |
| `/cart/` | GET | Giỏ hàng |
| `/checkout/` | GET | Thanh toán (gọi ship + pay service) |
| `/orders/` | GET | Lịch sử đơn hàng |
| `/staff/` | GET | Dashboard nhân viên (đơn hàng, kho, danh mục) |
| `/manager/` | GET | Dashboard quản trị |
| `/track/` | POST | **Tracking hành vi** — cập nhật session + ghi Neo4j |
| `/recommendations/` | GET | **Gợi ý cá nhân hóa** — 4 sản phẩm (graph + content + behavior) |
| `/api/docs/` | GET | Swagger UI |
| `/api/redoc/` | GET | ReDoc |
| `/api/schema/` | GET | OpenAPI schema |

### Proxy API vạn năng (Gateway)

Pattern: `/api/<service_name>/<path>`

Gateway chuyển tiếp tới microservice tương ứng. Ví dụ:

- `/api/product/products/` → product-service
- `/api/cart/carts/1/` → cart-service
- `/api/ai-behavior/chat` → ai-behavior-service

Danh sách `service_name` hỗ trợ: `customer`, `staff`, `admin`, `cart`, `order`, `pay`, `ship`, `book`, `clothes`, `product`, `catalog`, `comment`, `ai`, `auth`, `ai-behavior`.

---

## 4. Router API qua Nginx (`/api/...`)

Khi truy cập qua Nginx (`http://localhost`), các prefix sau được route **trực tiếp** tới microservice (không qua Django gateway proxy):

| Prefix Nginx | Service | Ví dụ endpoint |
|---|---|---|
| `/api/auth/` | auth-service | `POST /api/auth/login/` |
| `/api/customer/` | user-service | `GET /customers/` |
| `/api/staff/` | user-service | `GET /staffs/` |
| `/api/user/` | user-service | *(alias user-service)* |
| `/api/product/` | product-service | `GET /products/` |
| `/api/book/` | product-service | `GET /books/` |
| `/api/clothes/` | product-service | `GET /clothes/` |
| `/api/cart/` | cart-service | `GET /carts/<id>/` |
| `/api/order/` | order-service | `POST /orders/` |
| `/api/pay/` | pay-service | `POST /payments/` |
| `/api/ship/` | ship-service | `POST /shippings/` |
| `/api/catalog/` | catalog-service | `GET /categories/` |
| `/api/comment/` | comment-rate-service | `POST /reviews/` |
| `/api/ai-behavior/` | ai-behavior-service | `POST /chat` |
| `/api/ai/` | recommender-ai-service | `POST /ai-suggest/` |

> **Lưu ý:** Prefix `/api/ai-behavior/` được Nginx strip — request tới `http://localhost/api/ai-behavior/chat` sẽ tới FastAPI endpoint `/chat`.

---

## 5. Chức năng theo microservice

### 5.1. Auth Service (`/api/auth/`)

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/register/` | Đăng ký tài khoản |
| POST | `/login/` | Đăng nhập, nhận JWT access + refresh token |
| POST | `/token/refresh/` | Làm mới access token |

### 5.2. User Service

**Khách hàng** — prefix `/api/customer/`:

| Method | Endpoint | Mô tả |
|---|---|---|
| GET/POST | `/customers/` | Liệt kê / tạo hồ sơ khách |
| GET/PUT/PATCH/DELETE | `/customers/<id>/` | Chi tiết / cập nhật khách |

**Nhân viên** — prefix `/api/staff/`:

| Method | Endpoint | Mô tả |
|---|---|---|
| GET/POST | `/staffs/` | Quản lý nhân viên |
| GET/PUT/PATCH/DELETE | `/staffs/<id>/` | Chi tiết nhân viên |
| POST | `/staffs/<id>/add-product/` | Nhân viên thêm sản phẩm vào kho |

**Quản trị** — prefix `/api/admin/` hoặc gateway `admin`:

| Method | Endpoint | Mô tả |
|---|---|---|
| GET/POST | `/reports/` | Báo cáo doanh thu / hoạt động |
| GET | `/reports/<id>/` | Chi tiết báo cáo |

### 5.3. Product Service

| Method | Endpoint | Mô tả |
|---|---|---|
| GET/POST | `/books/`, `/books/<id>/` | Sách (tương thích cũ) |
| GET/POST | `/clothes/`, `/clothes/<id>/` | Quần áo |
| GET | `/products/`, `/products/<id>/` | **Unified** — tất cả loại sản phẩm |
| GET/POST | `/<type>/`, `/<type>/<id>/` | 8 loại mới: `stationery`, `electronics`, `toy`, `cosmetic`, `bag`, `shoe`, `watch`, `gift` |

### 5.4. Cart Service

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/carts/` | Tạo giỏ hàng |
| GET | `/carts/<customer_id>/` | Xem giỏ theo khách |
| POST | `/cart-items/` | Thêm sản phẩm |
| PUT/DELETE | `/cart-items/<item_id>/` | Sửa số lượng / xóa |

### 5.5. Order Service

| Method | Endpoint | Mô tả |
|---|---|---|
| GET/POST | `/orders/` | Danh sách / tạo đơn |
| PUT/PATCH | `/orders/<id>/status/` | Cập nhật trạng thái |

Worker `order-worker` lắng nghe RabbitMQ để xử lý đơn bất đồng bộ.

### 5.6. Pay Service

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/payment-methods/` | Phương thức thanh toán |
| POST | `/payments/` | Xử lý thanh toán |

### 5.7. Ship Service

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/shipping-methods/` | Phương thức vận chuyển |
| POST | `/shippings/` | Tạo / cập nhật vận chuyển |

### 5.8. Catalog Service

| Method | Endpoint | Mô tả |
|---|---|---|
| GET/POST | `/categories/` | Quản lý danh mục |

### 5.9. Comment & Rate Service

| Method | Endpoint | Mô tả |
|---|---|---|
| GET/POST | `/reviews/` | Xem / gửi đánh giá sản phẩm |

### 5.10. Recommender AI Service (`/api/ai/`)

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/ai-suggest/` | Gợi ý **1 cuốn sách** dựa trên review & thể loại yêu thích |

Body mẫu: `{ "customer_id": 1 }`

> Service này dùng thuật toán rule-based + collaborative filtering trên review. Khác với **ai-behavior-service** (LSTM + graph + RAG).

### 5.11. AI Behavior Service (`/api/ai-behavior/`)

Xem chi tiết tại [AI_LUONG_HOAT_DONG.md](./AI_LUONG_HOAT_DONG.md).

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/health` | Trạng thái LSTM, chatbot, GNN, Neo4j |
| POST | `/analyze-behavior` | Phân loại hành vi khách (LSTM) |
| POST | `/chat` | Chatbot tư vấn RAG |
| GET | `/user/{id}/profile` | Behavior profile đã cache |
| POST | `/feedback` | Góp ý chatbot (rating 1–5) |
| POST | `/interact` | Ghi tương tác User→Product vào Neo4j |
| GET | `/recommend` | Gợi ý từ graph traversal |
| GET | `/user/{id}/history` | Lịch sử tương tác trong graph |
| GET | `/gnn/status` | Trạng thái model GNN |
| POST | `/gnn/train` | Train GNN (background) |
| GET | `/gnn/product/{id}/similar` | Sản phẩm tương tự (cosine) |
| POST | `/gnn/user/embedding` | Embedding user (cold-start aware) |
| POST | `/clear-session/{user_id}` | Xóa lịch sử chat |

Hầu hết endpoint yêu cầu header: `X-API-Key: bookstore-ai-secret-key-2024`

---

## 6. Luồng nghiệp vụ chính

### 6.1. Mua hàng

```
Đăng nhập → Duyệt sản phẩm → Thêm giỏ (/api/cart/)
    → Checkout (/checkout/) → POST /api/order/orders/
    → POST /api/pay/payments/ → POST /api/ship/shippings/
    → Xem đơn (/orders/)
```

### 6.2. Tracking & gợi ý (tích hợp frontend)

```
User xem/click/tìm kiếm/thêm giỏ
    → POST /track/  (gateway)
        ├─ Cập nhật session behavior (LSTM features)
        └─ Forward /interact → Neo4j graph

Đủ dữ liệu hành vi
    → POST /analyze-behavior (nội bộ gateway)
    → Lưu behavior_label (impulse_buyer, researcher, ...)

User mở trang gợi ý
    → GET /recommendations/
        ├─ Tầng 1: GET /recommend (Neo4j graph)
        ├─ Tầng 2: Ưu tiên loại sản phẩm đã xem
        └─ Tầng 3: Sort theo behavior label
```

### 6.3. Chatbot tư vấn

```
Frontend → POST /api/ai-behavior/chat
    { "user_id": "user_42", "message": "Có sách AI nào hay không?" }
    Header: X-API-Key

→ RAG pipeline (retrieve KB + rerank + DeepSeek)
→ Cá nhân hóa theo behavior profile nếu đã phân tích
```

---

## 7. Ví dụ gọi API nhanh

```bash
# Health check AI
curl http://localhost/api/ai-behavior/health

# Danh sách sản phẩm
curl http://localhost/api/product/products/

# Phân tích hành vi
curl -X POST http://localhost/api/ai-behavior/analyze-behavior \
  -H "Content-Type: application/json" \
  -H "X-API-Key: bookstore-ai-secret-key-2024" \
  -d '{
    "user_id": "user_1",
    "sessions": [{
      "click_count": 5, "view_count": 10, "purchase_count": 0,
      "time_on_page": 120, "cart_add_count": 2, "search_count": 3,
      "session_duration": 15, "avg_price_viewed": 250000,
      "category_diversity": 0.5, "return_rate": 0.1
    }]
  }'

# Chatbot
curl -X POST http://localhost/api/ai-behavior/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: bookstore-ai-secret-key-2024" \
  -d '{"user_id": "user_1", "message": "Gợi ý sách lập trình cho người mới"}'

# Gợi ý sách theo review (recommender-ai-service)
curl -X POST http://localhost/api/ai/ai-suggest/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1}'
```

---

## 8. Xử lý sự cố thường gặp

| Triệu chứng | Nguyên nhân có thể | Cách xử lý |
|---|---|---|
| Chatbot trả mock response | Thiếu `DEEPSEEK_API_KEY` | Thêm key vào `.env`, restart ai-behavior-service |
| `/recommend` trả rỗng | Neo4j chưa có lịch sử / offline | Kiểm tra Neo4j :7474, gọi `/track/` với product |
| 401 từ AI API | Thiếu/sai `X-API-Key` | Dùng key khớp `API_KEY` trong `.env` |
| Gateway 500 proxy | Service nội bộ chưa sẵn sàng | `docker-compose ps`, xem log từng container |
| GNN endpoints 503 | Model chưa train | `POST /gnn/train` hoặc chờ training xong |

---

*Tài liệu cập nhật theo codebase microservices — Software Engineering Project.*
