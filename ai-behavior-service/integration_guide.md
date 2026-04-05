# Hướng Dẫn Tích Hợp AI Behavior Service

## 1. Kiến Trúc Tổng Thể

```
┌──────────────────────────────┐
│     Frontend (Website)       │
│  ┌────────────────────────┐  │
│  │  Chat Widget (iframe)  │  │
│  └──────────┬─────────────┘  │
└─────────────┼────────────────┘
              │ HTTP
              ▼
┌──────────────────────────────┐
│   API Gateway (:8000)        │
│   Proxy → AI Service (:8020) │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│  AI Behavior Service (:8020) │
│  ┌─────┐ ┌────┐ ┌─────────┐ │
│  │Model│ │ KB │ │RAG Chat │ │
│  └─────┘ └────┘ └─────────┘ │
└──────────────────────────────┘
```

## 2. API Endpoints

### 2.1 Phân tích hành vi
```bash
POST http://localhost:8020/analyze-behavior
Header: X-API-Key: bookstore-ai-secret-key-2024
Body:
{
  "user_id": "customer_001",
  "sessions": [
    {
      "click_count": 25, "view_count": 10, "purchase_count": 3,
      "time_on_page": 5.0, "cart_add_count": 4, "search_count": 6,
      "session_duration": 20, "avg_price_viewed": 150,
      "category_diversity": 0.5, "return_rate": 0.05
    }
  ]
}
```

### 2.2 Chat tư vấn
```bash
POST http://localhost:8020/chat
Header: X-API-Key: bookstore-ai-secret-key-2024
Body:
{
  "user_id": "customer_001",
  "message": "Gợi ý sách hay về lập trình đi!"
}
```

### 2.3 Lấy profile
```bash
GET http://localhost:8020/user/customer_001/profile
Header: X-API-Key: bookstore-ai-secret-key-2024
```

### 2.4 Gửi feedback
```bash
POST http://localhost:8020/feedback
Header: X-API-Key: bookstore-ai-secret-key-2024
Body:
{
  "user_id": "customer_001",
  "message_id": "abc123",
  "rating": 5,
  "comment": "Tư vấn rất hữu ích!"
}
```

## 3. Tích Hợp Chat Widget

### Cách 1: JavaScript Snippet (Khuyên dùng)

Thêm đoạn code này vào cuối `<body>` trong trang web:

```html
<script>
(function() {
  const AI_API = 'http://localhost:8020';
  const API_KEY = 'bookstore-ai-secret-key-2024';

  // Tạo chat widget
  const widget = document.createElement('div');
  widget.id = 'ai-chat-widget';
  widget.innerHTML = `
    <div id="chat-toggle" style="position:fixed;bottom:20px;right:20px;width:60px;height:60px;
      background:linear-gradient(135deg,#667eea,#764ba2);border-radius:50%;cursor:pointer;
      display:flex;align-items:center;justify-content:center;box-shadow:0 4px 15px rgba(0,0,0,0.2);z-index:9999">
      <span style="color:white;font-size:28px">💬</span>
    </div>
    <div id="chat-box" style="display:none;position:fixed;bottom:90px;right:20px;width:380px;height:500px;
      background:white;border-radius:16px;box-shadow:0 8px 30px rgba(0,0,0,0.15);z-index:9999;
      display:flex;flex-direction:column;overflow:hidden">
      <div style="background:linear-gradient(135deg,#667eea,#764ba2);padding:16px;color:white">
        <h3 style="margin:0;font-size:16px">🤖 AI Tư Vấn BookStore</h3>
        <small>Tư vấn sách & thời trang cá nhân hóa</small>
      </div>
      <div id="chat-messages" style="flex:1;overflow-y:auto;padding:12px"></div>
      <div style="padding:12px;border-top:1px solid #eee;display:flex;gap:8px">
        <input id="chat-input" placeholder="Nhập câu hỏi..."
          style="flex:1;padding:10px;border:1px solid #ddd;border-radius:8px;outline:none">
        <button id="chat-send"
          style="padding:10px 16px;background:#667eea;color:white;border:none;border-radius:8px;cursor:pointer">
          Gửi
        </button>
      </div>
    </div>
  `;
  document.body.appendChild(widget);

  const toggle = document.getElementById('chat-toggle');
  const box = document.getElementById('chat-box');
  const input = document.getElementById('chat-input');
  const send = document.getElementById('chat-send');
  const messages = document.getElementById('chat-messages');

  let userId = localStorage.getItem('ai_user_id') || 'user_' + Date.now();
  localStorage.setItem('ai_user_id', userId);

  toggle.onclick = () => {
    box.style.display = box.style.display === 'none' ? 'flex' : 'none';
  };

  function addMessage(text, isUser) {
    const div = document.createElement('div');
    div.style.cssText = `margin:8px 0;padding:10px 14px;border-radius:12px;max-width:85%;
      ${isUser ? 'background:#667eea;color:white;margin-left:auto' : 'background:#f0f0f0;color:#333'}`;
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  async function sendMessage() {
    const msg = input.value.trim();
    if (!msg) return;
    addMessage(msg, true);
    input.value = '';

    try {
      const res = await fetch(AI_API + '/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-API-Key': API_KEY},
        body: JSON.stringify({user_id: userId, message: msg})
      });
      const data = await res.json();
      addMessage(data.answer || 'Xin lỗi, có lỗi xảy ra.', false);
    } catch(e) {
      addMessage('⚠️ Không kết nối được AI service.', false);
    }
  }

  send.onclick = sendMessage;
  input.onkeydown = (e) => { if (e.key === 'Enter') sendMessage(); };
})();
</script>
```

### Cách 2: iframe

```html
<!-- Nhúng trực tiếp vào trang -->
<iframe src="http://localhost:8020/chat-widget"
        width="400" height="550"
        style="position:fixed;bottom:20px;right:20px;border:none;border-radius:16px;
               box-shadow:0 8px 30px rgba(0,0,0,0.15);z-index:9999">
</iframe>
```

## 4. Flow tích hợp đầy đủ

```
1. User truy cập website
2. Frontend thu thập session data (click, view, thời gian...)
3. Gọi POST /analyze-behavior → nhận behavior profile
4. User mở chat → Gọi POST /chat với user_id
5. AI tự động cá nhân hóa dựa trên profile đã phân tích
6. User feedback → POST /feedback
```

## 5. Chạy hệ thống

```bash
# Từ thư mục root bookstore-microservice
docker compose up --build

# AI service sẽ chạy tại: http://localhost:8020
# Test health: curl http://localhost:8020/health
```
