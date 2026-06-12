# Đánh giá dự án so với yêu cầu đề bài

**Ngày đánh giá:** 2026-06-11  
**Dự án:** Bookstore Microservices (E-Commerce)

---

## Nguồn yêu cầu

| Ký hiệu | File | Mô tả |
|----------|------|--------|
| **TL** | `docs/requirement/tieuluan_Monhoc_KientrucThietke_PM_04-2026.pdf` | Tiểu luận SoAD - Kiến trúc và Thiết kế PM (GVHD: Trần Đình Quế) |
| **DG** | `docs/requirement/danhgia_kientruc_thietke_2026.pdf` | Đánh giá kiến trúc thiết kế (PDF scan, không trích xuất text được) |
| **BT** | `docs/requirement/baitap_dudoan_diemthi.pdf` | Bài tập Option: Dự đoán điểm thi bằng ML |

---

## Chương 2: E-Commerce Microservices & DDD (TL, trang 11-20)

### Functional Requirements (TL §2.1.1, trang 11)

| ID | Yêu cầu | Trạng thái | Nguồn | Ghi chú |
|----|----------|:-----------:|-------|---------|
| FR-01 | Quản lý sản phẩm (đa domain: book, electronics, fashion) | ✅ | TL §2.1.1, tr.11 | `product-service` hỗ trợ books + clothes, có `seeds/clothes_catalog.json` |
| FR-02 | Quản lý người dùng (admin, staff, customer) | ✅ | TL §2.1.1, tr.11 | `user-service/modules/admin/`, `modules/customer/`, RBAC |
| FR-03 | Giỏ hàng (cart) | ✅ | TL §2.1.1, tr.11 | `cart-service` đầy đủ CRUD |
| FR-04 | Đặt hàng (order) | ✅ | TL §2.1.1, tr.11 | `order-service` + RabbitMQ worker |
| FR-05 | Thanh toán (payment) | ✅ | TL §2.1.1, tr.11 | `pay-service` + worker |
| FR-06 | Giao hàng (shipping) | ✅ | TL §2.1.1, tr.11 | `ship-service` + worker |
| FR-07 | Tìm kiếm và gợi ý sản phẩm | ✅ | TL §2.1.1, tr.11 | `recommender-ai-service` + `ai-behavior-service` |

### Non-functional Requirements (TL §2.1.2, trang 11)

| ID | Yêu cầu | Trạng thái | Nguồn | Ghi chú |
|----|----------|:-----------:|-------|---------|
| NFR-01 | Scalability: scale từng service độc lập | ✅ | TL §2.1.2, tr.11 | Microservices + K8s manifests có resource limits |
| NFR-02 | High Availability: hệ thống luôn sẵn sàng | ⚠️ | TL §2.1.2, tr.11 | Health checks có, nhưng chưa có replicas/load balancing |
| NFR-03 | Security: JWT, authentication | ✅ | TL §2.1.2, tr.11 | `auth-service` với djangorestframework-simplejwt |
| NFR-04 | Maintainability: dễ bảo trì | ✅ | TL §2.1.2, tr.11 | Monorepo, service tách biệt, DDD trong user/product-service |

### Bài tập (TL §2.10.6, trang 20)

| ID | Yêu cầu | Trạng thái | Nguồn | Ghi chú |
|----|----------|:-----------:|-------|---------|
| BT2-01 | Vẽ Class Diagram cho toàn bộ hệ thống bằng VP | ❌ | TL §2.10.6, tr.20 | Không tìm thấy file diagram (.puml, .drawio, .vpp, hình ảnh) |
| BT2-02 | Mapping sang database schema | ⚠️ | TL §2.10.6, tr.20 | Có models.py mỗi service nhưng thiếu tài liệu mapping rõ ràng |
| BT2-03 | Triển khai database bằng MySQL/PostgreSQL | ⚠️ | TL §2.10.6, tr.20 | Chỉ dùng PostgreSQL, chưa có MySQL |

### Checklist đánh giá (TL §2.10.7, trang 20)

| ID | Yêu cầu | Trạng thái | Nguồn | Ghi chú |
|----|----------|:-----------:|-------|---------|
| CL2-01 | Có sơ đồ class đúng UML | ❌ | TL §2.10.7, tr.20 | Thiếu |
| CL2-02 | Có mapping rõ ràng sang database | ⚠️ | TL §2.10.7, tr.20 | Implicit qua Django models, chưa có tài liệu riêng |
| CL2-03 | Database tách riêng từng service | ✅ | TL §2.10.7, tr.20 | `postgres-init/init.sql` tạo 16 database riêng biệt |
| CL2-04 | Có sử dụng cả MySQL và PostgreSQL | ❌ | TL §2.10.7, tr.20 | Toàn bộ dùng PostgreSQL 15 |

---

## Chương 3: AI Service cho tư vấn sản phẩm (TL, trang 21-25)

### Bài tập (TL §3.10, trang 25)

| ID | Yêu cầu | Trạng thái | Nguồn | Ghi chú |
|----|----------|:-----------:|-------|---------|
| BT3-01 | Xây dựng model LSTM đơn giản | ✅ | TL §3.10, tr.25 | `module1_behavior/model_behavior.py` — LSTM + Attention, 5 behavior classes |
| BT3-02 | Tạo graph trong Neo4j | ✅ | TL §3.10, tr.25 | `module0_graph/` — Neo4j connector, graph builder, HeteroGraphSAGE |
| BT3-03 | Implement API recommendation | ✅ | TL §3.10, tr.25 | `module4_api/main.py` (FastAPI endpoints) |
| BT3-04 | Xây dựng chatbot cơ bản | ✅ | TL §3.10, tr.25 | `module3_rag/chatbot.py` + knowledge base FAQs |

### Checklist đánh giá (TL §3.11, trang 25)

| ID | Yêu cầu | Trạng thái | Nguồn | Ghi chú |
|----|----------|:-----------:|-------|---------|
| CL3-01 | Có pipeline AI rõ ràng | ✅ | TL §3.11, tr.25 | 5 modules: graph → behavior → knowledge → RAG → API |
| CL3-02 | Có model (LSTM) | ✅ | TL §3.11, tr.25 | Bi-LSTM + Multi-Head Attention, có `behavior_model.pth` trained |
| CL3-03 | Có Graph và RAG | ✅ | TL §3.11, tr.25 | Neo4j graph + `rag_pipeline.py` + vector DB |
| CL3-04 | Có API hoạt động | ✅ | TL §3.11, tr.25 | FastAPI trên port 8020, có auth + rate limiter |

---

## Chương 4: Xây dựng hệ thống hoàn chỉnh (TL, trang 26-32)

### Bài tập thực hành (TL §4.11, trang 32)

| ID | Yêu cầu | Trạng thái | Nguồn | Ghi chú |
|----|----------|:-----------:|-------|---------|
| BT4-01 | Triển khai các service bằng Django | ✅ | TL §4.11, tr.32 | 10 Django services hoạt động |
| BT4-02 | Kết nối qua API | ✅ | TL §4.11, tr.32 | REST calls + RabbitMQ giữa services |
| BT4-03 | Docker hóa hệ thống | ✅ | TL §4.11, tr.32 | `docker-compose.yml` với 12 services + infra |
| BT4-04 | Test full flow mua hàng + kết quả tư vấn | ⚠️ | TL §4.11, tr.32 | Có `tests/demo_e2e.py` nhưng thiếu test suite tự động |

### Checklist đánh giá (TL §4.12, trang 32)

| ID | Yêu cầu | Trạng thái | Nguồn | Ghi chú |
|----|----------|:-----------:|-------|---------|
| CL4-01 | Có API Gateway | ✅ | TL §4.12, tr.32 | Nginx reverse proxy (port 80) + Django api-gateway (SSR) |
| CL4-02 | Có JWT Auth | ✅ | TL §4.12, tr.32 | `auth-service` cấp/verify JWT tokens |
| CL4-03 | Có Docker chạy được | ✅ | TL §4.12, tr.32 | `docker-compose up --build -d` hoạt động |
| CL4-04 | Có flow order → payment → shipping | ✅ | TL §4.12, tr.32 | Saga pattern qua RabbitMQ (order-worker, pay-worker, ship-worker) |

---

## Bài tập phụ: Dự đoán điểm thi (BT, trang 1-2)

| ID | Yêu cầu | Trạng thái | Nguồn | Ghi chú |
|----|----------|:-----------:|-------|---------|
| ML-01 | Construct dataset with peer influence | ✅ | BT §2 Task 1, tr.1 | `ml-exam-prediction/predict_exam_score.ipynb` — N=800, 5 academic + 10 peer, CSV import |
| ML-02 | Train 3 models (GBoost, MLP, GraphSAGE) | ✅ | BT §2 Task 2, tr.1 | Đúng 3 model theo đề: GBoost, MLP (GNN-style), GraphSAGE |
| ML-03 | Evaluate using 5 metrics (MAE, MSE, RMSE, MAPE, R²) | ✅ | BT §2 Task 3, tr.1 | 5 metrics đầy đủ + bar chart |
| ML-04 | Compare under different social structures | ✅ | BT §2 Task 4, tr.2 | 4 structures × 3 models, grouped bar chart |
| ML-05 | Analyze peer influence propagation | ✅ | BT §2 Task 5, tr.2 | Hop 0/1/2 analysis + propagation chart |

---

## Tổng kết

### Thống kê

| Mức đánh giá | Số lượng |
|:---:|:---:|
| ✅ Đạt | 24 |
| ⚠️ Đạt một phần | 9 |
| ❌ Thiếu | 4 |
| ❓ Chưa xác nhận | 1 |

### Tỷ lệ hoàn thành ước tính: ~80%

### Các hạng mục cần bổ sung (ưu tiên cao → thấp)

| # | ID liên quan | Hạng mục | Nguồn yêu cầu | Độ khó |
|---|---|----------|----------------|:------:|
| 1 | CL2-01, BT2-01 | **Class Diagram UML** (vẽ VP hoặc Mermaid/PlantUML) | TL §2.10.6-7 | Trung bình |
| 2 | CL2-04, BT2-03 | **Thêm MySQL** cho ít nhất 1 service (hoặc document lý do chọn PostgreSQL) | TL §2.10.7 | Dễ |
| 3 | CL2-02, BT2-02 | **Tài liệu mapping Class → DB** cho mỗi service | TL §2.10.6-7 | Dễ |
| 4 | BT4-04 | **Test E2E tự động** cho full flow mua hàng | TL §4.11 | Trung bình |
| 5 | ML-01→05 | **Module dự đoán điểm thi** (nếu bài BT là bắt buộc) | BT §2 | Cao |
| 6 | NFR-02 | HA config (replicas, liveness probes) | TL §2.1.2 | Dễ (K8s đã có sẵn) |
