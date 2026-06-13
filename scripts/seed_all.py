"""
=============================================================
SEED DATA SCRIPT — Bookstore Microservices
=============================================================
Chạy:
  docker.exe compose exec postgres-db psql -U admin -d default_db -f /docker-entrypoint-initdb.d/init.sql
  python scripts/seed_all.py

Script này kết nối trực tiếp PostgreSQL và seed data cho TẤT CẢ services.
"""
import psycopg2
import os
import random
import json
import hashlib
from datetime import datetime, timedelta

# ─── CONFIG ───────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "admin",
    "password": "123",
}

# ─── VIETNAMESE DATA ──────────────────────────────────────
FIRST_NAMES = [
    "An", "Bình", "Chi", "Dung", "Hà", "Hải", "Hạnh", "Hiền", "Hoàng", "Hùng",
    "Hương", "Khánh", "Lan", "Linh", "Long", "Mai", "Minh", "Nam", "Ngọc", "Nhung",
    "Phong", "Phương", "Quân", "Sơn", "Thắng", "Thanh", "Thảo", "Thủy", "Trang", "Trung",
    "Tuấn", "Tùng", "Vy", "Xuân", "Yến", "Đức", "Hòa", "Khoa", "Lâm", "Nghĩa",
    "Phúc", "Quang", "Tâm", "Thịnh", "Toàn", "Trí", "Việt", "Vũ", "Anh", "Bảo",
]
LAST_NAMES = [
    "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng",
    "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Đinh", "Trịnh", "Lương", "Tạ",
]
MIDDLE_NAMES = ["Văn", "Thị", "Đức", "Minh", "Hoàng", "Ngọc", "Quốc", "Thanh", "Hữu", "Thúy"]

ADDRESSES = [
    "123 Nguyễn Trãi, Thanh Xuân, Hà Nội",
    "456 Lê Lợi, Quận 1, TP.HCM",
    "78 Trần Phú, Hải Châu, Đà Nẵng",
    "90 Nguyễn Huệ, Quận 1, TP.HCM",
    "12 Phạm Văn Đồng, Cầu Giấy, Hà Nội",
    "34 Lý Thường Kiệt, Hoàn Kiếm, Hà Nội",
    "56 Hai Bà Trưng, Quận 3, TP.HCM",
    "78 Điện Biên Phủ, Bình Thạnh, TP.HCM",
    "100 Lạc Long Quân, Tây Hồ, Hà Nội",
    "22 Nguyễn Văn Linh, Hải An, Hải Phòng",
    "45 Trần Hưng Đạo, Sơn Trà, Đà Nẵng",
    "67 Bạch Đằng, Hồng Bàng, Hải Phòng",
    "89 Lê Duẩn, Đống Đa, Hà Nội",
    "11 Võ Văn Tần, Quận 3, TP.HCM",
    "33 Hoàng Hoa Thám, Ba Đình, Hà Nội",
    "55 Pasteur, Quận 1, TP.HCM",
    "77 Nguyễn Thái Học, Ba Đình, Hà Nội",
    "99 Cách Mạng Tháng 8, Quận 10, TP.HCM",
    "21 Trần Quốc Toản, Hải Châu, Đà Nẵng",
    "43 Phan Đình Phùng, Hoàn Kiếm, Hà Nội",
]

REVIEW_COMMENTS = [
    "Sách hay lắm, đọc rất cuốn! Mình đã đọc một mạch không ngừng.",
    "Nội dung phong phú, đáng đọc. Giao hàng nhanh.",
    "Chất lượng in ấn tốt, giá cả hợp lý.",
    "Cuốn sách này thay đổi cách nhìn của mình về cuộc sống.",
    "Tuyệt vời! Mình sẽ mua thêm những cuốn khác của tác giả.",
    "Nội dung ok nhưng bìa sách hơi mỏng.",
    "Đóng gói cẩn thận, sách không bị nhăn gấp.",
    "Mình thích phong cách viết của tác giả, dễ hiểu và sâu sắc.",
    "Cuốn sách kinh điển, ai cũng nên đọc một lần.",
    "Giao hàng hơi chậm nhưng sách thì tuyệt vời.",
    "Mua làm quà tặng bạn bè, ai cũng thích.",
    "Đọc xong muốn đọc lại lần nữa. Quá hay!",
    "Giấy in đẹp, font chữ dễ đọc. Rất hài lòng.",
    "Sách dịch rất tốt, giữ được tinh thần nguyên bản.",
    "Mình recommend cuốn này cho những ai thích đọc sách.",
    "Nội dung sâu sắc, nhiều bài học cuộc sống.",
    "Đã mua bản tiếng Anh rồi, giờ mua thêm bản tiếng Việt.",
    "Trang bìa đẹp, thiết kế sang trọng. Tặng quà rất ý nghĩa.",
    "Sách hay nhưng giá hơi cao so với sách cùng loại.",
    "Một cuốn must-read! Không thể bỏ qua.",
    "Nội dung phù hợp cho mọi lứa tuổi.",
    "Mình đã giới thiệu cho cả nhóm đọc sách, mọi người đều thích.",
    "Cuốn sách giúp mình relax sau giờ làm việc căng thẳng.",
    "Bản dịch lưu loát, đọc rất mượt mà.",
    "Đóng gói sách rất cẩn thận, ship nhanh, sách đẹp.",
    "Nội dung bình thường, không như kỳ vọng.",
    "Sách mỏng hơn mình tưởng, nhưng nội dung vẫn OK.",
    "Tác giả viết rất chân thực và xúc động.",
    "Mua cho con đọc, bé rất thích.",
    "Giá rẻ hơn nhà sách, chất lượng tương đương.",
]

CATEGORIES = [
    ("Văn học nước ngoài", "Tiểu thuyết, truyện ngắn từ các tác giả quốc tế"),
    ("Văn học Việt Nam", "Tác phẩm văn học trong nước"),
    ("Khoa học - Công nghệ", "Sách về khoa học tự nhiên và công nghệ thông tin"),
    ("Kinh tế - Quản lý", "Sách về kinh doanh, tài chính, quản trị"),
    ("Tâm lý - Kỹ năng sống", "Sách phát triển bản thân, tâm lý học"),
    ("Thiếu nhi", "Sách dành cho trẻ em và thiếu niên"),
    ("Giáo khoa - Tham khảo", "Sách giáo khoa và tài liệu tham khảo"),
    ("Lịch sử - Địa lý", "Sách về lịch sử, văn hóa, địa lý"),
    ("Thời trang", "Quần áo, phụ kiện thời trang"),
    ("Truyện tranh - Manga", "Manga, comic, truyện tranh"),
]

PAYMENT_METHODS = [
    ("Thanh toán khi nhận hàng", "COD"),
    ("Thẻ tín dụng/ghi nợ", "CREDIT_CARD"),
    ("Ví MoMo", "MOMO"),
    ("Chuyển khoản ngân hàng", "BANK_TRANSFER"),
    ("VNPay", "VNPAY"),
]

SHIPPING_METHODS = [
    ("Giao hàng tiêu chuẩn", 25000, "Giao trong 3-5 ngày làm việc"),
    ("Giao hàng nhanh", 45000, "Giao trong 1-2 ngày làm việc"),
    ("Giao hỏa tốc", 65000, "Giao trong 2-4 giờ (nội thành)"),
    ("Miễn phí ship", 0, "Áp dụng cho đơn hàng trên 300.000đ"),
]


def get_conn(dbname):
    return psycopg2.connect(dbname=dbname, **DB_CONFIG)


def make_password(raw):
    """Django-compatible pbkdf2_sha256 hash."""
    import base64
    salt = "randomsalt123456"
    iterations = 260000
    dk = hashlib.pbkdf2_hmac('sha256', raw.encode(), salt.encode(), iterations)
    hash_b64 = base64.b64encode(dk).decode()
    return f"pbkdf2_sha256${iterations}${salt}${hash_b64}"


def seed_auth(num_users=100):
    """Seed users vào auth_db."""
    print(f"🔐 Seeding {num_users} users vào auth_db...")
    conn = get_conn("auth_db")
    cur = conn.cursor()

    # Clear existing
    cur.execute("DELETE FROM users_user")

    password_hash = make_password("Password123!")
    users = []

    # Admin + Staff
    users.append(("admin", "admin@bookstore.vn", password_hash, "admin", True, True, True))
    users.append(("staff1", "staff1@bookstore.vn", password_hash, "staff", True, False, True))
    users.append(("manager1", "manager1@bookstore.vn", password_hash, "manager", True, False, True))

    # Customers
    used_usernames = set(["admin", "staff1", "manager1"])
    for i in range(num_users - 3):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        username = f"{first.lower()}{random.randint(1, 999)}"
        while username in used_usernames:
            username = f"{first.lower()}{random.randint(1, 9999)}"
        used_usernames.add(username)
        email = f"{username}@gmail.com"
        users.append((username, email, password_hash, "customer", True, False, True))

    for u in users:
        cur.execute("""
            INSERT INTO users_user (username, email, password, role, is_active, is_superuser, is_staff,
                                    first_name, last_name, date_joined)
            VALUES (%s, %s, %s, %s, %s, %s, %s, '', '', NOW())
        """, u)

    conn.commit()
    cur.close()
    conn.close()
    print(f"   ✅ {len(users)} users created (admin/staff1/manager1 + {num_users-3} customers)")
    return len(users)


def seed_customers(num_users=100):
    """Seed customers vào user_db."""
    print(f"👥 Seeding customers vào user_db...")
    conn = get_conn("user_db")
    cur = conn.cursor()
    cur.execute("DELETE FROM customers")

    customers = []
    for i in range(1, num_users + 1):
        last = random.choice(LAST_NAMES)
        middle = random.choice(MIDDLE_NAMES)
        first = random.choice(FIRST_NAMES)
        name = f"{last} {middle} {first}"
        email = f"customer{i}@gmail.com"
        customers.append((name, email))

    for c in customers:
        cur.execute("INSERT INTO customers (name, email) VALUES (%s, %s)", c)

    conn.commit()
    cur.close()
    conn.close()
    print(f"   ✅ {len(customers)} customers created")


def seed_categories():
    """Seed categories vào catalog_db."""
    print("📂 Seeding categories vào catalog_db...")
    conn = get_conn("catalog_db")
    cur = conn.cursor()
    cur.execute("DELETE FROM app_category")

    for name, desc in CATEGORIES:
        cur.execute("INSERT INTO app_category (name, description) VALUES (%s, %s)", (name, desc))

    conn.commit()
    cur.close()
    conn.close()
    print(f"   ✅ {len(CATEGORIES)} categories created")


def seed_products():
    """Seed products vào product_db (books + clothes)."""
    print("📚 Seeding products vào product_db...")
    conn = get_conn("product_db")
    cur = conn.cursor()
    cur.execute("DELETE FROM products")

    import os
    seeds_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "product-service", "seeds")

    # Books
    with open(os.path.join(seeds_dir, "books_catalog.json"), "r", encoding="utf-8") as f:
        books = json.load(f)

    for b in books:
        attrs = json.dumps({"author": b.get("author", ""), "isbn": ""}, ensure_ascii=False)
        cur.execute("""
            INSERT INTO products (id, name, product_type, price, stock, category_id, image_url, attributes)
            VALUES (%s, %s, 'book', %s, %s, %s, %s, %s)
        """, (b["id"], b["title"], b["price"], b.get("stock", 50), 1,
              b.get("image_url", ""), attrs))

    # Clothes
    with open(os.path.join(seeds_dir, "clothes_catalog.json"), "r", encoding="utf-8") as f:
        clothes = json.load(f)

    for c in clothes:
        attrs = json.dumps({"brand": c.get("brand", ""), "size": c.get("size", "M"),
                           "color": c.get("color", "")}, ensure_ascii=False)
        cur.execute("""
            INSERT INTO products (id, name, product_type, price, stock, category_id, image_url, attributes)
            VALUES (%s, %s, 'cloth', %s, %s, %s, %s, %s)
        """, (c["id"] + 100, c["name"], c["price"], c.get("stock", 30), 9,
              c.get("image_url", ""), attrs))

    conn.commit()
    cur.close()
    conn.close()
    print(f"   ✅ {len(books)} books + {len(clothes)} clothes created")
    return len(books)


def seed_payment_methods():
    """Seed payment methods vào pay_db."""
    print("💳 Seeding payment methods...")
    conn = get_conn("pay_db")
    cur = conn.cursor()
    cur.execute("DELETE FROM app_payment")
    cur.execute("DELETE FROM app_paymentmethod")

    for i, (name, code) in enumerate(PAYMENT_METHODS, 1):
        cur.execute("INSERT INTO app_paymentmethod (id, name, code) VALUES (%s, %s, %s)", (i, name, code))

    # Reset sequence
    cur.execute("SELECT setval(pg_get_serial_sequence('app_paymentmethod', 'id'), %s)", (len(PAYMENT_METHODS),))

    conn.commit()
    cur.close()
    conn.close()
    print(f"   ✅ {len(PAYMENT_METHODS)} payment methods created")


def seed_shipping_methods():
    """Seed shipping methods vào ship_db."""
    print("🚚 Seeding shipping methods...")
    conn = get_conn("ship_db")
    cur = conn.cursor()
    cur.execute("DELETE FROM app_shipment")
    cur.execute("DELETE FROM app_shippingmethod")

    for i, (name, fee, desc) in enumerate(SHIPPING_METHODS, 1):
        cur.execute("INSERT INTO app_shippingmethod (id, name, fee, description) VALUES (%s, %s, %s, %s)",
                   (i, name, fee, desc))

    cur.execute("SELECT setval(pg_get_serial_sequence('app_shippingmethod', 'id'), %s)", (len(SHIPPING_METHODS),))

    conn.commit()
    cur.close()
    conn.close()
    print(f"   ✅ {len(SHIPPING_METHODS)} shipping methods created")


def seed_orders(num_orders=500, num_users=100, num_books=28):
    """Seed orders + order items vào order_db."""
    print(f"🛒 Seeding {num_orders} orders...")
    conn = get_conn("order_db")
    cur = conn.cursor()
    cur.execute("DELETE FROM app_orderitem")
    cur.execute("DELETE FROM app_order")

    statuses = ["PENDING", "CONFIRMED", "SHIPPING", "DELIVERED", "CANCELLED"]
    status_weights = [10, 15, 20, 50, 5]

    # Load book prices
    seeds_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "product-service", "seeds")
    with open(os.path.join(seeds_dir, "books_catalog.json"), "r", encoding="utf-8") as f:
        books = json.load(f)
    book_prices = {b["id"]: b["price"] for b in books}

    orders_data = []
    for i in range(num_orders):
        customer_id = random.randint(1, num_users)
        num_items = random.randint(1, 5)
        items = []
        total = 0

        for _ in range(num_items):
            book_id = random.randint(1, num_books)
            qty = random.randint(1, 3)
            price = book_prices.get(book_id, 100000)
            items.append((book_id, "book", qty, price))
            total += price * qty

        shipping_id = random.randint(1, len(SHIPPING_METHODS))
        payment_id = random.randint(1, len(PAYMENT_METHODS))
        address = random.choice(ADDRESSES)
        status = random.choices(statuses, weights=status_weights, k=1)[0]
        created_at = datetime.now() - timedelta(days=random.randint(1, 180),
                                                 hours=random.randint(0, 23))

        cur.execute("""
            INSERT INTO app_order (customer_id, total_price, shipping_method_id, payment_method_id,
                                   address, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (customer_id, total, shipping_id, payment_id, address, status, created_at))

        order_id = cur.fetchone()[0]

        for book_id, item_type, qty, price in items:
            cur.execute("""
                INSERT INTO app_orderitem (order_id, book_id, item_type, quantity, price)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, book_id, item_type, qty, price))

        orders_data.append((order_id, customer_id, total, payment_id, shipping_id, address, status))

    conn.commit()
    cur.close()
    conn.close()
    print(f"   ✅ {num_orders} orders created")
    return orders_data


def seed_payments(orders_data):
    """Seed payments vào pay_db dựa trên orders."""
    print(f"💰 Seeding {len(orders_data)} payments...")
    conn = get_conn("pay_db")
    cur = conn.cursor()
    cur.execute("DELETE FROM app_payment")

    for order_id, _, total, payment_method_id, _, _, status in orders_data:
        pay_status = "COMPLETED" if status in ("DELIVERED", "SHIPPING", "CONFIRMED") else "PENDING"
        if status == "CANCELLED":
            pay_status = "CANCELLED"

        cur.execute("""
            INSERT INTO app_payment (order_id, payment_method_id, amount, status)
            VALUES (%s, %s, %s, %s)
        """, (order_id, payment_method_id, total, pay_status))

    conn.commit()
    cur.close()
    conn.close()
    print(f"   ✅ {len(orders_data)} payments created")


def seed_shipments(orders_data):
    """Seed shipments vào ship_db dựa trên orders."""
    print(f"📦 Seeding {len(orders_data)} shipments...")
    conn = get_conn("ship_db")
    cur = conn.cursor()
    cur.execute("DELETE FROM app_shipment")

    for order_id, _, _, _, shipping_method_id, address, status in orders_data:
        ship_status = "DELIVERED" if status == "DELIVERED" else \
                      "SHIPPING" if status == "SHIPPING" else \
                      "CANCELLED" if status == "CANCELLED" else "PENDING"

        cur.execute("""
            INSERT INTO app_shipment (order_id, shipping_method_id, address, status)
            VALUES (%s, %s, %s, %s)
        """, (order_id, shipping_method_id, address, ship_status))

    conn.commit()
    cur.close()
    conn.close()
    print(f"   ✅ {len(orders_data)} shipments created")


def seed_reviews(num_reviews=800, num_users=100, num_books=28):
    """Seed reviews vào comment_rate_db."""
    print(f"⭐ Seeding {num_reviews} reviews...")
    conn = get_conn("comment_rate_db")
    cur = conn.cursor()
    cur.execute("DELETE FROM app_review")

    for _ in range(num_reviews):
        customer_id = random.randint(1, num_users)
        book_id = random.randint(1, num_books)
        rating = random.choices([1, 2, 3, 4, 5], weights=[3, 5, 12, 35, 45], k=1)[0]
        comment = random.choice(REVIEW_COMMENTS)
        created_at = datetime.now() - timedelta(days=random.randint(1, 365))

        cur.execute("""
            INSERT INTO app_review (customer_id, book_id, rating, comment, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (customer_id, book_id, rating, comment, created_at))

    conn.commit()
    cur.close()
    conn.close()
    print(f"   ✅ {num_reviews} reviews created")


def seed_carts(num_carts=50, num_users=100, num_books=28):
    """Seed active carts vào cart_db."""
    print(f"🛍️ Seeding {num_carts} active carts...")
    conn = get_conn("cart_db")
    cur = conn.cursor()
    cur.execute("DELETE FROM app_cartitem")
    cur.execute("DELETE FROM app_cart")

    for i in range(num_carts):
        customer_id = random.randint(1, num_users)
        cur.execute("INSERT INTO app_cart (customer_id) VALUES (%s) RETURNING id", (customer_id,))
        cart_id = cur.fetchone()[0]

        num_items = random.randint(1, 4)
        for _ in range(num_items):
            book_id = random.randint(1, num_books)
            qty = random.randint(1, 3)
            cur.execute("""
                INSERT INTO app_cartitem (cart_id, book_id, item_type, quantity)
                VALUES (%s, %s, 'book', %s)
            """, (cart_id, book_id, qty))

    conn.commit()
    cur.close()
    conn.close()
    print(f"   ✅ {num_carts} carts created")


def seed_ai_logs(num_logs=200, num_users=100, num_books=28):
    """Seed AI recommendation logs."""
    print(f"🤖 Seeding {num_logs} AI recommendation logs...")
    conn = get_conn("recommender_ai_db")
    cur = conn.cursor()
    cur.execute("DELETE FROM app_ai_log")

    reasons = [
        "Dựa trên lịch sử mua hàng",
        "Sách cùng thể loại bạn thích",
        "Bestseller tháng này",
        "Người dùng tương tự đã mua",
        "Collaborative filtering",
        "Content-based recommendation",
        "Dựa trên ratings cao nhất",
        "Sách mới cùng tác giả yêu thích",
    ]

    for _ in range(num_logs):
        customer_id = random.randint(1, num_users)
        book_id = random.randint(1, num_books)
        reason = random.choice(reasons)
        created_at = datetime.now() - timedelta(days=random.randint(1, 90))

        cur.execute("""
            INSERT INTO app_ai_log (customer_id, recommended_book_id, reason, created_at)
            VALUES (%s, %s, %s, %s)
        """, (customer_id, book_id, reason, created_at))

    conn.commit()
    cur.close()
    conn.close()
    print(f"   ✅ {num_logs} AI logs created")


def main():
    print("=" * 60)
    print("🚀 BOOKSTORE MICROSERVICES — SEED ALL DATA")
    print("=" * 60)
    print()

    NUM_USERS = 100
    NUM_ORDERS = 500
    NUM_REVIEWS = 800

    # 1. Auth users
    seed_auth(NUM_USERS)
    print()

    # 2. Customer profiles
    seed_customers(NUM_USERS)
    print()

    # 3. Categories
    seed_categories()
    print()

    # 4. Products (books + clothes)
    num_books = seed_products()
    print()

    # 5. Payment methods
    seed_payment_methods()
    print()

    # 6. Shipping methods
    seed_shipping_methods()
    print()

    # 7. Orders + order items
    orders_data = seed_orders(NUM_ORDERS, NUM_USERS, num_books)
    print()

    # 8. Payments
    seed_payments(orders_data)
    print()

    # 9. Shipments
    seed_shipments(orders_data)
    print()

    # 10. Reviews
    seed_reviews(NUM_REVIEWS, NUM_USERS, num_books)
    print()

    # 11. Active carts
    seed_carts(50, NUM_USERS, num_books)
    print()

    # 12. AI recommendation logs
    seed_ai_logs(200, NUM_USERS, num_books)
    print()

    print("=" * 60)
    print("✅ HOÀN TẤT! Tổng data đã seed:")
    print(f"   • {NUM_USERS} users (auth + customer profiles)")
    print(f"   • {len(CATEGORIES)} categories")
    print(f"   • 38 products (28 books + 10 clothes)")
    print(f"   • {len(PAYMENT_METHODS)} payment methods")
    print(f"   • {len(SHIPPING_METHODS)} shipping methods")
    print(f"   • {NUM_ORDERS} orders")
    print(f"   • {NUM_ORDERS} payments")
    print(f"   • {NUM_ORDERS} shipments")
    print(f"   • {NUM_REVIEWS} reviews")
    print(f"   • 50 active carts")
    print(f"   • 200 AI recommendation logs")
    print("=" * 60)


if __name__ == "__main__":
    main()
