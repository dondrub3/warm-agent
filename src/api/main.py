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
    password: str = Field(..., min_length=6, description="用户密码（至少6位）")
    plan: str = Field("free", description="套餐类型")


class LoginRequest(BaseModel):
    """用户登录请求"""
    email: str = Field(..., description="用户邮箱")
    password: str = Field(..., description="用户密码")


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
                      color: white; border-radius: 10px; position: relative; }
            .content { margin-top: 30px; }
            .cta { display: inline-block; background: #667eea; color: white; padding: 12px 30px; 
                   text-decoration: none; border-radius: 5px; margin: 10px; font-weight: bold; font-size: 16px; }
            .cta-large { padding: 15px 40px; font-size: 18px; margin: 15px; }
            .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 30px; }
            .feature { padding: 20px; background: #f5f5f5; border-radius: 8px; }
            .login-buttons { position: absolute; top: 20px; right: 20px; }
            .login-btn { background: rgba(255, 255, 255, 0.2); color: white; padding: 8px 20px; 
                         text-decoration: none; border-radius: 5px; margin-left: 10px; border: 1px solid rgba(255, 255, 255, 0.3); }
            .login-btn:hover { background: rgba(255, 255, 255, 0.3); }
            .hero-cta { margin-top: 30px; }
            .hero-cta .cta { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); }
            .hero-cta .cta:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2); transition: all 0.3s ease; }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="login-buttons">
                <a href="/login" class="login-btn">🔐 登录</a>
                <a href="/register" class="login-btn" style="background: rgba(40, 167, 69, 0.7);">📝 注册</a>
            </div>
            <h1>🎉 Warm Agent API</h1>
            <p>为AI注入温度与情感</p>
            <div class="hero-cta">
                <a href="/register" class="cta cta-large" style="background: #28a745;">🚀 免费注册</a>
                <a href="/login" class="cta cta-large" style="background: #667eea;">🔐 立即登录</a>
            </div>
        </div>
        <div class="content">
            <h2>快速开始</h2>
            <p>Warm Agent 是一个轻量级的情感增强服务，让您的AI回应更有温度和同理心。</p>
            <center>
                <a href="/register" class="cta" style="background: #28a745;">📝 免费注册</a>
                <a href="/login" class="cta" style="background: #667eea;">🔐 登录</a>
                <a href="/dashboard" class="cta" style="background: #6c757d;">📊 Dashboard</a>
                <a href="/docs" class="cta">📚 API 文档</a>
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


@app.get("/register", response_class=HTMLResponse)
async def register_page():
    """注册页面"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>注册 - Warm Agent</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; }
            .form { margin-top: 30px; padding: 30px; background: #f5f5f5; border-radius: 8px; }
            input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            button { width: 100%; background: #667eea; color: white; padding: 14px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #5568d3; }
            .result { margin-top: 20px; padding: 15px; border-radius: 5px; display: none; }
            .success { background: #e8f5e9; border: 1px solid #4caf50; }
            .error { background: #ffebee; border: 1px solid #f44336; }
            .login-link { text-align: center; margin-top: 20px; }
            .login-link a { color: #667eea; text-decoration: none; }
            code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; word-break: break-all; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📝 注册</h1>
            <p>创建您的 Warm Agent 账户</p>
        </div>
        
        <div class="form">
            <input type="email" id="email" placeholder="邮箱地址" required>
            <input type="password" id="password" placeholder="密码（至少6位）" required>
            <select id="plan" style="width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px;">
                <option value="free">Free - 1,000次/月</option>
                <option value="pro">Pro - 10,000次/月 ($9/月)</option>
                <option value="enterprise">Enterprise - 100,000次/月 ($49/月)</option>
            </select>
            <button onclick="register()">创建账户</button>
            <div id="result" class="result"></div>
        </div>
        
        <div class="login-link">
            <p>已有账户？<a href="/login">立即登录</a></p>
        </div>
        
        <script>
            async function register() {
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                const plan = document.getElementById('plan').value;
                const resultDiv = document.getElementById('result');
                
                if (!email || !password) {
                    resultDiv.innerHTML = '<p>❌ 请填写邮箱和密码</p>';
                    resultDiv.className = 'result error';
                    resultDiv.style.display = 'block';
                    return;
                }
                
                if (password.length < 6) {
                    resultDiv.innerHTML = '<p>❌ 密码至少需要6位</p>';
                    resultDiv.className = 'result error';
                    resultDiv.style.display = 'block';
                    return;
                }
                
                try {
                    const response = await fetch('/auth/register', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email, password, plan })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultDiv.innerHTML = `
                            <h3>✅ 注册成功！</h3>
                            <p><strong>邮箱:</strong> ${data.email}</p>
                            <p><strong>API Key:</strong></p>
                            <code style="display: block; padding: 10px; background: #f4f4f4; margin: 10px 0;">${data.api_key}</code>
                            <p><strong>套餐:</strong> ${data.plan}</p>
                            <p><strong>每月额度:</strong> ${data.quota_limit} 次</p>
                            <hr>
                            <p>📝 请保存好您的 API Key，您也可以随时在 <a href="/dashboard">Dashboard</a> 查看</p>
                            <p><a href="/docs">查看 API 文档</a> 开始使用</p>
                        `;
                        resultDiv.className = 'result success';
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


@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """登录页面"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>登录 - Warm Agent</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; }
            .form { margin-top: 30px; padding: 30px; background: #f5f5f5; border-radius: 8px; }
            input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            button { width: 100%; background: #667eea; color: white; padding: 14px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #5568d3; }
            .result { margin-top: 20px; padding: 15px; border-radius: 5px; display: none; }
            .success { background: #e8f5e9; border: 1px solid #4caf50; }
            .error { background: #ffebee; border: 1px solid #f44336; }
            .links { text-align: center; margin-top: 20px; }
            .links a { color: #667eea; text-decoration: none; margin: 0 10px; }
            .warning { background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin-top: 20px; }
            code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; word-break: break-all; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔐 登录</h1>
            <p>访问您的 Warm Agent 账户</p>
        </div>
        
        <div class="form">
            <input type="email" id="email" placeholder="邮箱地址" required>
            <input type="password" id="password" placeholder="密码" required>
            <button onclick="login()">登录</button>
            <div id="result" class="result"></div>
        </div>
        
        <div class="links">
            <p><a href="/register">创建新账户</a> | <a href="/dashboard">Dashboard</a></p>
        </div>
        
        <div class="warning">
            <h4>📝 忘记密码？</h4>
            <p>如果您忘记了密码，可以<strong>注销当前账户</strong>，然后使用相同邮箱重新注册。</p>
            <p>当前为免费版，注销后重新注册不会有任何损失。</p>
            <p>👉 <a href="/dashboard">前往 Dashboard 注销账户</a></p>
        </div>
        
        <script>
            async function login() {
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                const resultDiv = document.getElementById('result');
                
                if (!email || !password) {
                    resultDiv.innerHTML = '<p>❌ 请填写邮箱和密码</p>';
                    resultDiv.className = 'result error';
                    resultDiv.style.display = 'block';
                    return;
                }
                
                try {
                    const response = await fetch('/auth/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email, password })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        const user = data.user;
                        resultDiv.innerHTML = `
                            <h3>✅ 登录成功！</h3>
                            <p><strong>邮箱:</strong> ${user.email}</p>
                            <p><strong>API Key:</strong></p>
                            <code style="display: block; padding: 10px; background: #f4f4f4; margin: 10px 0;">${user.api_key}</code>
                            <p><strong>套餐:</strong> ${user.plan}</p>
                            <p><strong>用量:</strong> ${user.quota_used} / ${user.quota_limit} (${user.usage_percentage}%)</p>
                            <hr>
                            <p>👉 <a href="/dashboard">进入 Dashboard</a> 查看详细用量统计</p>
                            <p>📚 <a href="/docs">查看 API 文档</a> 开始集成</p>
                        `;
                        resultDiv.className = 'result success';
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
            
            // 支持回车键登录
            document.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    login();
                }
            });
        </script>
    </body>
    </html>
    """


@app.post("/auth/register", response_model=UserResponse)
async def register(request: RegisterRequest, background_tasks: BackgroundTasks):
    """
    用户注册
    
    - **email**: 用户邮箱
    - **password**: 用户密码（至少6位）
    - **plan**: 套餐类型 (free/pro/enterprise)，默认 free
    
    注册成功后会发送API key到邮箱
    """
    try:
        user = user_manager.create_user(request.email, request.password, request.plan)
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
    
    - **email**: 用户邮箱
    - **password**: 用户密码
    
    验证成功后返回用户信息（包含完整API key）
    """
    user = user_manager.authenticate_user(request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
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
            button { background: #667eea; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px; }
            button:hover { background: #5568d3; }
            .btn-danger { background: #e74c3c; }
            .btn-danger:hover { background: #c0392b; }
            .result { margin-top: 20px; padding: 15px; background: #e8f5e9; border-radius: 5px; display: none; }
            .error { background: #ffebee; }
            .warning { background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin-top: 20px; }
            code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Dashboard</h1>
            <p>查看您的 API 用量和账户信息</p>
        </div>
        
        <div class="form" id="loginForm">
            <h3>登录查看</h3>
            <input type="email" id="email" placeholder="输入您的邮箱">
            <input type="password" id="password" placeholder="输入您的密码">
            <button onclick="login()">登录</button>
            <div id="result" class="result"></div>
        </div>
        
        <div class="form" id="userPanel" style="display: none;">
            <h3>账户信息</h3>
            <div id="userInfo"></div>
            <hr>
            <button onclick="viewUsage()">查看详细用量</button>
            <button class="btn-danger" onclick="deleteAccount()">注销账户</button>
            <div id="usageResult" class="result" style="margin-top: 20px;"></div>
        </div>
        
        <div class="warning">
            <h4>📝 忘记密码？</h4>
            <p>如果您忘记了密码或 API Key，可以<strong>注销当前账户</strong>，然后使用相同邮箱重新注册。</p>
            <p>当前为免费版，注销后重新注册不会有任何损失。</p>
        </div>
        
        <script>
            let currentApiKey = '';
            
            async function login() {
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                const resultDiv = document.getElementById('result');
                
                if (!email || !password) {
                    resultDiv.innerHTML = `<p>❌ 请输入邮箱和密码</p>`;
                    resultDiv.className = 'result error';
                    resultDiv.style.display = 'block';
                    return;
                }
                
                try {
                    const response = await fetch('/auth/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email, password })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        const user = data.user;
                        currentApiKey = user.api_key;
                        
                        document.getElementById('loginForm').style.display = 'none';
                        document.getElementById('userPanel').style.display = 'block';
                        
                        document.getElementById('userInfo').innerHTML = `
                            <p><strong>邮箱:</strong> ${user.email}</p>
                            <p><strong>套餐:</strong> ${user.plan}</p>
                            <p><strong>API Key:</strong> <code>${user.api_key}</code></p>
                            <p><strong>用量:</strong> ${user.quota_used} / ${user.quota_limit} (${user.usage_percentage}%)</p>
                            <p><strong>剩余:</strong> ${user.quota_remaining} 次</p>
                        `;
                    } else {
                        resultDiv.innerHTML = `<p>❌ ${data.detail}</p>`;
                        resultDiv.className = 'result error';
                        resultDiv.style.display = 'block';
                    }
                } catch (e) {
                    resultDiv.innerHTML = `<p>❌ 请求失败: ${e.message}</p>`;
                    resultDiv.className = 'result error';
                    resultDiv.style.display = 'block';
                }
            }
            
            async function viewUsage() {
                const resultDiv = document.getElementById('usageResult');
                
                try {
                    const response = await fetch('/user/usage?days=30', {
                        headers: { 'X-API-Key': currentApiKey }
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultDiv.innerHTML = `
                            <h4>📈 用量统计（近${data.period_days}天）</h4>
                            <p><strong>总请求:</strong> ${data.total_requests}</p>
                            <p><strong>平均响应:</strong> ${data.avg_processing_time_ms}ms</p>
                            <p><strong>端点分布:</strong></p>
                            <ul>
                                ${data.by_endpoint.map(e => `<li>${e.endpoint}: ${e.count}</li>`).join('')}
                            </ul>
                            <p><strong>按天统计:</strong></p>
                            <ul>
                                ${data.by_day.map(d => `<li>${d.date}: ${d.count}</li>`).join('')}
                            </ul>
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
            
            async function deleteAccount() {
                if (!confirm('⚠️ 确定要注销账户吗？\n\n此操作将删除您的所有数据，包括用量记录。\n\n注销后可以立即使用相同邮箱重新注册。')) {
                    return;
                }
                
                try {
                    const response = await fetch('/user/delete', {
                        method: 'DELETE',
                        headers: { 'X-API-Key': currentApiKey }
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        alert('✅ 账户已注销！\n\n您可以立即使用相同邮箱重新注册。');
                        location.reload();
                    } else {
                        alert('❌ 注销失败: ' + data.detail);
                    }
                } catch (e) {
                    alert('❌ 请求失败: ' + e.message);
                }
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


@app.delete("/user/delete")
async def delete_account(user: User = Depends(get_current_user)):
    """
    注销账户
    
    删除用户账户和所有相关数据（用量记录等）
    删除后可以重新使用相同邮箱注册
    """
    success = user_manager.delete_user(user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )
    
    return {
        "message": "Account deleted successfully",
        "note": "You can re-register with the same email anytime"
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
