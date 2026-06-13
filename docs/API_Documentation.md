# API Documentation

Tài liệu REST API cho dự án Bookstore Microservices. Cập nhật theo kiến trúc hiện tại (user-service, product-service, ai-behavior-service).

> Xem thêm: [Hướng dẫn sử dụng](./HUONG_DAN_SU_DUNG.md) | [Luồng AI](./AI_LUONG_HOAT_DONG.md)

---

## Base URL

Khi chạy Docker với Nginx:

```
http://localhost/api/<prefix>/
```

Ví dụ: `http://localhost/api/product/products/`

Khi gọi qua API Gateway proxy:

```
http://localhost/api/<service_name>/<path>
```

Ví dụ: `http://localhost/api/product/products/` hoặc `http://localhost/api/cart/carts/1/`

---

## 1. API Gateway — Giao diện & Proxy

### Trang web (HTML)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/` | Trang chủ |
| GET | `/health/` | Health check gateway |
| GET | `/login/` | Trang đăng nhập |
| GET | `/logout/` | Đăng xuất |
| GET | `/auth/` | Trang xác thực |
| GET | `/listing/` | Danh sách sản phẩm |
| GET | `/product/<product_id>/` | Chi tiết sản phẩm |
| GET | `/cart/` | Giỏ hàng |
| GET | `/checkout/` | Thanh toán |
| GET | `/orders/` | Lịch sử đơn hàng |
| GET | `/staff/` | Dashboard nhân viên |
| GET | `/manager/` | Dashboard quản trị |
| POST | `/track/` | Tracking hành vi + ghi graph |
| GET | `/recommendations/` | Gợi ý cá nhân hóa (4 SP) |

### Tài liệu OpenAPI

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/schema/` | OpenAPI schema |
| GET | `/api/docs/` | Swagger UI |
| GET | `/api/redoc/` | ReDoc |

### Universal Proxy

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| * | `/api/<service_name>/<path>` | Chuyển tiếp tới microservice |

`service_name`: `auth`, `customer`, `staff`, `admin`, `cart`, `order`, `pay`, `ship`, `book`, `clothes`, `product`, `catalog`, `comment`, `ai`, `ai-behavior`

---

## 2. Auth Service

**Prefix Nginx:** `/api/auth/`

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/register/` | Đăng ký |
| POST | `/login/` | Đăng nhập JWT |
| POST | `/token/refresh/` | Refresh token |

---

## 3. User Service

Gộp customer, staff, manager.

### Khách hàng — `/api/customer/`

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/customers/` | Liệt kê khách |
| POST | `/customers/` | Tạo khách |
| GET | `/customers/<id>/` | Chi tiết |
| PUT/PATCH/DELETE | `/customers/<id>/` | Cập nhật / xóa |

### Nhân viên — `/api/staff/`

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/staffs/` | Liệt kê nhân viên |
| POST | `/staffs/` | Tạo nhân viên |
| GET/PUT/PATCH/DELETE | `/staffs/<id>/` | CRUD nhân viên |
| POST | `/staffs/<id>/add-product/` | Thêm sản phẩm |

### Quản trị — `/api/admin/` (gateway: `admin`)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET/POST | `/reports/` | Báo cáo |
| GET | `/reports/<id>/` | Chi tiết báo cáo |

---

## 4. Product Service

**Prefix:** `/api/product/`, `/api/book/`, `/api/clothes/`

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET/POST | `/books/` | Sách |
| GET/PUT/PATCH/DELETE | `/books/<id>/` | Chi tiết sách |
| GET/POST | `/clothes/` | Quần áo |
| GET/PUT/PATCH/DELETE | `/clothes/<id>/` | Chi tiết quần áo |
| GET | `/products/` | Tất cả loại sản phẩm |
| GET | `/products/<id>/` | Chi tiết unified |
| GET/POST | `/<type>/` | `stationery`, `electronics`, `toy`, `cosmetic`, `bag`, `shoe`, `watch`, `gift` |
| GET/PUT/PATCH/DELETE | `/<type>/<id>/` | CRUD theo loại |

---

## 5. Cart Service — `/api/cart/`

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/carts/` | Tạo giỏ |
| GET | `/carts/<customer_id>/` | Xem giỏ |
| POST | `/cart-items/` | Thêm item |
| PUT | `/cart-items/<item_id>/` | Cập nhật số lượng |
| DELETE | `/cart-items/<item_id>/` | Xóa item |

---

## 6. Order Service — `/api/order/`

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET/POST | `/orders/` | Danh sách / tạo đơn |
| PUT/PATCH | `/orders/<id>/status/` | Cập nhật trạng thái |

---

## 7. Pay Service — `/api/pay/`

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/payment-methods/` | Phương thức thanh toán |
| POST | `/payments/` | Xử lý thanh toán |

---

## 8. Ship Service — `/api/ship/`

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/shipping-methods/` | Phương thức vận chuyển |
| POST | `/shippings/` | Tạo / cập nhật vận chuyển |

---

## 9. Catalog Service — `/api/catalog/`

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET/POST | `/categories/` | Danh mục |

---

## 10. Comment & Rate Service — `/api/comment/`

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET/POST | `/reviews/` | Đánh giá sản phẩm |

---

## 11. Recommender AI Service — `/api/ai/`

Gợi ý sách dựa trên review (collaborative filtering).

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/ai-suggest/` | Gợi ý 1 sách cho `customer_id` |

**Body:** `{ "customer_id": 1 }`

---

## 12. AI Behavior Service — `/api/ai-behavior/`

FastAPI service — phân tích hành vi, graph, RAG chatbot.

**Auth:** Header `X-API-Key: bookstore-ai-secret-key-2024` (trừ `/health`, `/gnn/status`)

### Core

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/health` | Health check |
| POST | `/analyze-behavior` | Phân loại hành vi LSTM |
| POST | `/chat` | Chatbot RAG |
| GET | `/user/<user_id>/profile` | Behavior profile |
| POST | `/feedback` | Feedback chat (rating 1–5) |
| POST | `/clear-session/<user_id>` | Xóa session chat |

### Graph (Neo4j)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/interact` | Ghi tương tác User→Product |
| GET | `/recommend` | Gợi ý graph (`?user_id=&behavior_label=&top_k=`) |
| GET | `/user/<user_id>/history` | Lịch sử tương tác |

### GNN

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/gnn/status` | Trạng thái model |
| POST | `/gnn/train` | Train GNN (background) |
| GET | `/gnn/product/<id>/embedding` | Product embedding |
| GET | `/gnn/product/<id>/similar` | Sản phẩm tương tự |
| POST | `/gnn/user/embedding` | User embedding |

Chi tiết luồng xử lý: [AI_LUONG_HOAT_DONG.md](./AI_LUONG_HOAT_DONG.md)

---

## Mapping Nginx → Service

| Location | Upstream |
|----------|----------|
| `/api/auth/` | auth-service:8000 |
| `/api/customer/`, `/api/staff/`, `/api/user/` | user-service:8000 |
| `/api/product/`, `/api/book/`, `/api/clothes/` | product-service:8000 |
| `/api/cart/` | cart-service:8000 |
| `/api/order/` | order-service:8000 |
| `/api/pay/` | pay-service:8000 |
| `/api/ship/` | ship-service:8000 |
| `/api/catalog/` | catalog-service:8000 |
| `/api/comment/` | comment-rate-service:8000 |
| `/api/ai-behavior/` | ai-behavior-service:8020 |
| `/api/ai/` | recommender-ai-service:8000 |
| `/` (còn lại) | api-gateway:8000 |

---

*Cập nhật: 2026 — Bookstore Microservices Project*
