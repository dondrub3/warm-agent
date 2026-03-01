#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Warm Agent API 主服务 - 包含用户管理功能
基于FastAPI的RESTful API服务
"""

import os
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, validator
import uvicorn

from ..core.emotion_analyzer import get_emotion_analyzer, EmotionResult
from ..core.warm_response_engine import get_warm_response_engine, WarmResponse
from ..core.user_manager import get_user_manager, UserManager, User
from ..core.email_service import get_email_service


# ==================== Pydantic 模型 ====================

class EmotionRequest(BaseModel):
    """情感分析请求"""
    text: str = Field(..., min_length=1, max_length=10000, description="要分析的文本")
    language: str = Field("zh-CN", description="语言代码")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")
    
    @validator('language')
    def validate_language(cls, v):
        valid_languages = ["zh-CN", "en-US", "ja-JP"]
        if v not in valid_languages:
            raise ValueError(f"Language must be one of: {valid_languages}")
        return v


class WarmResponseRequest(BaseModel):
    """温暖回应生成请求"""
    text: str = Field(..., min_length=1, max_length=10000, description="用户输入文本")
    base_response: Optional[str] = Field(None, description="基础AI回应")
    emotion_data: Optional[Dict[str, Any]] = Field(None, description="情感分析数据")
    user_context: Optional[Dict[str, Any]] = Field(None, description="用户上下文")


class RegisterRequest(BaseModel):
    """用户注册请求"""
    email: str = Field(..., description="用户邮箱")
    plan: str = Field("free", description="套餐类型")


class LoginRequest(BaseModel):
    """用户登录请求"""
    email: str = Field(..., description="用户邮箱")


class UserResponse(BaseModel):
    """用户响应"""
    id: str
    email: str
    api_key: str
    plan: str
    quota_used: int
    quota_limit: int
    quota_remaining: int
    usage_percentage: float
    is_active: bool
    created_at: Optional[str]
    updated_at: Optional[str]


class UsageStatsResponse(BaseModel):
    """用量统计响应"""
    period_days: int
    total_requests: int
    avg_processing_time_ms: float
    by_endpoint: List[Dict[str, Any]]
    by_day: List[Dict[str, Any]]


# ==================== FastAPI 应用 ====================

app = FastAPI(
    title="Warm Agent API",
    description="为AI注入温度与情感的API服务",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化核心组件
emotion_analyzer = get_emotion_analyzer()
warm_engine = get_warm_response_engine()
user_manager = get_user_manager()
email_service = get_email_service()

# API Key 认证
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user(api_key: str = Depends(api_key_header)) -> User:
    """验证API Key并获取用户"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is required"
        )
    
    user = user_manager.get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # 检查配额
    if user.quota_used >= user.quota_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Quota exceeded. Please upgrade your plan."
        )
    
    return user


def check_and_increment_quota(user: User) -> bool:
    """检查并增加用量计数"""
    return user_manager.increment_quota(user.api_key)


# ==================== 公开端点（无需认证） ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    """首页 - 简单的欢迎页面"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Warm Agent API</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                   max-width: 800px; margin: 50px auto; padding: 20px; line-height: 1.6; }
            .header { text-align: center; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      color: white; border-radius: 10px; }
            .content { margin-top: 30px; }
            .cta { display: inline-block; background: #667eea; color: white; padding: 12px 30px; 
                   text-decoration: none; border-radius: 5px; margin: 10px; }
            .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 30px; }
            .feature { padding: 20px; background: #f5f5f5; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎉 Warm Agent API</h1>
            <p>为AI注入温度与情感</p>
        </div>
        <div class="content">
            <h2>快速开始</h2>
            <p>Warm Agent 是一个轻量级的情感增强服务，让您的AI回应更有温度和同理心。</p>
            <center>
                <a href="/register" class="cta">免费注册</a>
                <a href="/docs" class="cta">API 文档</a>
                <a href="/dashboard" class="cta">Dashboard</a>
            </center>
            
            <div class="features">
                <div class="feature">
                    <h3>🎯 情感分析</h3>
                    <p>准确识别9种情感类型，理解用户真实情绪</p>
                </div>
                <div class="feature">
                    <h3>💝 温暖回应</h3>
                    <p>将普通AI回应转化为有温度的表达</p>
                </div>
                <div class="feature">
                    <h3>⚡ 高性能</h3>
                    <p>&lt;100ms响应，支持高并发</p>
                </div>
                <div class="feature">
                    <h3>🔒 安全可靠</h3>
                    <p>API Key认证，用量监控，数据安全</p>
                </div>
            </div>
            
            <h2>定价</h2>
            <ul>
                <li><strong>Free</strong>: 1,000 次/月 - 免费</li>
                <li><strong>Pro</strong>: 10,000 次/月 - $9/月</li>
                <li><strong>Enterprise</strong>: 100,000 次/月 - $49/月</li>
            </ul>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.1.0",
        "components": {
            "emotion_analyzer": "ok",
            "warm_engine": "ok",
            "user_system": "ok"
        }
    }


@app.post("/auth/register", response_model=UserResponse)
async def register(request: RegisterRequest, background_tasks: BackgroundTasks):
    """
    用户注册
    
    - **email**: 用户邮箱
    - **plan**: 套餐类型 (free/pro/enterprise)，默认 free
    
    注册成功后会发送API key到邮箱
    """
    try:
        user = user_manager.create_user(request.email, request.plan)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # 异步发送邮件
    background_tasks.add_task(
        email_service.send_api_key,
        user.email,
        user.api_key,
        user.plan
    )
    
    return user.to_full_dict()


@app.post("/auth/login")
async def login(request: LoginRequest):
    """
    用户登录
    
    通过邮箱获取用户信息（包含完整API key）
    """
    user = user_manager.get_user_by_email(request.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "message": "Login successful",
        "user": user.to_full_dict()
    }


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Dashboard 页面（简化版）"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Warm Agent Dashboard</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; }
            .form { margin: 30px 0; padding: 20px; background: #f5f5f5; border-radius: 8px; }
            input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #667eea; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #5568d3; }
            .result { margin-top: 20px; padding: 15px; background: #e8f5e9; border-radius: 5px; display: none; }
            .error { background: #ffebee; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Dashboard</h1>
            <p>查看您的 API 用量和账户信息</p>
        </div>
        
        <div class="form">
            <h3>登录查看</h3>
            <input type="email" id="email" placeholder="输入您的邮箱">
            <button onclick="login()">查看用量</button>
            <div id="result" class="result"></div>
        </div>
        
        <script>
            async function login() {
                const email = document.getElementById('email').value;
                const resultDiv = document.getElementById('result');
                
                try {
                    const response = await fetch('/auth/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        const user = data.user;
                        resultDiv.innerHTML = `
                            <h4>✅ 登录成功</h4>
                            <p><strong>邮箱:</strong> ${user.email}</p>
                            <p><strong>套餐:</strong> ${user.plan}</p>
                            <p><strong>API Key:</strong> <code>${user.api_key}</code></p>
                            <p><strong>用量:</strong> ${user.quota_used} / ${user.quota_limit} (${user.usage_percentage}%)</p>
                            <p><strong>剩余:</strong> ${user.quota_remaining} 次</p>
                            <hr>
                            <p><a href="/user/usage?days=30&api_key=${user.api_key}">查看详细用量统计</a></p>
                        `;
                        resultDiv.className = 'result';
                    } else {
                        resultDiv.innerHTML = `<p>❌ ${data.detail}</p>`;
                        resultDiv.className = 'result error';
                    }
                } catch (e) {
                    resultDiv.innerHTML = `<p>❌ 请求失败: ${e.message}</p>`;
                    resultDiv.className = 'result error';
                }
                resultDiv.style.display = 'block';
            }
        </script>
    </body>
    </html>
    """


# ==================== 认证端点（需要API Key） ====================

@app.get("/user/profile", response_model=UserResponse)
async def get_profile(user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return user.to_dict()


@app.post("/user/regenerate-key")
async def regenerate_key(user: User = Depends(get_current_user)):
    """重新生成API Key"""
    new_key = user_manager.regenerate_api_key(user.id)
    
    if not new_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate API key"
        )
    
    return {
        "message": "API key regenerated successfully",
        "api_key": new_key
    }


@app.get("/user/usage", response_model=UsageStatsResponse)
async def get_usage(
    days: int = 30,
    user: User = Depends(get_current_user)
):
    """获取用量统计"""
    return user_manager.get_usage_stats(user.id, days)


# ==================== 核心功能端点（需要API Key） ====================

@app.post("/v1/emotion/analyze")
async def analyze_emotion(
    request: EmotionRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user)
):
    """
    情感分析端点
    
    - **text**: 要分析的文本
    - **language**: 语言代码 (zh-CN, en-US, ja-JP)
    - **context**: 上下文信息
    """
    start_time = time.time()
    
    # 检查并增加配额
    if not check_and_increment_quota(user):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Quota exceeded"
        )
    
    try:
        # 执行情感分析
        emotion_result = emotion_analyzer.analyze(
            request.text,
            context=request.context
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        # 后台记录用量
        background_tasks.add_task(
            user_manager.log_usage,
            user.api_key,
            "/v1/emotion/analyze",
            len(request.text),
            len(json.dumps(emotion_result.to_dict())),
            processing_time
        )
        
        return {
            "success": True,
            "data": emotion_result.to_dict(),
            "metadata": {
                "user_id": user.id,
                "plan": user.plan,
                "quota_remaining": user.quota_limit - user.quota_used - 1,
                "processing_time_ms": processing_time,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/v1/warm-response/generate")
async def generate_warm_response(
    request: WarmResponseRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user)
):
    """
    温暖回应生成端点
    
    - **text**: 用户输入文本
    - **base_response**: 基础AI回应
    - **emotion_data**: 情感分析数据（可选）
    - **user_context**: 用户上下文（可选）
    """
    start_time = time.time()
    
    # 检查并增加配额
    if not check_and_increment_quota(user):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Quota exceeded"
        )
    
    try:
        # 如果没有提供情感数据，先进行分析
        if request.emotion_data:
            emotion_result = EmotionResult.from_dict(request.emotion_data)
        else:
            emotion_result = emotion_analyzer.analyze(request.text)
        
        # 合并用户上下文和偏好
        user_context = request.user_context or {}
        if "preferences" not in user_context:
            user_context["preferences"] = {
                "style": "warm",
                "emoji_level": "moderate",
                "warmth_intensity": 0.8
            }
        
        # 生成温暖回应
        warm_response = warm_engine.generate(
            emotion_result=emotion_result,
            base_response=request.base_response,
            user_context=user_context
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        # 后台记录用量
        background_tasks.add_task(
            user_manager.log_usage,
            user.api_key,
            "/v1/warm-response/generate",
            len(request.text),
            len(warm_response.text),
            processing_time
        )
        
        return {
            "success": True,
            "data": warm_response.to_dict(),
            "metadata": {
                "user_id": user.id,
                "plan": user.plan,
                "quota_remaining": user.quota_limit - user.quota_used - 1,
                "processing_time_ms": processing_time,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Response generation failed: {str(e)}"
        )


# ==================== 启动入口 ====================

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
