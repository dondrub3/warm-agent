#!/usr/bin/env python3
"""
Warm Agent 使用示例
演示如何在不同场景下使用 Warm Agent API
"""

import requests
import json

# API 配置
BASE_URL = "http://localhost:8000"
API_KEY = "test_api_key_123"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}


def analyze_emotion(text: str, context: dict = None) -> dict:
    """
    情感分析示例
    """
    payload = {
        "text": text,
        "language": "zh-CN",
        "context": context or {}
    }
    
    response = requests.post(
        f"{BASE_URL}/v1/emotion/analyze",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def generate_warm_response(text: str, base_response: str, 
                          emotion_data: dict = None,
                          user_context: dict = None) -> dict:
    """
    温暖回应生成示例
    """
    payload = {
        "text": text,
        "base_response": base_response,
        "emotion_data": emotion_data,
        "user_context": user_context or {
            "preferences": {
                "style": "warm",
                "emoji_level": "moderate",
                "warmth_intensity": 0.8
            }
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/v1/warm-response/generate",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def health_check():
    """
    健康检查示例
    """
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        return response.json()
    return None


def print_result(title: str, data: dict):
    """
    美化打印结果
    """
    print(f"\n{'='*60}")
    print(f"📝 {title}")
    print('='*60)
    if data:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print("❌ 请求失败")


if __name__ == "__main__":
    # 场景1: 工作压力
    print("\n🔹 场景1: 工作压力场景")
    text1 = "今天工作压力好大，不知道该怎么办"
    emotion1 = analyze_emotion(text1)
    print_result("情感分析结果", emotion1)
    
    if emotion1:
        warm1 = generate_warm_response(
            text=text1,
            base_response="建议你休息一下",
            emotion_data=emotion1["data"]
        )
        print_result("温暖回应", warm1)
    
    # 场景2: 开心分享
    print("\n🔹 场景2: 开心分享场景")
    text2 = "哈哈，今天项目终于上线了，太开心了！"
    emotion2 = analyze_emotion(text2)
    print_result("情感分析结果", emotion2)
    
    if emotion2:
        warm2 = generate_warm_response(
            text=text2,
            base_response="恭喜！项目上线辛苦了",
            emotion_data=emotion2["data"]
        )
        print_result("温暖回应", warm2)
    
    # 场景3: 生气抱怨
    print("\n🔹 场景3: 生气抱怨场景")
    text3 = "这个服务又崩溃了，气死我了！"
    emotion3 = analyze_emotion(text3)
    print_result("情感分析结果", emotion3)
    
    if emotion3:
        warm3 = generate_warm_response(
            text=text3,
            base_response="我们会尽快修复问题",
            emotion_data=emotion3["data"]
        )
        print_result("温暖回应", warm3)
    
    # 场景4: 表达爱意
    print("\n🔹 场景4: 表达爱意场景")
    text4 = "谢谢你一直陪在我身边，真的很感激"
    emotion4 = analyze_emotion(text4)
    print_result("情感分析结果", emotion4)
    
    if emotion4:
        warm4 = generate_warm_response(
            text=text4,
            base_response="不客气，我也很开心",
            emotion_data=emotion4["data"]
        )
        print_result("温暖回应", warm4)
    
    # 健康检查
    print("\n🔹 系统健康检查")
    health = health_check()
    print_result("健康状态", health)
