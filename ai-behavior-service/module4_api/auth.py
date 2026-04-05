"""
MODULE 4 — API Key Authentication Middleware
"""

import os
from fastapi import HTTPException, Header
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY", "bookstore-ai-secret-key-2024")


async def verify_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
    """
    Xác thực API key từ header X-API-Key.
    Nếu không có API key hoặc sai → trả 401/403.
    """
    if x_api_key is None:
        raise HTTPException(
            status_code=401,
            detail="Thiếu API key. Thêm header: X-API-Key: <your-key>"
        )
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="API key không hợp lệ."
        )
    return x_api_key
