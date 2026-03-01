#!/usr/bin/env python3
"""
Warm Agent 高级使用示例
展示不同风格和参数配置
"""

import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = "test_api_key_123"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}


def test_different_styles():
    """
    测试不同风格配置
    """
    text = "今天有点难过，感觉做什么都不顺利"
    base_response = "别难过，明天会更好的"
    
    styles = [
        {
            "name": "温暖风格 (warm)",
            "preferences": {
                "style": "warm",
                "emoji_level": "high",
                "warmth_intensity": 0.9
            }
        },
        {
            "name": "轻松风格 (casual)",
            "preferences": {
                "style": "casual",
                "emoji_level": "moderate",
                "warmth_intensity": 0.6
            }
        },
        {
            "name": "专业风格 (professional)",
            "preferences": {
                "style": "professional",
                "emoji_level": "low",
                "warmth_intensity": 0.4
            }
        }
    ]
    
    print("\n" + "="*70)
    print("🎨 不同风格对比测试")
    print("="*70)
    print(f"\n原文: {text}")
    print(f"基础回应: {base_response}\n")
    
    for style_config in styles:
        print(f"\n{'─'*70}")
        print(f"▶ {style_config['name']}")
        print('─'*70)
        
        payload = {
            "text": text,
            "base_response": base_response,
            "user_context": {
                "preferences": style_config["preferences"]
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/warm-response/generate",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            data = result["data"]
            print(f"温暖度: {data['warmth_score']:.2f}")
            print(f"风格: {data['style']}")
            print(f"回应: {data['text']}")


def test_complex_emotions():
    """
    测试复杂情感场景
    """
    test_cases = [
        {
            "name": "混合情感 - 开心中带点担忧",
            "text": "哈哈，终于拿到offer了！但是新环境会不会适应不了啊..."
        },
        {
            "name": "委婉表达 - 暗示不满",
            "text": "嗯...这个方案可能还有改进空间吧"
        },
        {
            "name": "焦虑求助 - 迫切需要支持",
            "text": " deadline 快到了，代码还有bug，真的好慌，救命"
        },
        {
            "name": "惊喜分享 - 意外的好消息",
            "text": "天哪！没想到居然中奖了！太意外了！"
        },
        {
            "name": "失落情绪 - 期望落空",
            "text": "准备了这么久，结果还是没通过..."
        }
    ]
    
    print("\n" + "="*70)
    print("🎭 复杂情感场景测试")
    print("="*70)
    
    for case in test_cases:
        print(f"\n{'─'*70}")
        print(f"▶ {case['name']}")
        print(f"文本: {case['text']}")
        print('─'*70)
        
        # 情感分析
        emotion_response = requests.post(
            f"{BASE_URL}/v1/emotion/analyze",
            headers=headers,
            json={"text": case["text"], "language": "zh-CN"}
        )
        
        if emotion_response.status_code == 200:
            emotion_data = emotion_response.json()["data"]
            print(f"主要情感: {emotion_data['primary_emotion']}")
            print(f"强度: {emotion_data['intensity']}")
            print(f"关键词: {', '.join(emotion_data['keywords'])}")
            print(f"需要支持: {'是' if emotion_data['needs_support'] else '否'}")


def test_response_comparison():
    """
    对比：普通回应 vs 温暖回应
    """
    scenarios = [
        {
            "user_input": "我觉得自己做不好这个任务",
            "base_ai_response": "你可以尝试分解任务，一步步完成"
        },
        {
            "user_input": "最近总是失眠，很难受",
            "base_ai_response": "建议你看医生或者试试放松技巧"
        },
        {
            "user_input": "和朋友吵架了，心情很糟",
            "base_ai_response": "沟通很重要，可以找个机会好好谈谈"
        }
    ]
    
    print("\n" + "="*70)
    print("🆚 普通回应 vs 温暖回应 对比")
    print("="*70)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'─'*70}")
        print(f"场景 {i}: {scenario['user_input']}")
        print('─'*70)
        
        payload = {
            "text": scenario["user_input"],
            "base_response": scenario["base_ai_response"],
            "user_context": {
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
            result = response.json()["data"]
            print(f"🤖 普通AI回应: {scenario['base_ai_response']}")
            print(f"💝 Warm Agent回应: {result['text']}")
            print(f"📊 温暖度提升: {result['warmth_score']:.0%}")


if __name__ == "__main__":
    print("\n" + "🔥"*35)
    print("  Warm Agent 高级功能演示")
    print("🔥"*35)
    
    # 测试1: 不同风格
    test_different_styles()
    
    # 测试2: 复杂情感
    test_complex_emotions()
    
    # 测试3: 对比测试
    test_response_comparison()
    
    print("\n" + "="*70)
    print("✅ 所有测试完成！")
    print("="*70)
