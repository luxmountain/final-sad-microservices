"""
================================================================
  MODULE 3 — Chatbot: Quản lý hội thoại + session
================================================================
Quản lý conversation memory qua Redis, tích hợp behavior
embedding từ Module 1 vào RAG context.

Chạy standalone:
  cd ai-behavior-service
  python -m module3_rag.chatbot
"""

import json
import uuid
import os
from typing import Dict, List, Optional
from datetime import datetime

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


# =============================================
# CONVERSATION MEMORY (Redis hoặc In-Memory)
# =============================================
class ConversationMemory:
    """Lưu trữ lịch sử hội thoại — Redis hoặc fallback dict."""

    def __init__(self, max_turns=10):
        self.max_turns = max_turns  # Giữ N lượt hội thoại gần nhất
        self.redis_client = None

        if REDIS_AVAILABLE:
            try:
                host = os.getenv("REDIS_HOST", "localhost")
                port = int(os.getenv("REDIS_PORT", "6379"))
                self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)
                self.redis_client.ping()
                print(f"✅ Redis connected: {host}:{port}")
            except Exception as e:
                print(f"⚠️ Redis unavailable ({e}), dùng in-memory")
                self.redis_client = None

        if not self.redis_client:
            self._memory = {}  # Fallback in-memory

    def _key(self, user_id: str) -> str:
        return f"chat:history:{user_id}"

    def get_history(self, user_id: str) -> List[Dict]:
        """Lấy lịch sử hội thoại của user."""
        if self.redis_client:
            data = self.redis_client.get(self._key(user_id))
            if data:
                return json.loads(data)
            return []
        else:
            return self._memory.get(user_id, [])

    def add_message(self, user_id: str, role: str, content: str):
        """Thêm tin nhắn vào lịch sử, giữ max N lượt."""
        history = self.get_history(user_id)
        history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        # Giữ max_turns * 2 messages (mỗi lượt = 1 user + 1 assistant)
        max_messages = self.max_turns * 2
        if len(history) > max_messages:
            history = history[-max_messages:]

        if self.redis_client:
            self.redis_client.set(
                self._key(user_id),
                json.dumps(history, ensure_ascii=False),
                ex=3600  # TTL 1 giờ
            )
        else:
            self._memory[user_id] = history

    def clear_history(self, user_id: str):
        """Xóa lịch sử hội thoại."""
        if self.redis_client:
            self.redis_client.delete(self._key(user_id))
        else:
            self._memory.pop(user_id, None)


# =============================================
# BEHAVIOR PROFILE CACHE
# =============================================
class BehaviorProfileCache:
    """Cache behavior profile của user — Redis hoặc in-memory."""

    def __init__(self):
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                host = os.getenv("REDIS_HOST", "localhost")
                port = int(os.getenv("REDIS_PORT", "6379"))
                self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)
                self.redis_client.ping()
            except Exception:
                self.redis_client = None
        if not self.redis_client:
            self._cache = {}

    def _key(self, user_id: str) -> str:
        return f"behavior:profile:{user_id}"

    def get(self, user_id: str) -> Optional[Dict]:
        if self.redis_client:
            data = self.redis_client.get(self._key(user_id))
            return json.loads(data) if data else None
        return self._cache.get(user_id)

    def set(self, user_id: str, profile: Dict):
        if self.redis_client:
            self.redis_client.set(
                self._key(user_id),
                json.dumps(profile, ensure_ascii=False),
                ex=7200  # TTL 2 giờ
            )
        else:
            self._cache[user_id] = profile


# =============================================
# CHATBOT
# =============================================
class Chatbot:
    """
    Chatbot tư vấn cá nhân hóa.
    Kết hợp: Behavior Profile (Module 1) + RAG (Module 3).
    """

    def __init__(self, rag_pipeline=None):
        self.memory = ConversationMemory(max_turns=10)
        self.profile_cache = BehaviorProfileCache()

        if rag_pipeline is None:
            from module3_rag.rag_pipeline import RAGPipeline
            self.rag = RAGPipeline()
        else:
            self.rag = rag_pipeline

    def chat(self, user_id: str, message: str) -> Dict:
        """
        Xử lý 1 tin nhắn từ user.
        Returns: {answer, sources, behavior_label, message_id}
        """
        message_id = str(uuid.uuid4())[:8]

        # 1. Lấy behavior profile (nếu có)
        profile = self.profile_cache.get(user_id)

        # 2. Lấy conversation history
        history = self.memory.get_history(user_id)

        # 3. Chạy RAG pipeline
        result = self.rag.query(
            user_message=message,
            behavior_profile=profile,
            conversation_history=history,
        )

        # 4. Lưu vào memory
        self.memory.add_message(user_id, "user", message)
        self.memory.add_message(user_id, "assistant", result["answer"])

        return {
            "message_id": message_id,
            "answer": result["answer"],
            "sources": result["sources"],
            "behavior_label": result.get("behavior_label"),
            "user_id": user_id,
        }

    def set_behavior_profile(self, user_id: str, profile: Dict):
        """Cập nhật behavior profile cho user."""
        self.profile_cache.set(user_id, profile)

    def clear_session(self, user_id: str):
        """Xóa session chat."""
        self.memory.clear_history(user_id)


# =============================================
# DEMO 3 CONVERSATION FLOWS
# =============================================
def demo_conversations():
    """Demo 3 cuộc hội thoại cho 3 nhóm khách hàng khác nhau."""

    print("=" * 60)
    print("  MODULE 3 — Demo Chatbot Conversations")
    print("=" * 60)

    chatbot = Chatbot()

    # --- Flow 1: Impulse Buyer ---
    print("\n" + "=" * 60)
    print("  🛒 FLOW 1: Khách hàng mua bốc đồng (impulse_buyer)")
    print("=" * 60)
    user1 = "user_impulse_001"
    chatbot.set_behavior_profile(user1, {
        "label": "impulse_buyer", "confidence": 0.92
    })

    messages1 = [
        "Có gì hot không shop?",
        "Áo Gucci bao nhiêu tiền?",
        "Có khuyến mãi gì không?",
    ]
    for msg in messages1:
        print(f"\n  👤 Khách: {msg}")
        result = chatbot.chat(user1, msg)
        print(f"  🤖 Bot: {result['answer'][:200]}...")

    # --- Flow 2: Researcher ---
    print("\n" + "=" * 60)
    print("  🔍 FLOW 2: Khách hàng nghiên cứu kỹ (researcher)")
    print("=" * 60)
    user2 = "user_researcher_002"
    chatbot.set_behavior_profile(user2, {
        "label": "researcher", "confidence": 0.88
    })

    messages2 = [
        "So sánh Clean Code với Pragmatic Programmer giúp tôi",
        "Chính sách đổi trả sách như nào?",
        "Sách nào về AI được đánh giá cao nhất?",
    ]
    for msg in messages2:
        print(f"\n  👤 Khách: {msg}")
        result = chatbot.chat(user2, msg)
        print(f"  🤖 Bot: {result['answer'][:200]}...")

    # --- Flow 3: Price Sensitive ---
    print("\n" + "=" * 60)
    print("  💰 FLOW 3: Khách nhạy cảm giá (price_sensitive)")
    print("=" * 60)
    user3 = "user_price_003"
    chatbot.set_behavior_profile(user3, {
        "label": "price_sensitive", "confidence": 0.85
    })

    messages3 = [
        "Sách nào rẻ nhất shop?",
        "Có mã giảm giá nào không?",
        "Mua combo được giảm bao nhiêu?",
    ]
    for msg in messages3:
        print(f"\n  👤 Khách: {msg}")
        result = chatbot.chat(user3, msg)
        print(f"  🤖 Bot: {result['answer'][:200]}...")

    print("\n✅ Demo hoàn tất!")


if __name__ == "__main__":
    demo_conversations()
