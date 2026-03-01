#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 测试
测试FastAPI端点
"""

import pytest
import sys
import os
import json
from fastapi.testclient import TestClient

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api.main import app


class TestAPI:
    """API测试"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def valid_api_key(self):
        return "test_api_key_123"
    
    @pytest.fixture
    def premium_api_key(self):
        return "test_api_key_456"
    
    def test_root_endpoint(self, client):
        """测试根端点"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Warm Agent API"
        assert "endpoints" in data
    
    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "components" in data
    
    def test_emotion_analysis_without_auth(self, client):
        """测试未认证的情感分析"""
        data = {"text": "今天心情很好"}
        response = client.post("/v1/emotion/analyze", json=data)
        
        assert response.status_code == 401
    
    def test_emotion_analysis_with_auth(self, client, valid_api_key):
        """测试认证的情感分析"""
        headers = {"X-API-Key": valid_api_key}
        data = {"text": "今天心情很好"}
        
        response = client.post("/v1/emotion/analyze", 
                              json=data, 
                              headers=headers)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] is True
        assert "data" in result
        assert "primary_emotion" in result["data"]
        assert "intensity" in result["data"]
        assert "metadata" in result
    
    def test_emotion_analysis_with_context(self, client, valid_api_key):
        """测试带上下文的情感分析"""
        headers = {"X-API-Key": valid_api_key}
        data = {
            "text": "工作压力大",
            "language": "zh-CN",
            "context": {
                "previous_emotions": ["stress"],
                "time_of_day": "morning"
            }
        }
        
        response = client.post("/v1/emotion/analyze",
                              json=data,
                              headers=headers)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] is True
        assert result["data"]["primary_emotion"] in ["anxiety", "stress", "fear"]
    
    def test_warm_response_generation(self, client, valid_api_key):
        """测试温暖回应生成"""
        headers = {"X-API-Key": valid_api_key}
        data = {
            "text": "今天工作压力大",
            "base_response": "建议休息一下",
            "emotion_data": {
                "primary_emotion": "anxiety",
                "secondary_emotions": ["stress"],
                "intensity": 0.8,
                "confidence": 0.9,
                "keywords": ["压力"],
                "context_hints": ["work"],
                "needs_support": True,
                "suggested_response": "听到你提到压力..."
            }
        }
        
        response = client.post("/v1/warm-response/generate",
                              json=data,
                              headers=headers)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] is True
        assert "warm_response" in result["data"]
        assert "warmth_score" in result["data"]
        assert result["data"]["warmth_score"] > 0.0
    
    def test_warm_response_without_emotion_data(self, client, valid_api_key):
        """测试不带情感数据的温暖回应生成"""
        headers = {"X-API-Key": valid_api_key}
        data = {
            "text": "今天很难过",
            "base_response": "建议找朋友聊聊"
        }
        
        response = client.post("/v1/warm-response/generate",
                              json=data,
                              headers=headers)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] is True
        assert "warm_response" in result["data"]
    
    def test_openclaw_integration(self, client, valid_api_key):
        """测试OpenClaw集成"""
        headers = {"X-API-Key": valid_api_key}
        data = {
            "content": "今天工作压力好大",
            "base_response": "建议你休息一下",
            "user_id": "test_user_1",
            "channel": "qqbot",
            "user_context": {
                "preferences": {
                    "style": "warm",
                    "emoji_level": "moderate"
                }
            }
        }
        
        response = client.post("/v1/openclaw/process",
                              json=data,
                              headers=headers)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] is True
        assert "enhanced_response" in result["data"]
        assert "should_enhance" in result["data"]
    
    def test_user_summary(self, client, valid_api_key):
        """测试用户摘要"""
        headers = {"X-API-Key": valid_api_key}
        
        # 先进行一些交互
        interaction_data = {
            "content": "今天心情不好",
            "base_response": "建议休息",
            "user_id": "test_user_1",
            "channel": "qqbot"
        }
        
        client.post("/v1/openclaw/process",
                   json=interaction_data,
                   headers=headers)
        
        # 获取用户摘要
        response = client.get("/v1/user/test_user_1/summary",
                             headers=headers)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] is True
        assert "data" in result
        assert "user_id" in result["data"]
    
    def test_user_summary_unauthorized(self, client, valid_api_key):
        """测试未授权的用户摘要访问"""
        headers = {"X-API-Key": valid_api_key}
        
        # 尝试访问其他用户的数据
        response = client.get("/v1/user/test_user_2/summary",
                             headers=headers)
        
        assert response.status_code == 403
    
    def test_update_user_preferences(self, client, valid_api_key):
        """测试更新用户偏好"""
        headers = {"X-API-Key": valid_api_key}
        data = {
            "preferences": {
                "style": "professional",
                "emoji_level": "none",
                "warmth_intensity": 0.3
            }
        }
        
        response = client.put("/v1/user/test_user_1/preferences",
                             json=data,
                             headers=headers)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] is True
        assert "updated_preferences" in result["data"]
        assert result["data"]["updated_preferences"]["style"] == "professional"
    
    def test_get_user_quota(self, client, valid_api_key):
        """测试获取用户配额"""
        headers = {"X-API-Key": valid_api_key}
        
        response = client.get("/v1/user/test_user_1/quota",
                             headers=headers)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] is True
        assert "quota_used" in result["data"]
        assert "quota_limit" in result["data"]
        assert "quota_remaining" in result["data"]
    
    def test_batch_emotion_analysis(self, client, valid_api_key):
        """测试批量情感分析"""
        headers = {"X-API-Key": valid_api_key}
        data = [
            {"text": "今天很开心"},
            {"text": "工作压力大"},
            {"text": "需要安慰"}
        ]
        
        response = client.post("/v1/batch/emotion/analyze",
                              json=data,
                              headers=headers)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] is True
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 3
        assert "total_requests" in result["metadata"]
    
    def test_rate_limiting_simulation(self, client):
        """测试限流模拟"""
        # 创建一个新用户进行测试
        test_api_key = "test_rate_limit_key"
        
        # 模拟超过配额
        headers = {"X-API-Key": test_api_key}
        data = {"text": "测试"}
        
        # 在实际实现中，这里会测试配额限制
        # 这里只是测试API Key验证
        response = client.post("/v1/emotion/analyze",
                              json=data,
                              headers=headers)
        
        # 无效的API Key应该返回401
        assert response.status_code == 401
    
    def test_invalid_language(self, client, valid_api_key):
        """测试无效语言"""
        headers = {"X-API-Key": valid_api_key}
        data = {
            "text": "今天心情很好",
            "language": "invalid_lang"
        }
        
        response = client.post("/v1/emotion/analyze",
                              json=data,
                              headers=headers)
        
        # 应该返回验证错误
        assert response.status_code == 422
    
    def test_empty_text(self, client, valid_api_key):
        """测试空文本"""
        headers = {"X-API-Key": valid_api_key}
        data = {"text": ""}
        
        response = client.post("/v1/emotion/analyze",
                              json=data,
                              headers=headers)
        
        # 应该返回验证错误
        assert response.status_code == 422
    
    def test_long_text(self, client, valid_api_key):
        """测试长文本"""
        headers = {"X-API-Key": valid_api_key}
        data = {"text": "a" * 10001}  # 超过10000字符
        
        response = client.post("/v1/emotion/analyze",
                              json=data,
                              headers=headers)
        
        # 应该返回验证错误
        assert response.status_code == 422


if __name__ == "__main__":
    """运行API测试"""
    print("运行API测试...")
    
    # 创建测试客户端
    client = TestClient(app)
    
    # 测试健康检查
    print("\n=== 测试健康检查 ===")
    response = client.get("/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    # 测试根端点
    print("\n=== 测试根端点 ===")
    response = client.get("/")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"服务: {data['service']}")
    print(f"版本: {data['version']}")
    
    # 测试认证的情感分析
    print("\n=== 测试情感分析（带认证）===")
    headers = {"X-API-Key": "test_api_key_123"}
    data = {"text": "今天工作压力大，有点焦虑"}
    
    response = client.post("/v1/emotion/analyze",
                          json=data,
                          headers=headers)
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"成功: {result['success']}")
        print(f"主要情感: {result['data']['primary_emotion']}")
        print(f"强度: {result['data']['intensity']}")
        print(f"关键词: {result['data']['keywords']}")
    
    # 测试温暖回应生成
    print("\n=== 测试温暖回应生成 ===")
    data = {
        "text": "今天很难过",
        "base_response": "建议你休息一下，听听音乐"
    }
    
    response = client.post("/v1/warm-response/generate",
                          json=data,
                          headers=headers)
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"成功: {result['success']}")
        print(f"温暖回应: {result['data']['text']}")
        print(f"温暖度分数: {result['data']['warmth_score']:.2f}")
    
    print("\n✅ API测试完成！")