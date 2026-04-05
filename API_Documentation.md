# API Documentation

This document outlines the exposed REST API endpoints for the Bookstore Microservices project. The API requests are intended to be routed through the `api-gateway` which forwards them to the respective service.

## Base URL
All API requests (other than direct gateway UI routes) are typically prefixed with the API gateway host and port.

**Example**: `http://localhost:8000/api/<service_name>/`

---

## 1. Gateway & Authentication Routes (`api-gateway`)

These endpoints are handled directly by the API Gateway to serve pages and manage global auth.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET | `/auth/` | Authentication view/page |
| POST | `/login/` | Process user login and retrieve tokens |
| GET | `/book/<int:book_id>/` | Gateway view for book details |
| GET | `/cart/` | Cart page view |
| GET | `/checkout/` | Checkout page view |
| GET | `/orders/` | User orders dashboard |
| GET | `/staff/` | Staff dashboard view |
| GET | `/manager/` | Manager dashboard view |
| GET | `/api/docs/` | Swagger UI documentation |
| GET | `/api/redoc/` | ReDoc API documentation |

---

## 2. Book Service (`book-service`)

Manages the core book inventory, prices, authorship, and availability.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/book-service/books/` | Retrieve a list of all active books |
| POST | `/api/book-service/books/` | Create a new book record |
| GET | `/api/book-service/books/<id>/` | Retrieve specific book details by ID |
| PUT | `/api/book-service/books/<id>/` | Update an existing book's entirety |
| PATCH| `/api/book-service/books/<id>/` | Partially update an existing book |
| DELETE| `/api/book-service/books/<id>/` | Remove a book from inventory |

---

## 3. Cart Service (`cart-service`)

Manages user shopping carts and active session items.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/cart-service/carts/` | Create a new unified cart |
| GET | `/api/cart-service/carts/<customer_id>/` | Retrieve the active cart for a customer |
| POST | `/api/cart-service/cart-items/` | Add a new item to the cart |
| PUT | `/api/cart-service/cart-items/<item_id>/` | Update a cart item (e.g., quantity) |
| DELETE| `/api/cart-service/cart-items/<item_id>/` | Remove an item from the cart |

---

## 4. Order Service (`order-service`)

Handles order processing, fulfillment lifecycle, and checkout history.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/order-service/orders/` | List all orders (filtered by user context) |
| POST | `/api/order-service/orders/` | Create a new order (checkout) |
| PUT/PATCH | `/api/order-service/orders/<id>/status/` | Update the delivery/payment status of an order |

---

## 5. Pay Service (`pay-service`)

Handles transactions, external payment intents, and methods.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/pay-service/payment-methods/` | List all available payment methods |
| POST | `/api/pay-service/payments/` | Process a new payment transaction |

---

## 6. Catalog Service (`catalog-service`)

Manages product categorization and tags.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/catalog-service/categories/` | List all book categories / genres |
| POST | `/api/catalog-service/categories/` | Create a new category |

---

## 7. Customer Service (`customer-service`)

Manages user and profile details.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/customer-service/customers/` | List customer profiles |
| POST | `/api/customer-service/customers/` | Register/Create a new customer profile |

---

## 8. Ship Service (`ship-service`)

Manages shipping integration, delivery tracking, and providers.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ship-service/shipping-methods/` | List supported shipping providers/methods |
| POST | `/api/ship-service/shippings/` | Create a new shipping manifest or update state |

---

## 9. Comment & Rate Service (`comment-rate-service`)

Manages user-generated reviews, numerical ratings, and feedback on books.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/comment-rate-service/reviews/` | Fetch reviews (filterable by book ID) |
| POST | `/api/comment-rate-service/reviews/` | Submit a new review/rating |

---

## 10. Recommender AI Service (`recommender-ai-service`)

Provides AI-driven suggestions.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST/GET | `/api/recommender-ai-service/ai-suggest/` | Request AI-based book recommendations |

---

## 11. Staff Service (`staff-service`)

Manages internal staff roles and privileged actions on books.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/staff-service/staffs/` | Register / Onboard new staff |
| POST/PUT | `/api/staff-service/staff-books/` | Advanced inventory and management queries for books |

---

## 12. Manager Service (`manager-service`)

Manages high-level aggregation and corporate reporting.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/manager-service/reports/` | Generate and fetch sales, inventory, and activity reports |

