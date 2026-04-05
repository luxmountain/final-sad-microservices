-- ================================================================
-- MODULE 2 — Schema SQL cho pgvector (PostgreSQL)
-- ================================================================
-- Chạy trong database ai_behavior_db
-- Yêu cầu: PostgreSQL 15+ với pgvector extension

-- Kích hoạt extension pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Bảng lưu documents đã chunk + embedding
CREATE TABLE IF NOT EXISTS kb_documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,                          -- Nội dung chunk
    metadata JSONB DEFAULT '{}',                    -- Source, type, etc.
    embedding vector(384) NOT NULL,                 -- Embedding 384-dim (MiniLM)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index cho tìm kiếm vector similarity (cosine distance)
CREATE INDEX IF NOT EXISTS idx_kb_embedding
    ON kb_documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 10);

-- Bảng lưu behavior profile của từng user
CREATE TABLE IF NOT EXISTS behavior_profiles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,           -- ID khách hàng
    behavior_label VARCHAR(50) NOT NULL,            -- impulse_buyer, researcher, ...
    behavior_label_id INTEGER NOT NULL,             -- 0-4
    confidence FLOAT DEFAULT 0.0,                   -- Độ tin cậy dự đoán
    embedding vector(128),                          -- Behavior embedding 128-dim
    probabilities JSONB DEFAULT '{}',               -- Xác suất từng nhóm
    session_data JSONB DEFAULT '[]',                -- Raw session data gần nhất
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng lưu feedback từ khách hàng
CREATE TABLE IF NOT EXISTS user_feedback (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    message_id VARCHAR(100),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng lưu lịch sử chat (backup từ Redis)
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,                      -- 'user' hoặc 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chat_user ON chat_history(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_profile_user ON behavior_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_user ON user_feedback(user_id);
