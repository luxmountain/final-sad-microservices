import requests

CAT_URL = "http://localhost:8006/categories/"
CLOTHES_URL = "http://localhost:8013/clothes/"

# 1. Tạo Danh Mục mới cho quần áo
categories = [
    {"name": "Thời Trang Nam", "description": "Quần áo thời trang dành cho nam giới"},
    {"name": "Thời Trang Nữ", "description": "Quần áo thời trang dành cho nữ giới"},
    {"name": "Thời Trang Hàng Hiệu", "description": "Các món đồ hiệu xa xỉ từ Gucci, Dior..."}
]

cat_map = {}
for c in categories:
    res = requests.post(CAT_URL, json=c)
    if res.status_code in (200, 201):
        data = res.json()
        cat_map[c["name"]] = data.get("id")
    else:
        # Thử lấy danh sách xem có chưa
        all_cats = requests.get(CAT_URL).json()
        for ac in all_cats:
            if ac["name"] == c["name"]:
                cat_map[c["name"]] = ac["id"]

cat_id_luxury = cat_map.get("Thời Trang Hàng Hiệu")

if cat_id_luxury:
    # 2. Cập nhật toàn bộ quần áo sang Thời Trang Hàng Hiệu
    clothes = requests.get(CLOTHES_URL).json()
    count = 0
    for c in clothes:
        c_id = c["id"]
        c["category_id"] = cat_id_luxury
        # Gọi PUT để update
        update_url = f"{CLOTHES_URL}{c_id}/"
        # Bỏ id khi update để an toàn
        res = requests.put(update_url, json=c)
        if res.status_code == 200:
            count += 1
    print(f"Đã cập nhật {count} sản phẩm quần áo sang danh mục 'Thời Trang Hàng Hiệu' (ID: {cat_id_luxury})!")
else:
    print("Không tạo được danh mục Thời trang!")
