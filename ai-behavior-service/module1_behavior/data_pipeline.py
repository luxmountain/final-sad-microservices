"""
================================================================
  MODULE 1 — Data Pipeline: Tiền xử lý & sinh dữ liệu hành vi
================================================================
Sinh dữ liệu tổng hợp (synthetic) cho 5 nhóm khách hàng:
  0: impulse_buyer    — Mua sắm bốc đồng
  1: researcher       — Nghiên cứu kỹ trước khi mua
  2: loyal_customer   — Khách hàng trung thành
  3: price_sensitive  — Nhạy cảm về giá
  4: window_shopper   — Chỉ xem, ít mua

Chạy standalone:
  cd ai-behavior-service
  python -m module1_behavior.data_pipeline
"""

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
import json
import os

# =============================================
# ĐỊNH NGHĨA NHÃN NHÓM HÀNH VI
# =============================================
BEHAVIOR_LABELS = {
    0: "impulse_buyer",
    1: "researcher",
    2: "loyal_customer",
    3: "price_sensitive",
    4: "window_shopper",
}

LABEL_DESCRIPTIONS = {
    "impulse_buyer": "Khách mua nhanh, ít cân nhắc, bị thu hút bởi khuyến mãi",
    "researcher": "Xem nhiều, so sánh kỹ, đọc review trước khi quyết định",
    "loyal_customer": "Quay lại thường xuyên, mua đều đặn, ít đổi trả",
    "price_sensitive": "Tìm giá tốt nhất, hay dùng mã giảm giá, so sánh giá",
    "window_shopper": "Xem nhiều nhưng mua rất ít, chỉ lướt qua",
}

# Cấu hình kích thước dữ liệu
NUM_FEATURES = 10      # Số features mỗi session
NUM_SESSIONS = 10      # Số session mỗi user (cho LSTM)

FEATURE_NAMES = [
    "click_count",        # Số lần click
    "view_count",         # Số lần xem sản phẩm
    "purchase_count",     # Số lần mua
    "time_on_page",       # Thời gian trên trang (phút)
    "cart_add_count",     # Số lần thêm vào giỏ
    "search_count",       # Số lần tìm kiếm
    "session_duration",   # Thời lượng phiên (phút)
    "avg_price_viewed",   # Giá trung bình sản phẩm đã xem (nghìn VNĐ)
    "category_diversity", # Đa dạng thể loại (0-1)
    "return_rate",        # Tỷ lệ đổi trả (0-1)
]


class BehaviorDataGenerator:
    """
    Sinh dữ liệu hành vi tổng hợp cho 5 nhóm khách hàng.
    Mỗi user gồm nhiều sessions, mỗi session có 10 features.
    """

    def __init__(self, num_users_per_class=200, num_sessions=NUM_SESSIONS, seed=42):
        self.num_users_per_class = num_users_per_class
        self.num_sessions = num_sessions
        np.random.seed(seed)

    def _gen_impulse_buyer(self, n):
        """Mua bốc đồng: click nhiều, mua nhanh, ít suy nghĩ, cart_add cao."""
        data = np.zeros((n, self.num_sessions, NUM_FEATURES))
        for i in range(n):
            for s in range(self.num_sessions):
                data[i, s] = [
                    np.random.randint(15, 40),       # click_count: cao
                    np.random.randint(5, 15),        # view_count: trung bình
                    np.random.randint(3, 8),         # purchase_count: cao
                    np.random.uniform(0.5, 3.0),     # time_on_page: thấp
                    np.random.randint(5, 12),        # cart_add_count: cao
                    np.random.randint(1, 5),         # search_count: thấp
                    np.random.uniform(5, 15),        # session_duration: ngắn
                    np.random.uniform(100, 500),     # avg_price: đa dạng
                    np.random.uniform(0.3, 0.8),     # category_diversity: TB
                    np.random.uniform(0.1, 0.35),    # return_rate: cao
                ]
        return data

    def _gen_researcher(self, n):
        """Nghiên cứu kỹ: xem rất nhiều, search nhiều, mua ít."""
        data = np.zeros((n, self.num_sessions, NUM_FEATURES))
        for i in range(n):
            for s in range(self.num_sessions):
                data[i, s] = [
                    np.random.randint(20, 50),       # click_count: rất cao
                    np.random.randint(15, 40),       # view_count: rất cao
                    np.random.randint(1, 3),         # purchase_count: thấp
                    np.random.uniform(5, 15),        # time_on_page: rất cao
                    np.random.randint(2, 6),         # cart_add_count: TB
                    np.random.randint(8, 20),        # search_count: rất cao
                    np.random.uniform(20, 60),       # session_duration: dài
                    np.random.uniform(100, 800),     # avg_price: đa dạng
                    np.random.uniform(0.5, 0.95),    # category_diversity: cao
                    np.random.uniform(0.02, 0.1),    # return_rate: rất thấp
                ]
        return data

    def _gen_loyal_customer(self, n):
        """Khách trung thành: mua đều đặn, ổn định, return thấp."""
        data = np.zeros((n, self.num_sessions, NUM_FEATURES))
        for i in range(n):
            base_click = np.random.randint(10, 20)
            base_purchase = np.random.randint(2, 5)
            for s in range(self.num_sessions):
                data[i, s] = [
                    base_click + np.random.randint(-3, 4),
                    np.random.randint(8, 20),
                    base_purchase + np.random.randint(-1, 2),
                    np.random.uniform(3, 8),
                    np.random.randint(2, 6),
                    np.random.randint(3, 8),
                    np.random.uniform(10, 30),
                    np.random.uniform(150, 400),
                    np.random.uniform(0.2, 0.5),     # diversity thấp (trung thành)
                    np.random.uniform(0.01, 0.05),   # return rất thấp
                ]
        return data

    def _gen_price_sensitive(self, n):
        """Nhạy cảm giá: search nhiều, avg_price thấp, cart_add rồi bỏ."""
        data = np.zeros((n, self.num_sessions, NUM_FEATURES))
        for i in range(n):
            for s in range(self.num_sessions):
                data[i, s] = [
                    np.random.randint(15, 35),
                    np.random.randint(10, 30),
                    np.random.randint(1, 4),
                    np.random.uniform(3, 10),
                    np.random.randint(5, 15),        # cart_add rất cao (thêm rồi bỏ)
                    np.random.randint(10, 25),       # search rất cao
                    np.random.uniform(15, 40),
                    np.random.uniform(50, 200),      # avg_price THẤP
                    np.random.uniform(0.6, 0.95),    # diversity cao (so sánh)
                    np.random.uniform(0.05, 0.2),
                ]
        return data

    def _gen_window_shopper(self, n):
        """Chỉ xem: view nhiều, click & mua rất ít."""
        data = np.zeros((n, self.num_sessions, NUM_FEATURES))
        for i in range(n):
            for s in range(self.num_sessions):
                data[i, s] = [
                    np.random.randint(3, 10),        # click: thấp
                    np.random.randint(10, 30),       # view: cao (scroll)
                    np.random.randint(0, 1),         # purchase: gần 0
                    np.random.uniform(1, 4),
                    np.random.randint(0, 2),         # cart_add: gần 0
                    np.random.randint(1, 5),
                    np.random.uniform(3, 12),
                    np.random.uniform(100, 600),
                    np.random.uniform(0.4, 0.9),
                    np.random.uniform(0.0, 0.05),
                ]
        return data

    def generate(self):
        """
        Sinh toàn bộ dataset.
        Returns: X shape (n_total, num_sessions, num_features), y shape (n_total,)
        """
        generators = [
            self._gen_impulse_buyer,
            self._gen_researcher,
            self._gen_loyal_customer,
            self._gen_price_sensitive,
            self._gen_window_shopper,
        ]

        X_list, y_list = [], []
        for label, gen_fn in enumerate(generators):
            X_class = gen_fn(self.num_users_per_class)
            y_class = np.full(self.num_users_per_class, label)
            X_list.append(X_class)
            y_list.append(y_class)

        X = np.concatenate(X_list, axis=0)
        y = np.concatenate(y_list, axis=0)

        # Trộn dữ liệu
        idx = np.random.permutation(len(X))
        return X[idx], y[idx]


class BehaviorDataset(Dataset):
    """PyTorch Dataset — chuẩn hóa features bằng StandardScaler."""

    def __init__(self, X, y, scaler=None, fit_scaler=True):
        n, s, f = X.shape
        X_flat = X.reshape(-1, f)

        if fit_scaler:
            self.scaler = StandardScaler()
            X_flat = self.scaler.fit_transform(X_flat)
        else:
            self.scaler = scaler
            X_flat = self.scaler.transform(X_flat)

        X_scaled = X_flat.reshape(n, s, f)
        self.X = torch.FloatTensor(X_scaled)
        self.y = torch.LongTensor(y)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


def create_dataloaders(num_users_per_class=200, batch_size=32, test_ratio=0.2, seed=42):
    """Tạo DataLoader cho training và testing."""
    generator = BehaviorDataGenerator(num_users_per_class=num_users_per_class, seed=seed)
    X, y = generator.generate()

    n = len(X)
    n_test = int(n * test_ratio)
    X_train, X_test = X[:n-n_test], X[n-n_test:]
    y_train, y_test = y[:n-n_test], y[n-n_test:]

    train_ds = BehaviorDataset(X_train, y_train, fit_scaler=True)
    test_ds = BehaviorDataset(X_test, y_test, scaler=train_ds.scaler, fit_scaler=False)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)

    print(f"✅ Dataset: Train={len(train_ds)} | Test={len(test_ds)}")
    print(f"   Shape: ({NUM_SESSIONS} sessions, {NUM_FEATURES} features)")
    for k, v in BEHAVIOR_LABELS.items():
        print(f"   {k}: {v} — train={(y_train==k).sum()}, test={(y_test==k).sum()}")

    return train_loader, test_loader, train_ds.scaler


def preprocess_single_user(session_data, scaler):
    """
    Tiền xử lý dữ liệu 1 user để dự đoán realtime.
    Args: session_data — list of dict hoặc np.ndarray
    Returns: torch.Tensor shape (1, NUM_SESSIONS, NUM_FEATURES)
    """
    if isinstance(session_data, list):
        X = np.array([[
            s.get("click_count", 0), s.get("view_count", 0),
            s.get("purchase_count", 0), s.get("time_on_page", 0),
            s.get("cart_add_count", 0), s.get("search_count", 0),
            s.get("session_duration", 0), s.get("avg_price_viewed", 0),
            s.get("category_diversity", 0), s.get("return_rate", 0),
        ] for s in session_data])
    else:
        X = np.array(session_data)

    # Padding nếu chưa đủ sessions
    if len(X) < NUM_SESSIONS:
        pad = np.zeros((NUM_SESSIONS - len(X), NUM_FEATURES))
        X = np.concatenate([pad, X], axis=0)
    elif len(X) > NUM_SESSIONS:
        X = X[-NUM_SESSIONS:]

    X_scaled = scaler.transform(X)
    return torch.FloatTensor(X_scaled).unsqueeze(0)


# =============================================
# CHẠY STANDALONE ĐỂ TEST
# =============================================
if __name__ == "__main__":
    print("=" * 60)
    print("  MODULE 1 — Data Pipeline Test")
    print("=" * 60)

    train_loader, test_loader, scaler = create_dataloaders()

    X_batch, y_batch = next(iter(train_loader))
    print(f"\n📦 Batch: X={X_batch.shape}, y={y_batch.shape}")
    print(f"   Labels: {y_batch[:8].tolist()}")

    # Test preprocess 1 user
    sample = [{"click_count": 25, "view_count": 8, "purchase_count": 5,
               "time_on_page": 1.5, "cart_add_count": 7, "search_count": 2,
               "session_duration": 8, "avg_price_viewed": 250,
               "category_diversity": 0.4, "return_rate": 0.15}] * 3
    X_single = preprocess_single_user(sample, scaler)
    print(f"   Single user shape: {X_single.shape}")
    print("   ✅ Pipeline OK!")
