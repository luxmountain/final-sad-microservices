# Technical Report: Bookstore Microservices System

**Prepared for:** Software Engineering Project / Microservice Architecture
**System Overview:** Scalable E-commerce Platform

---

## Executive Summary

The Bookstore Microservices System is an enterprise-grade e-commerce application developed using a modern, scalable microservices architecture. Instead of relying on a traditional monolithic design, the system has been decoupled into twelve independent, highly cohesive, and loosely coupled services, alongside a dedicated API Gateway. This Technical Report provides a comprehensive overview of the architectural decisions, service-level responsibilities, database strategies, security protocols, and deployment environments that constitute the system. 

The architecture leverages Django and Django REST Framework (DRF) as the underlying technology stack for individual services, ensuring rapid development, robust ORM capabilities, and straightforward API generation. The system operates primarily within a Dockerized environment, orchestrated by Docker Compose, to ensure seamless parity between development and production setups.

---

## 1. Introduction & Objectives

### 1.1 Project Purpose
The purpose of the Bookstore Microservices project is to simulate a real-world, high-traffic e-commerce platform capable of handling diverse operational loads. By splitting the application into microservices, the system achieves targeted scalability, fault isolation, and independent deployment cycles.

### 1.2 Core Objectives
- **Scalability**: Allow individual components (such as the `order-service` or `recommender-ai-service`) to scale horizontally without impacting the performance of other domains (like the `staff-service`).
- **Resilience**: Ensure that the failure of a single non-critical service (e.g., `comment-rate-service`) does not take down the entire purchasing pipeline.
- **Maintainability**: Enforce strict domain boundaries, preventing "spaghetti code" and allowing specialized teams to manage distinct services.
- **Technology Agnosticism (Potential)**: While the current iteration relies heavily on Python/Django, the HTTP/REST boundary allows future services to be written in Rust, Go, or Node.js as needed.

---

## 2. High-Level System Architecture

The overarching architecture follows a pattern where a primary Gateway routes all external traffic to internal microservices.

### 2.1 The Monorepo Approach
The application is structured as a Monorepo, containing all independent service directories at the root level. This approach simplifies dependency management, shared testing strategies, and global Docker orchestration via a single `docker-compose.yml` file.

### 2.2 The API Gateway Pattern
In a microservices ecosystem, exposing all internal services directly to the public internet creates a massive attack surface and complicates front-end integration. To resolve this, the system implements an **API Gateway** (`api-gateway` running on port 8000). 
- **Reverse Proxying**: All API calls from the client (e.g., `/api/order-service/orders/`) are intercepted by the Gateway and securely proxied to internal network addresses (e.g., `http://order-service:8000/api/orders/`).
- **Frontend Delivery**: The Gateway also acts as a monolithic frontend server, rendering essential HTML templates and managing global session state. This hybrid approach (Server-Side Rendering + REST APIs) provides immediate SEO benefits while allowing dynamic interactions.

---

## 3. Microservices Domain Breakdown

The system is decomposed into 12 distinct domains, each bounded by specific business logic.

### 3.1 Book Service (`book-service`)
**Role:** Manages the core product catalog representing physical or digital books.
**Responsibilities:** 
- Tracking titles, authors, ISBNs, base pricing, and stock levels.
- Responding to search and filter queries from the API Gateway.
- Ensuring inventory decrement operations during order fulfillment.

### 3.2 Cart Service (`cart-service`)
**Role:** Manages ephemeral state related to user shopping sessions.
**Responsibilities:**
- Maintaining a list of `CartItems` mapped to a specific `Cart` identifying a user session.
- Calculating sub-totals and applying temporary promotional rules before checkout.
- Managing cart lifecycle (creation, item updates, clearing upon successful checkout).

### 3.3 Catalog Service (`catalog-service`)
**Role:** Manages high-level categorization, genres, and ontological mapping of books.
**Responsibilities:**
- Maintaining hierarchical category trees (e.g., Fiction -> Sci-Fi -> Cyberpunk).
- Allowing rapid retrieval of books based on broad category tags rather than specific title searches.

### 3.4 Order Service (`order-service`)
**Role:** The transactional heart of the e-commerce platform.
**Responsibilities:**
- Transforming a `Cart` into an immutable `Order` record.
- Tracking order lifecycle statuses (Pending -> Paid -> Shipped -> Delivered).
- Integrating deeply with the `Pay-Service` and `Ship-Service` to orchestrate fulfillment.

### 3.5 Customer Service (`customer-service`)
**Role:** Manages User/Client profiles.
**Responsibilities:**
- Storing customer addresses, preferences, and aggregate lifetime value metrics.
- Separating public identity from system-level User authentication records (which may reside at the gateway or auth layer).

### 3.6 Pay Service (`pay-service`)
**Role:** Interfacing with financial gateways.
**Responsibilities:**
- Managing Payment Methods (Credit Card, PayPal, On-Delivery).
- Processing payment logic and generating transaction receipts.
- Interacting with the `Order-Service` to confirm successful fund capture.

### 3.7 Ship Service (`ship-service`)
**Role:** Logistics and delivery management.
**Responsibilities:**
- Managing different shipping tiers (Standard, Express, International).
- Generating tracking updates and dispatch manifests for completed orders.

### 3.8 Comment & Rate Service (`comment-rate-service`)
**Role:** User-generated content management.
**Responsibilities:**
- Storing written reviews and numerical 1-5 star ratings for specific books.
- Calculating aggregated review scores asynchronously to avoid slowing down `book-service` queries.

### 3.9 Recommender AI Service (`recommender-ai-service`)
**Role:** Machine learning and analytics.
**Responsibilities:**
- Analyzing user purchase history and viewing habits to generate personalized "Books you might like" lists.
- Serving pre-computed machine learning inferences via the `/ai-suggest/` endpoints.

### 3.10 Staff & Manager Services (`staff-service`, `manager-service`)
**Role:** Internal administration and business intelligence.
**Responsibilities:**
- **Staff Service:** Allows bookstore employees to update inventory, process offline returns, and manage daily store operations.
- **Manager Service:** Aggregates data from `pay-service`, `order-service`, and `book-service` to generate financial reports, sales charts, and high-level BI dashboards.

---

## 4. Data Layer and Persistence Strategy

### 4.1 Centralized PostgreSQL Database
While a strictly pure microservices architecture advocates for "database-per-service" to ensure absolute isolation, this project implements a **Centralized Database Pattern** (`default_db` via PostgreSQL 15). 
- **Rationale**: For an academic or mid-tier enterprise project, orchestrating 12 separate database instances incurs massive memory overhead and introduces complex distributed transaction problems (e.g., Two-Phase Commit or Saga Patterns).
- **Logical Isolation**: Despite residing in a single physical instance, the data layout is logically partitioned. Django's ORM ensures that each service only interacts with its own declared tables via migrations. Cross-service joins at the SQL level are strictly prohibited in the code; services must communicate via API to retrieve related data.

### 4.2 Data Integrity
By using PostgreSQL, the system benefits from advanced concurrency controls, robust ACID compliance, and sophisticated JSONB indexing, which is occasionally utilized by the AI and telemetry services for unstructured data storage.

---

## 5. Network Communication and Routing

The system relies strictly on synchronous HTTP/REST communication for real-time reads.

### 5.1 Universal API Proxying Protocol
To minimize the maintenance overhead of writing mapping logic for every new endpoint, the `api-gateway` employs a "Universal Proxy" view.
A path such as: `http://localhost:8000/api/order-service/orders/123/`
Is dynamically intercepted by the Gateway. The Gateway extracts the `service_name` (`order-service`) and the remaining `path` (`/orders/123/`). Using Python's `requests` library, the Gateway acts as a reverse proxy, forwarding the client's payload (Headers, GET params, POST body) directly to the internal Docker network alias `http://order-service:8000/orders/123/`.

### 5.2 Internal Service Service Discovery
Because the services are deployed via Docker Compose, Docker's internal DNS handles service discovery. `order-service` will resolve to the internal IP of the respective container, regardless of host machine IP changes.

---

## 6. Authentication and Security

### 6.1 Authentication Flow
Authentication is managed centrally to prevent users from having to authenticate 12 different times.
- Users POST to `/login/` on the Gateway.
- The Gateway verifies credentials (often against a local shared User table or dedicated Identity service).
- Sessions or JWT (JSON Web Tokens) are established. The Gateway attaches validation headers to all downstream proxy requests, allowing internal microservices to trust the identity of the incoming request without hitting the database repeatedly.

### 6.2 Service-to-Service Security
Currently, services within the Docker network (`172.x.x.x`) trust traffic implicitly if it originates from the Gateway. Direct external access to nodes (e.g., hitting `book-service` on port 8002 directly) is intended for local debugging only. In a production environment, only port 8000 (Gateway) is exposed to the host firewall.

---

## 7. Containerization and Infrastructure

### 7.1 Docker Compose Configuration
The `docker-compose.yml` serves as the Infrastructure-as-Code (IaC) definition for the platform.
- **Base Images**: All Python services are containerized using lightweight Python Alpine or Slim images, significantly reducing the surface area for vulnerabilities.
- **Volume Mounting**: During development, local directories (`./book-service:/app`) are mapped to the containers. This enables "hot-reloading," allowing developers to edit `views.py` on their host machine and instantly see changes inside the container without rebuilding the Docker image.
- **Database Initialization**: A volume map `./postgres-init:/docker-entrypoint-initdb.d` is utilized to pre-seed the database schema and root users automatically when the cluster starts for the very first time.

### 7.2 Port Mapping Strategy
To avoid conflicts, port bindings increment sequentially:
- Gateway: 8000
- Customer: 8001
- Book: 8002
- Cart: 8003
- Staff: 8004
- Manager: 8005
- Catalog: 8006
- Order: 8007
- Ship: 8008
- Pay: 8009
- Comment/Rate: 8010
- Recommender-AI: 8011

---

## 8. Automated API Documentation (Swagger/OpenAPI)

Documentation is critical for a decoupled system. The project integrates `drf-spectacular` to automatically generate OpenAPI 3.0 schemas.
- **Dynamic Schema**: The generation occurs directly from DRF serializers and viewsets, meaning the documentation is strictly tied to the code and cannot fall out of date.
- **UI Interfaces**: Both Swagger UI (`/api/docs/`) and ReDoc (`/api/redoc/`) are served by the Gateway, providing interactive sandboxes where developers and QA testers can safely mock API requests against the live system.

---

## 9. Future Work & Scalability Prospects

While robust, the current architecture has several avenues for future optimization:
1. **Asynchronous Message Brokers (RabbitMQ/Kafka)**: Moving from synchronous HTTP REST calls between services (e.g., Order -> Pay) to asynchronous event-driven queues (e.g., `OrderCreated` event) would massively improve resilience. If the Pay service is down, the message stays in the queue until the service recovers.
2. **Caching Layers (Redis/Memcached)**: The `catalog-service` and `book-service` are heavily read-optimized. Placing a Redis cache in front of these services would reduce PostgreSQL load by 90% during peak traffic.
3. **Database-Per-Service Migration**: As data scales, migrating from `default_db` to isolated physical data stores (or migrating specific high-transaction services like `order-service` to a NoSQL store like MongoDB) would increase throughput.

---

## 10. Conclusion

The Bookstore Microservices platform effectively demonstrates the power and flexibility of modernized backend engineering. By decoupling the monolithic constraints of traditional Django apps into 12 tightly focused domains, the system offers unparalleled maintainability and scalability. The presence of the API Gateway seamlessly unifies the fragmented backend for the client applications, while Docker ensures that the complex orchestration of 13 separate containers occurs flawlessly across varying operating systems. The implementation forms a robust foundation for a production-ready, globally scalable enterprise application.
