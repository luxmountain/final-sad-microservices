"""
================================================================
  MODULE 3 — RAG Pipeline: Retriever + Reranker + Generator
================================================================
Pipeline: Query → Hybrid Retrieve → Cross-Encoder Rerank
          → Augment (behavior profile) → Gemini Generate

Chạy standalone:
  cd ai-behavior-service
  python -m module3_rag.rag_pipeline
"""

import os
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# =============================================
# RERANKER (Cross-Encoder)
# =============================================
class CrossEncoderReranker:
    """Rerank kết quả retrieval bằng cross-encoder."""

    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        from sentence_transformers import CrossEncoder
        print(f"🔄 Loading reranker: {model_name}")
        self.model = CrossEncoder(model_name)
        print("✅ Reranker loaded!")

    def rerank(self, query: str, documents, top_k=5):
        """
        Rerank documents theo relevance score.
        Args:
            query: câu hỏi
            documents: list of (Document, score) từ retriever
            top_k: số kết quả trả về
        Returns: list of (Document, rerank_score)
        """
        if not documents:
            return []

        pairs = [(query, doc.content) for doc, _ in documents]
        scores = self.model.predict(pairs)

        # Ghép score mới với document
        scored = list(zip([d for d, _ in documents], scores))
        scored.sort(key=lambda x: x[1], reverse=True)

        return scored[:top_k]


# =============================================
# LLM GENERATOR (Google Gemini)
# =============================================
class GeminiGenerator:
    """Sinh câu trả lời bằng Google Gemini API."""

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY", "")
        self.model_name = os.getenv("LLM_MODEL", "gemini-2.5-flash")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1024"))

        if api_key and api_key != "your_gemini_api_key_here":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.available = True
            print(f"✅ Gemini ready: {self.model_name}")
        else:
            self.model = None
            self.available = False
            print("⚠️  Gemini API key chưa cấu hình → dùng mock response")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Gọi Gemini API hoặc trả mock response."""
        if not self.available:
            return self._mock_response(prompt)

        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                }
            )
            return response.text
        except Exception as e:
            print(f"⚠️ Gemini error: {e}")
            return self._mock_response(prompt)

    def _mock_response(self, prompt: str) -> str:
        """Mock response khi chưa có API key."""
        return (
            "🤖 [Mock Response - Cần cấu hình GOOGLE_API_KEY]\n\n"
            "Xin chào! Tôi là trợ lý tư vấn AI của BookStore. "
            "Hiện tại tôi đang chạy ở chế độ demo. "
            "Để có câu trả lời thực, vui lòng thêm Gemini API key vào file .env.\n\n"
            f"Câu hỏi của bạn: {prompt[:200]}..."
        )


# =============================================
# RAG PIPELINE
# =============================================
class RAGPipeline:
    """
    Pipeline RAG hoàn chỉnh:
    1. Hybrid Retrieve (FAISS + BM25)
    2. Cross-Encoder Rerank
    3. Augment với behavior profile
    4. Generate bằng Gemini
    """

    def __init__(self, kb_builder=None):
        # Retriever (KB)
        if kb_builder is None:
            from module2_knowledge.kb_builder import KnowledgeBaseBuilder, INDEX_DIR
            self.kb = KnowledgeBaseBuilder()
            index_path = INDEX_DIR
            if os.path.exists(os.path.join(index_path, "faiss_index")):
                self.kb.load_index(index_path)
            else:
                print("⚠️ Chưa có index, đang build...")
                self.kb.build_index()
                self.kb.save_index(index_path)
        else:
            self.kb = kb_builder

        # Reranker
        self.reranker = CrossEncoderReranker()

        # Generator
        self.generator = GeminiGenerator()

    def _build_system_prompt(self, behavior_profile: Optional[Dict] = None) -> str:
        """Tạo system prompt với behavior profile."""
        base = (
            "Bạn là trợ lý tư vấn AI của BookStore & Fashion — cửa hàng bán sách và thời trang hàng hiệu.\n"
            "Quy tắc:\n"
            "1. Trả lời bằng tiếng Việt, thân thiện và chuyên nghiệp\n"
            "2. CHỈ trả lời dựa trên thông tin được cung cấp trong Context bên dưới\n"
            "3. Nếu không tìm thấy thông tin, nói rõ: 'Tôi không có thông tin về vấn đề này'\n"
            "4. KHÔNG BỊA thông tin sản phẩm, giá cả hoặc chính sách\n"
            "5. Gợi ý sản phẩm phù hợp với nhóm hành vi khách hàng\n"
            "6. Giá tiền luôn hiển thị bằng VNĐ\n"
        )

        if behavior_profile:
            label = behavior_profile.get("label", "unknown")
            confidence = behavior_profile.get("confidence", 0)

            # Load chiến lược tư vấn theo nhóm
            scenario_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "module2_knowledge", "knowledge_base", "scenarios", f"{label}.json"
            )
            strategy = ""
            if os.path.exists(scenario_path):
                with open(scenario_path, 'r', encoding='utf-8') as f:
                    scenario = json.load(f)
                    s = scenario.get("consultation_strategy", {})
                    strategy = (
                        f"\nChiến lược tư vấn cho nhóm này:\n"
                        f"- Tone: {s.get('tone', '')}\n"
                        f"- Approach: {s.get('approach', '')}\n"
                        f"- Tránh: {s.get('avoid', '')}\n"
                    )

            base += (
                f"\n--- THÔNG TIN KHÁCH HÀNG ---\n"
                f"Nhóm hành vi: {label} (độ tin cậy: {confidence:.0%})\n"
                f"{strategy}"
            )

        return base

    def _build_context(self, retrieved_docs) -> str:
        """Ghép nội dung documents thành context string."""
        context_parts = []
        for i, (doc, score) in enumerate(retrieved_docs):
            source = doc.metadata.get("source", "unknown")
            context_parts.append(f"[Nguồn {i+1}: {source}]\n{doc.content}")
        return "\n\n---\n\n".join(context_parts)

    def query(self, user_message: str, behavior_profile: Optional[Dict] = None,
              conversation_history: List[Dict] = None, top_k_retrieve=20,
              top_k_rerank=5) -> Dict:
        """
        Chạy RAG pipeline hoàn chỉnh.

        Args:
            user_message: câu hỏi của user
            behavior_profile: dict từ Module 1 (label, confidence, embedding...)
            conversation_history: list of {role, content}
            top_k_retrieve: số docs retrieve ban đầu
            top_k_rerank: số docs sau rerank

        Returns:
            dict: {answer, sources, behavior_label}
        """
        # 1. Retrieve
        retrieved = self.kb.hybrid_search(user_message, top_k=top_k_retrieve)

        # 2. Rerank
        reranked = self.reranker.rerank(user_message, retrieved, top_k=top_k_rerank)

        # 3. Build context
        context = self._build_context(reranked)

        # 4. Build prompt
        system_prompt = self._build_system_prompt(behavior_profile)

        # Conversation history
        history_text = ""
        if conversation_history:
            last_5 = conversation_history[-10:]  # 5 lượt = 10 messages
            for msg in last_5:
                role = "Khách" if msg["role"] == "user" else "Tư vấn viên"
                history_text += f"{role}: {msg['content']}\n"

        user_prompt = (
            f"--- CONTEXT TỪ CƠ SỞ TRI THỨC ---\n{context}\n\n"
        )
        if history_text:
            user_prompt += f"--- LỊCH SỬ HỘI THOẠI ---\n{history_text}\n\n"
        user_prompt += f"--- CÂU HỎI HIỆN TẠI ---\nKhách: {user_message}\n\nTư vấn viên:"

        # 5. Generate
        answer = self.generator.generate(user_prompt, system_prompt)

        # 6. Return
        sources = [doc.metadata.get("source", "?") for doc, _ in reranked]
        return {
            "answer": answer,
            "sources": list(set(sources)),
            "behavior_label": behavior_profile.get("label") if behavior_profile else None,
            "num_retrieved": len(retrieved),
            "num_reranked": len(reranked),
        }


# =============================================
# CHẠY STANDALONE
# =============================================
if __name__ == "__main__":
    print("=" * 60)
    print("  MODULE 3 — RAG Pipeline Test")
    print("=" * 60)

    pipeline = RAGPipeline()

    # Test 1: Không có behavior profile
    print("\n📝 Test 1: Query chung")
    result = pipeline.query("Có sách nào về lập trình Python không?")
    print(f"  Answer: {result['answer'][:300]}...")
    print(f"  Sources: {result['sources']}")

    # Test 2: Với behavior profile (impulse buyer)
    print("\n📝 Test 2: Với behavior profile (impulse_buyer)")
    profile = {"label": "impulse_buyer", "confidence": 0.85}
    result = pipeline.query("Gợi ý sách hay đi!", behavior_profile=profile)
    print(f"  Answer: {result['answer'][:300]}...")

    # Test 3: Thời trang
    print("\n📝 Test 3: Hỏi về thời trang")
    result = pipeline.query("Áo Gucci có bao nhiêu tiền?")
    print(f"  Answer: {result['answer'][:300]}...")

    print("\n✅ RAG Pipeline OK!")
