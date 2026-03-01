-- Warm Agent 用户系统数据库迁移
-- 创建用户表和用量记录表

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    api_key VARCHAR(64) UNIQUE NOT NULL,
    plan VARCHAR(20) DEFAULT 'free',
    quota_used INTEGER DEFAULT 0,
    quota_limit INTEGER DEFAULT 1000,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 用量记录表
CREATE TABLE IF NOT EXISTS usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    endpoint VARCHAR(100) NOT NULL,
    request_size INTEGER DEFAULT 0,
    response_size INTEGER DEFAULT 0,
    processing_time_ms INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API key 查询索引
CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key);

-- 邮箱查询索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- 用量记录查询索引
CREATE INDEX IF NOT EXISTS idx_usage_logs_user_id ON usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_created_at ON usage_logs(created_at);

-- 插入默认测试用户（可选）
-- INSERT INTO users (email, api_key, plan, quota_limit) 
-- VALUES ('test@example.com', 'test_api_key_123', 'free', 1000)
-- ON CONFLICT (email) DO NOTHING;
