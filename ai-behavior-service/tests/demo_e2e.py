"""
================================================================
  DEMO END-TO-END: Từ session data → behavior → chat
================================================================
Chạy:
  cd ai-behavior-service
  python tests/demo_e2e.py

Hoặc nếu đang chạy Docker:
  curl -X POST http://localhost:8020/analyze-behavior -H "X-API-Key: bookstore-ai-secret-key-2024" ...
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def demo():
    print("=" * 60)
    print("  DEMO END-TO-END: Session → Behavior → Chat")
    print("=" * 60)

    # ---- BƯỚC 1: Train model (Module 1) ----
    print("\n📦 BƯỚC 1: Training behavior model...")
    from module1_behavior.data_pipeline import create_dataloaders
    from module1_behavior.model_behavior import (
        BehaviorModel, train_model, save_model, predict_behavior, evaluate_model
    )

    train_loader, test_loader, scaler = create_dataloaders(num_users_per_class=100)
    model = BehaviorModel()
    model = train_model(model, train_loader, test_loader, epochs=30)
    save_model(model, scaler)

    acc, f1, auc, report = evaluate_model(model, test_loader)
    print(f"\n📊 Accuracy={acc:.4f} | F1={f1:.4f} | AUC={auc:.4f}")

    # ---- BƯỚC 2: Phân tích hành vi user ----
    print("\n🔍 BƯỚC 2: Phân tích hành vi user mẫu...")
    # Giả lập 1 user có hành vi impulse buyer
    sessions = [
        {"click_count": 28, "view_count": 7, "purchase_count": 5,
         "time_on_page": 1.5, "cart_add_count": 8, "search_count": 2,
         "session_duration": 10, "avg_price_viewed": 300,
         "category_diversity": 0.5, "return_rate": 0.2}
    ] * 10

    profile = predict_behavior(model, sessions, scaler)
    print(f"  Nhóm: {profile['label']} ({profile['confidence']:.2%})")
    for g, p in profile['probabilities'].items():
        print(f"    {g:20s}: {p:.4f}")

    # ---- BƯỚC 3: Build KB (Module 2) ----
    print("\n📚 BƯỚC 3: Building Knowledge Base...")
    from module2_knowledge.kb_builder import KnowledgeBaseBuilder
    kb = KnowledgeBaseBuilder()
    kb.build_index()
    kb.save_index()

    # Test search
    results = kb.hybrid_search("sách lập trình", top_k=2)
    print(f"  Search 'sách lập trình': found {len(results)} results")

    # ---- BƯỚC 4: Chat với RAG (Module 3) ----
    print("\n💬 BƯỚC 4: Chat với AI tư vấn viên...")
    from module3_rag.chatbot import Chatbot
    chatbot = Chatbot()
    chatbot.set_behavior_profile("demo_user", profile)

    questions = [
        "Có sách nào hay về công nghệ không?",
        "Giá bao nhiêu? Có khuyến mãi gì không?",
    ]

    for q in questions:
        print(f"\n  👤 Khách: {q}")
        result = chatbot.chat("demo_user", q)
        answer = result['answer'][:300]
        print(f"  🤖 Bot: {answer}...")
        print(f"  📎 Sources: {result['sources']}")

    print("\n" + "=" * 60)
    print("  ✅ DEMO HOÀN TẤT!")
    print("=" * 60)
    print("\nĐể chạy API server:")
    print("  uvicorn module4_api.main:app --host 0.0.0.0 --port 8020 --reload")


if __name__ == "__main__":
    demo()
