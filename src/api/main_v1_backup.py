#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Warm Agent API 主服务
基于FastAPI的RESTful API服务
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field, validator
import uvicorn

from ..core.emotion_analyzer import get_emotion_analyzer, EmotionResult
from ..core.warm_response_engine import get_warm_response_engine, WarmResponse
from ..integrations.openclaw import get_openclaw_integration


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


class OpenClawRequest(BaseModel):
    """OpenClaw集成请求"""
    content: str = Field(..., min_length=1, max_length=10000, description="消息内容")
    base_response: str = Field(..., description="基础AI回应")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    user_id: str = Field(..., description="用户ID")
    channel: str = Field(..., description="渠道")
    user_context: Optional[Dict[str, Any]] = Field(None, description="用户上下文")


class UpdatePreferencesRequest(BaseModel):
    """更新偏好请求"""
    preferences: Dict[str, Any] = Field(..., description="用户偏好")


# ==================== API Key 认证 ====================

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# 模拟用户数据库（实际实现中应使用数据库）
USERS_DB = {
    "test_user_1": {
        "api_key": "test_api_key_123",
        "plan": "free",
        "quota_used": 0,
        "quota_limit": 1000,
        "preferences": {
            "style": "balanced",
            "emoji_level": "moderate",
            "warmth_intensity": 0.7
        }
    },
    "test_user_2": {
        "api_key": "test_api_key_456",
        "plan": "premium",
        "quota_used": 0,
        "quota_limit": 10000,
        "preferences": {
            "style": "warm",
            "emoji_level": "high",
            "warmth_intensity": 0.9
        }
    }
}

API_KEYS = {user_data["api_key"]: user_id for user_id, user_data in USERS_DB.items()}


async def get_current_user(api_key: str = Depends(api_key_header)):
    """验证API Key并获取用户"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is required"
        )
    
    if api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    
    user_id = API_KEYS[api_key]
    user_data = USERS_DB[user_id]
    
    # 检查配额
    if user_data["quota_used"] >= user_data["quota_limit"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Quota exceeded"
        )
    
    # 更新使用量
    user_data["quota_used"] += 1
    
    return {
        "user_id": user_id,
        "plan": user_data["plan"],
        "preferences": user_data["preferences"]
    }


# ==================== FastAPI 应用 ====================

app = FastAPI(
    title="Warm Agent API",
    description="为AI注入温度与情感的API服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化核心组件
emotion_analyzer = get_emotion_analyzer()
warm_engine = get_warm_response_engine()
openclaw_integration = get_openclaw_integration()


# ==================== 中间件 ====================

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """添加处理时间头"""
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds()
    response.headers["X-Process-Time"] = str(process_time)
    return response


# ==================== 健康检查端点 ====================

@app.get("/")
async def root():
    """根端点"""
    return {
        "service": "Warm Agent API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "emotion_analysis": "/v1/emotion/analyze",
            "warm_response": "/v1/warm-response/generate",
            "openclaw": "/v1/openclaw/process",
            "user_summary": "/v1/user/{user_id}/summary"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "emotion_analyzer": "ok",
            "warm_engine": "ok",
            "openclaw_integration": "ok"
        }
    }


# ==================== 情感分析端点 ====================

@app.post("/v1/emotion/analyze")
async def analyze_emotion(
    request: EmotionRequest,
    user: Dict = Depends(get_current_user)
):
    """
    情感分析端点
    
    - **text**: 要分析的文本
    - **language**: 语言代码 (zh-CN, en-US, ja-JP)
    - **context**: 上下文信息
    """
    try:
        # 执行情感分析
        emotion_result = emotion_analyzer.analyze(
            request.text,
            context=request.context
        )
        
        return {
            "success": True,
            "data": emotion_result.to_dict(),
            "metadata": {
                "user_id": user["user_id"],
                "plan": user["plan"],
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


# ==================== 温暖回应生成端点 ====================

@app.post("/v1/warm-response/generate")
async def generate_warm_response(
    request: WarmResponseRequest,
    user: Dict = Depends(get_current_user)
):
    """
    温暖回应生成端点
    
    - **text**: 用户输入文本
    - **base_response**: 基础AI回应
    - **emotion_data**: 情感分析数据（可选）
    - **user_context**: 用户上下文（可选）
    """
    try:
        # 如果没有提供情感数据，先进行分析
        if request.emotion_data:
            emotion_result = EmotionResult.from_dict(request.emotion_data)
        else:
            emotion_result = emotion_analyzer.analyze(request.text)
        
        # 合并用户上下文和偏好
        user_context = request.user_context or {}
        if "preferences" not in user_context:
            user_context["preferences"] = user["preferences"]
        
        # 生成温暖回应
        warm_response = warm_engine.generate(
            emotion_result=emotion_result,
            base_response=request.base_response,
            user_context=user_context
        )
        
        return {
            "success": True,
            "data": warm_response.to_dict(),
            "metadata": {
                "user_id": user["user_id"],
                "plan": user["plan"],
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Response generation failed: {str(e)}"
        )


# ==================== OpenClaw集成端点 ====================

@app.post("/v1/openclaw/process")
async def process_openclaw_message(
    request: OpenClawRequest,
    user: Dict = Depends(get_current_user)
):
    """
    OpenClaw集成端点
    
    - **content**: 消息内容
    - **base_response**: 基础AI回应
    - **metadata**: 元数据
    - **user_id**: 用户ID
    - **channel**: 渠道
    - **user_context**: 用户上下文
    """
    try:
        from ..integrations.openclaw import OpenClawMessage, OpenClawContext
        
        # 创建消息和上下文
        message = OpenClawMessage(
            content=request.content,
            base_response=request.base_response,
            metadata=request.metadata
        )
        
        # 合并用户上下文和偏好
        user_context = request.user_context or {}
        if "preferences" not in user_context:
            user_context["preferences"] = user["preferences"]
        
        context = OpenClawContext(
            user_id=request.user_id,
            channel=request.channel,
            user_context=user_context
        )
        
        # 处理消息
        result = openclaw_integration.process_message(message, context)
        
        return {
            "success": True,
            "data": {
                "enhanced_response": result.enhanced_response,
                "should_enhance": result.should_enhance,
                "emotion_data": result.emotion_data.to_dict(),
                "enhancement_metadata": result.enhancement_metadata
            },
            "metadata": {
                "user_id": user["user_id"],
                "plan": user["plan"],
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OpenClaw processing failed: {str(e)}"
        )


# ==================== 用户管理端点 ====================

@app.get("/v1/user/{user_id}/summary")
async def get_user_summary(
    user_id: str,
    user: Dict = Depends(get_current_user)
):
    """
    获取用户摘要
    
    - **user_id**: 用户ID
    """
    # 检查权限（只能访问自己的数据）
    if user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other user's data"
        )
    
    try:
        summary = openclaw_integration.get_user_summary(user_id)
        
        return {
            "success": True,
            "data": summary,
            "metadata": {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user summary: {str(e)}"
        )


@app.put("/v1/user/{user_id}/preferences")
async def update_user_preferences(
    user_id: str,
    request: UpdatePreferencesRequest,
    user: Dict = Depends(get_current_user)
):
    """
    更新用户偏好
    
    - **user_id**: 用户ID
    - **preferences**: 用户偏好
    """
    # 检查权限
    if user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update other user's preferences"
        )
    
    try:
        result = openclaw_integration.update_user_preferences(
            user_id, request.preferences
        )
        
        # 同时更新用户数据库
        if user_id in USERS_DB:
            USERS_DB[user_id]["preferences"].update(request.preferences)
        
        return {
            "success": True,
            "data": result,
            "metadata": {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )


# ==================== 配额管理端点 ====================

@app.get("/v1/user/{user_id}/quota")
async def get_user_quota(
    user_id: str,
    user: Dict = Depends(get_current_user)
):
    """
    获取用户配额信息
    
    - **user_id**: 用户ID
    """
    # 检查权限
    if user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other user's quota"
        )
    
    if user_id not in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_data = USERS_DB[user_id]
    
    return {
        "success": True,
        "data": {
            "user_id": user_id,
            "plan": user_data["plan"],
            "quota_used": user_data["quota_used"],
            "quota_limit": user_data["quota_limit"],
            "quota_remaining": user_data["quota_limit"] - user_data["quota_used"],
            "usage_percentage": (user_data["quota_used"] / user_data["quota_limit"]) * 100
        },
        "metadata": {
            "timestamp": datetime.utcnow().isoformat()
        }
    }


# ==================== 批量处理端点 ====================

@app.post("/v1/batch/emotion/analyze")
async def batch_analyze_emotion(
    requests: List[EmotionRequest],
    user: Dict = Depends(get_current_user)
):
    """
    批量情感分析端点
    
    - **requests**: 情感分析请求列表
    """
    try:
        results = []
        
        for req in requests:
            emotion_result = emotion_analyzer.analyze(
                req.text,
                context=req.context
            )
            results.append(emotion_result.to_dict())
        
        return {
            "success": True,
            "data": results,
            "metadata": {
                "user_id": user["user_id"],
                "plan": user["plan"],
                "total_requests": len(requests),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch analysis failed: {str(e)}"
        )


# ==================== 错误处理 ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理器"""
    return {
        "success": False,
        "error": {
            "code": exc.status_code,
            "message": exc.detail
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理器"""
    return {
        "success": False,
        "error": {
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Internal server error"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ==================== 启动应用 ====================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )