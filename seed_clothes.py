import requests
import time

URL = "http://localhost:8013/clothes/"

clothes_data = [
    {
        "name": "Gucci Vintage Logo T-Shirt",
        "brand": "Gucci",
        "size": "M",
        "color": "White",
        "price": 550.00,
        "stock": 15,
        "category_id": 1,
        "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=600&q=80"
    },
    {
        "name": "Christian Dior Oblique Jacket",
        "brand": "Dior",
        "size": "L",
        "color": "Navy Blue",
        "price": 2800.00,
        "stock": 5,
        "category_id": 2,
        "image_url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=600&q=80"
    },
    {
        "name": "Louis Vuitton Monogram Denim Jacket",
        "brand": "Louis Vuitton",
        "size": "L",
        "color": "Blue",
        "price": 3100.00,
        "stock": 3,
        "category_id": 2,
        "image_url": "https://images.unsplash.com/photo-1578587018452-892bace94f12?w=600&q=80"
    },
    {
        "name": "Chanel Classic Tweed Coat",
        "brand": "Chanel",
        "size": "S",
        "color": "Black/White",
        "price": 6500.00,
        "stock": 2,
        "category_id": 3,
        "image_url": "https://images.unsplash.com/photo-1544441893-675973e31985?w=600&q=80"
    },
    {
        "name": "Balenciaga Oversized Hoodie",
        "brand": "Balenciaga",
        "size": "XL",
        "color": "Black",
        "price": 950.00,
        "stock": 20,
        "category_id": 4,
        "image_url": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=600&q=80"
    },
    {
        "name": "Prada Re-Nylon Shirt",
        "brand": "Prada",
        "size": "M",
        "color": "Black",
        "price": 1200.00,
        "stock": 10,
        "category_id": 1,
        "image_url": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=600&q=80"
    },
    {
        "name": "Versace Silk Barocco Shirt",
        "brand": "Versace",
        "size": "M",
        "color": "Gold/Black",
        "price": 1450.00,
        "stock": 8,
        "category_id": 1,
        "image_url": "https://images.unsplash.com/photo-1603252109303-2751441dd157?w=600&q=80"
    },
    {
        "name": "Hermes Cashmere Sweater",
        "brand": "Hermes",
        "size": "L",
        "color": "Camel",
        "price": 2200.00,
        "stock": 6,
        "category_id": 4,
        "image_url": "https://images.unsplash.com/photo-1614031679227-865ce379b1df?w=600&q=80"
    },
    {
        "name": "Burberry Classic Trench Coat",
        "brand": "Burberry",
        "size": "M",
        "color": "Beige",
        "price": 2400.00,
        "stock": 12,
        "category_id": 3,
        "image_url": "https://images.unsplash.com/photo-1520975954732-57dd22299614?w=600&q=80"
    },
    {
        "name": "YSL Leather Biker Jacket",
        "brand": "Yves Saint Laurent",
        "size": "S",
        "color": "Black",
        "price": 4900.00,
        "stock": 2,
        "category_id": 2,
        "image_url": "https://images.unsplash.com/photo-1559551409-dadc959f76b8?w=600&q=80"
    }
]

print("Bắt đầu khởi tạo dữ liệu Clothes vào hệ thống...")
success = 0
for item in clothes_data:
    try:
        response = requests.post(URL, json=item)
        if response.status_code in [200, 201]:
            print(f"✅ Đã thêm: {item['name']} - {item['brand']}")
            success += 1
        else:
            print(f"❌ Lỗi khi thêm {item['name']}:", response.text)
    except Exception as e:
        print(f"⚠️ Lỗi kết nối khi thêm {item['name']}: {e}")
    time.sleep(0.5)

print(f"\n🎉 Hoàn tất! Đã thêm thành công {success}/{len(clothes_data)} dữ liệu quần áo hàng hiệu.")
