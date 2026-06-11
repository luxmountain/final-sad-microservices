"""
Thay 4 sách VN không có ảnh bằng 4 tác phẩm Nga kinh điển
với ảnh bìa thật từ Open Library (đã test hoạt động).

Chạy: python replace_vnbooks_with_russian.py
"""
import requests

BOOK_URL = "http://localhost:8002"

# ===== BƯỚC 1: XOÁ 4 SÁCH VIỆT NAM KHÔNG CÓ ẢNH =====
# Số Đỏ=6, Tắt Đèn=7, Dế Mèn=8, Chí Phèo=9
print("🗑️  Xoá 4 sách Việt Nam không ảnh...")
for book_id in [6, 7, 8, 9]:
    r = requests.delete(f"{BOOK_URL}/books/{book_id}/")
    status = "✅" if r.status_code in (200, 204) else f"❌ {r.status_code}"
    print(f"  {status} Xoá sách ID={book_id}")

# ===== BƯỚC 2: THÊM 4 TÁC PHẨM NGA KINH ĐIỂN =====
print("\n📚 Thêm 4 tác phẩm Nga kinh điển...")

# Lấy category_id của "Văn học nước ngoài"
cats_r = requests.get("http://localhost:8006/categories/")
cats = cats_r.json() if cats_r.status_code == 200 else []
vhnn_id = next((c["id"] for c in cats if "nước ngoài" in c.get("name", "").lower()), 6)
print(f"  → Dùng category 'Văn học nước ngoài' (ID={vhnn_id})")

russian_books = [
    {
        "title": "Chiến Tranh và Hòa Bình (War and Peace)",
        "author": "Leo Tolstoy",
        "price": 175000,
        "stock": 45,
        "category_id": vhnn_id,
        # Open Library - ISBN 9780199232764 (Oxford World's Classics)
        "image_url": "https://covers.openlibrary.org/b/isbn/9780199232765-L.jpg"
    },
    {
        "title": "Tội Ác và Hình Phạt (Crime and Punishment)",
        "author": "Fyodor Dostoevsky",
        "price": 125000,
        "stock": 60,
        "category_id": vhnn_id,
        # Open Library - ISBN Penguin Classics
        "image_url": "https://covers.openlibrary.org/b/isbn/9780143058144-L.jpg"
    },
    {
        "title": "Anh Em Nhà Karamazov (The Brothers Karamazov)",
        "author": "Fyodor Dostoevsky",
        "price": 155000,
        "stock": 38,
        "category_id": vhnn_id,
        # Open Library - Farrar Straus edition
        "image_url": "https://covers.openlibrary.org/b/isbn/9780374528379-L.jpg"
    },
    {
        "title": "Anna Karenina",
        "author": "Leo Tolstoy",
        "price": 145000,
        "stock": 52,
        "category_id": vhnn_id,
        # Open Library - Penguin Classics
        "image_url": "https://covers.openlibrary.org/b/isbn/9780143035008-L.jpg"
    },
]

for book in russian_books:
    r = requests.post(f"{BOOK_URL}/books/", json=book)
    if r.status_code in (200, 201):
        data = r.json()
        print(f"  ✅ {book['title']} (ID={data.get('id')})")
    else:
        print(f"  ❌ {book['title']} → {r.status_code}: {r.text[:80]}")

print("\n🎉 Xong! Reload localhost:8000 để xem sách Nga với ảnh bìa đẹp.")
