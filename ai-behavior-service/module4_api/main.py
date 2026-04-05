"""
================================================================
  MODULE 4 — FastAPI REST API
================================================================
Endpoints:
  POST /analyze-behavior  — Phân tích hành vi → behavior profile
  POST /chat              — Chatbot RAG tư vấn
  GET  /user/{user_id}/profile — Lấy behavior profile
  POST /feedback          — Thu thập feedback
  GET  /health            — Health check

Chạy standalone:
  cd ai-behavior-service
  uvicorn module4_api.main:app --host 0.0.0.0 --port 8020 --reload
"""

import os
import sys
import json
import time
from typing import Optional, List, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# =============================================
# PYDANTIC MODELS (Request/Response)
# =============================================
class SessionData(BaseModel):
    click_count: int = 0
    view_count: int = 0
    purchase_count: int = 0
    time_on_page: float = 0.0
    cart_add_count: int = 0
    search_count: int = 0
    session_duration: float = 0.0
    avg_price_viewed: float = 0.0
    category_diversity: float = 0.0
    return_rate: float = 0.0

class AnalyzeBehaviorRequest(BaseModel):
    user_id: str
    sessions: List[SessionData]

class ChatRequest(BaseModel):
    user_id: str
    message: str

class FeedbackRequest(BaseModel):
    user_id: str
    message_id: Optional[str] = None
    rating: int  # 1-5
    comment: Optional[str] = None


# =============================================
# GLOBAL COMPONENTS (lazy load)
# =============================================
_components = {}

def get_behavior_model():
    """Lazy load behavior model (Module 1)."""
    if "model" not in _components:
        try:
            from module1_behavior.model_behavior import load_model, BehaviorModel
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
            if os.path.exists(os.path.join(model_path, "behavior_model.pth")):
                model, scaler = load_model(model_path)
                _components["model"] = model
                _components["scaler"] = scaler
                print("✅ Behavior model loaded!")
            else:
                # Train model nếu chưa có
                print("🔄 Model chưa có, đang train...")
                from module1_behavior.model_behavior import (
                    BehaviorModel, train_model, save_model
                )
                from module1_behavior.data_pipeline import create_dataloaders
                train_loader, test_loader, scaler = create_dataloaders()
                model = BehaviorModel()
                model = train_model(model, train_loader, test_loader, epochs=30)
                save_model(model, scaler, model_path)
                _components["model"] = model
                _components["scaler"] = scaler
        except Exception as e:
            print(f"⚠️ Không load được model: {e}")
            _components["model"] = None
            _components["scaler"] = None

    return _components.get("model"), _components.get("scaler")

def get_chatbot():
    """Lazy load chatbot (Module 3)."""
    if "chatbot" not in _components:
        try:
            from module3_rag.chatbot import Chatbot
            _components["chatbot"] = Chatbot()
            print("✅ Chatbot loaded!")
        except Exception as e:
            print(f"⚠️ Không load được chatbot: {e}")
            _components["chatbot"] = None
    return _components.get("chatbot")


# =============================================
# AUTH & RATE LIMITING
# =============================================
from module4_api.auth import verify_api_key
from module4_api.rate_limiter import setup_rate_limiter


# =============================================
# FASTAPI APP
# =============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: preload models."""
    print("🚀 AI Behavior Service starting...")
    yield
    print("👋 AI Behavior Service shutting down...")

app = FastAPI(
    title="AI Behavior Analysis Service",
    description="Phân tích hành vi khách hàng và tư vấn cá nhân hóa bằng AI",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
setup_rate_limiter(app)


# =============================================
# ENDPOINTS
# =============================================

@app.get("/health")
async def health_check():
    """Kiểm tra trạng thái service."""
    return {
        "status": "healthy",
        "service": "ai-behavior-service",
        "timestamp": time.time(),
    }


@app.post("/analyze-behavior")
async def analyze_behavior(req: AnalyzeBehaviorRequest, api_key: str = Depends(verify_api_key)):
    """
    Phân tích hành vi khách hàng từ session data.
    Trả về: behavior profile (label, confidence, embedding, probabilities).
    """
    model, scaler = get_behavior_model()
    if model is None:
        raise HTTPException(500, "Model chưa sẵn sàng. Vui lòng thử lại sau.")

    try:
        from module1_behavior.model_behavior import predict_behavior
        session_dicts = [s.model_dump() for s in req.sessions]
        result = predict_behavior(model, session_dicts, scaler)

        # Cache profile vào chatbot
        chatbot = get_chatbot()
        if chatbot:
            chatbot.set_behavior_profile(req.user_id, result)

        return {
            "user_id": req.user_id,
            "behavior_profile": result,
        }
    except Exception as e:
        raise HTTPException(500, f"Lỗi phân tích: {str(e)}")


@app.post("/chat")
async def chat(req: ChatRequest, api_key: str = Depends(verify_api_key)):
    """
    Chat với AI tư vấn viên.
    Response được cá nhân hóa dựa trên behavior profile (nếu có).
    """
    chatbot = get_chatbot()
    if chatbot is None:
        raise HTTPException(500, "Chatbot chưa sẵn sàng. Vui lòng thử lại sau.")

    try:
        result = chatbot.chat(req.user_id, req.message)
        return result
    except Exception as e:
        raise HTTPException(500, f"Lỗi chat: {str(e)}")


@app.get("/user/{user_id}/profile")
async def get_user_profile(user_id: str, api_key: str = Depends(verify_api_key)):
    """Lấy behavior profile đã lưu của user."""
    chatbot = get_chatbot()
    if chatbot is None:
        raise HTTPException(500, "Service chưa sẵn sàng.")

    profile = chatbot.profile_cache.get(user_id)
    if profile is None:
        raise HTTPException(404, f"Không tìm thấy profile cho user {user_id}")

    return {"user_id": user_id, "behavior_profile": profile}


@app.post("/feedback")
async def submit_feedback(req: FeedbackRequest, api_key: str = Depends(verify_api_key)):
    """Thu thập feedback từ khách hàng để cải thiện model."""
    if req.rating < 1 or req.rating > 5:
        raise HTTPException(400, "Rating phải từ 1 đến 5")

    # Lưu feedback (in-memory cho demo, production dùng DB)
    feedback = {
        "user_id": req.user_id,
        "message_id": req.message_id,
        "rating": req.rating,
        "comment": req.comment,
        "timestamp": time.time(),
    }

    # Log feedback
    print(f"📝 Feedback: user={req.user_id}, rating={req.rating}, comment={req.comment}")

    return {"status": "success", "message": "Cảm ơn bạn đã góp ý!", "feedback": feedback}


@app.post("/clear-session/{user_id}")
async def clear_session(user_id: str, api_key: str = Depends(verify_api_key)):
    """Xóa session chat của user."""
    chatbot = get_chatbot()
    if chatbot:
        chatbot.clear_session(user_id)
    return {"status": "success", "message": f"Đã xóa session của {user_id}"}


# =============================================
# CHẠY TRỰC TIẾP
# =============================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("AI_SERVICE_PORT", "8020"))
    uvicorn.run("module4_api.main:app", host="0.0.0.0", port=port, reload=True)
