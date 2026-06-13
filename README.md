# Bookstore Microservices Project

Welcome to the Bookstore Microservices application! This project demonstrates a scalable e-commerce platform built using a microservices architecture. It contains multiple independent services communicating with each other.

## 🏗 System Architecture

This project is built using a Monorepo structured microservices architecture. The system contains the following services:

| Service Name | Description |
|---|---|
| `api-gateway` | The main entry point for clients, routing requests to the appropriate microservices |
| `auth-service` | Authentication (JWT register/login) |
| `user-service` | Customer, staff, and admin profiles (DDD monolith) |
| `product-service` | Books, clothes, and 8 other product types |
| `cart-service` | Handles user shopping carts and active sessions |
| `catalog-service` | Stores and retrieves book catalog and category details |
| `comment-rate-service` | Handles user ratings and comments on books |
| `order-service` | Handles order creation and lifecycle |
| `pay-service` | Manages payment processing |
| `recommender-ai-service` | Review-based book recommendation (collaborative filtering) |
| `ai-behavior-service` | LSTM behavior analysis, Neo4j graph, GNN, RAG chatbot |
| `ship-service` | Manages shipping and delivery updates |

## 🚀 How to Run the Project (Using Docker)

The easiest way to run the entire cluster of microservices is by using `docker-compose`.

### Prerequisites:
- Git
- Docker and Docker Compose installed on your machine.

### Steps to Run:
1. **Clone the repository:**
   ```bash
   git clone <your-github-repo-url>
   cd bookstore-microservice
   ```

2. **Start the services:**
   Run the following command in the root directory:
   ```bash
   docker-compose up --build -d
   ```
   *The `-d` flag runs the containers in the background.*

3. **Access the Application:**
   - Main website (via Nginx): `http://localhost`
   - API docs (Swagger): `http://localhost/api/docs/`
   - Neo4j Browser: `http://localhost:7474`
   - To stop the system, run:
     ```bash
     docker-compose down
     ```

## 🛠 Running Services Manually (Local Environment)

If you'd rather run the services individually without Docker, you will need Python installed. Do the following for **each service directory** in separate terminal windows:

1. Navigate to the service folder (e.g., `cd book-service`).
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install the dependencies for that specific service:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the development server (make sure you use a unique port per service):
   ```bash
   python manage.py runserver 8000
   ```

## 📚 Documentation

| Tài liệu | Nội dung |
|---|---|
| [Hướng dẫn sử dụng](./docs/HUONG_DAN_SU_DUNG.md) | Cài đặt, router, luồng nghiệp vụ, ví dụ API |
| [API Documentation](./docs/API_Documentation.md) | Chi tiết endpoint REST từng service |
| [Luồng hoạt động AI](./docs/AI_LUONG_HOAT_DONG.md) | LSTM, Neo4j graph, GNN, RAG chatbot |
| [Technical Report](./docs/Technical_Report.md) | Báo cáo kỹ thuật |

## 📦 Deliverables
- [x] GitHub Repository setup
- [x] API documentation
- [ ] Architecture diagram for each service
- [ ] 10-minute demo video
- [ ] 8-12 page technical report

---
*Developed for Software Engineering Project / Microservice Architecture.*
