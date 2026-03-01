#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心模块测试
测试情感分析引擎和温暖回应引擎
"""

import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.emotion_analyzer import EmotionAnalyzer, EmotionResult
from src.core.warm_response_engine import WarmResponseEngine, WarmResponse
from src.core.triggers import WarmAgentTriggers


class TestEmotionAnalyzer:
    """情感分析器测试"""
    
    @pytest.fixture
    def analyzer(self):
        return EmotionAnalyzer()
    
    def test_analyze_positive_emotion(self, analyzer):
        """测试正面情感分析"""
        text = "今天很开心！"
        result = analyzer.analyze(text)
        
        assert result.primary_emotion == "happiness"
        assert result.intensity > 0.5
        assert "开心" in result.keywords
        assert result.confidence > 0.7
        assert result.needs_support is False
    
    def test_analyze_negative_emotion(self, analyzer):
        """测试负面情感分析"""
        text = "工作压力好大"
        result = analyzer.analyze(text)
        
        assert result.primary_emotion in ["anxiety", "stress", "fear"]
        assert result.intensity > 0.6
        assert "压力" in result.keywords
        assert result.needs_support is True
    
    def test_analyze_with_negation(self, analyzer):
        """测试否定词处理"""
        text = "我不难过"
        result = analyzer.analyze(text)
        
        # 应该检测到否定，不触发负面情感
        assert result.primary_emotion != "sadness"
        assert result.intensity < 0.3
    
    def test_analyze_empty_text(self, analyzer):
        """测试空文本"""
        text = ""
        result = analyzer.analyze(text)
        
        assert result.primary_emotion == "neutral"
        assert result.intensity == 0.0
        assert result.confidence == 0.0
    
    def test_analyze_needs_detection(self, analyzer):
        """测试需求检测"""
        text = "需要安慰"
        result = analyzer.analyze(text)
        
        assert result.needs_support is True
        assert "安慰" in result.keywords
    
    @pytest.mark.parametrize("text,expected_emotion", [
        ("我很难过", "sadness"),
        ("我很高兴", "happiness"),
        ("我有点焦虑", "fear"),
        ("需要安慰", "sadness"),  # 需求词会映射到相关情感
        ("今天特别兴奋", "happiness"),
        ("对未来感到恐惧", "fear"),
    ])
    def test_multiple_emotions(self, analyzer, text, expected_emotion):
        """测试多种情感"""
        result = analyzer.analyze(text)
        assert result.primary_emotion == expected_emotion
    
    def test_context_analysis(self, analyzer):
        """测试上下文分析"""
        text = "工作压力大"
        context = {
            "previous_emotions": ["anxiety", "stress"],
            "time_of_day": "morning"
        }
        
        result = analyzer.analyze(text, context)
        
        assert "work" in result.context_hints
        assert result.intensity > 0.5


class TestWarmResponseEngine:
    """温暖回应引擎测试"""
    
    @pytest.fixture
    def engine(self):
        return WarmResponseEngine()
    
    @pytest.fixture
    def emotion_result(self):
        return EmotionResult(
            primary_emotion="sadness",
            secondary_emotions=["loneliness"],
            intensity=0.75,
            confidence=0.85,
            keywords=["难过"],
            context_hints=["work"],
            needs_support=True,
            suggested_response="听到你难过，我也跟着担心..."
        )
    
    def test_generate_warm_response(self, engine, emotion_result):
        """测试生成温暖回应"""
        response = engine.generate(emotion_result)
        
        assert isinstance(response, WarmResponse)
        assert response.text
        assert response.emotion == "sadness"
        assert response.warmth_score > 0.0
        assert response.warmth_score <= 1.0
    
    def test_generate_with_base_response(self, engine, emotion_result):
        """测试带基础回应的生成"""
        base_response = "建议你休息一下"
        response = engine.generate(
            emotion_result=emotion_result,
            base_response=base_response
        )
        
        assert base_response in response.text
        assert response.warmth_score > 0.3
    
    def test_generate_with_user_context(self, engine, emotion_result):
        """测试带用户上下文的生成"""
        user_context = {
            "preferences": {
                "style": "professional",
                "emoji_level": "none"
            }
        }
        
        response = engine.generate(
            emotion_result=emotion_result,
            user_context=user_context
        )
        
        # 专业风格应该没有表情符号
        assert not any(ord(char) > 10000 for char in response.text)
    
    def test_warmth_score_calculation(self, engine):
        """测试温暖度分数计算"""
        test_responses = [
            "我理解你的感受...❤️",
            "建议休息",
            "听到你难过，我也跟着担心...😔 我会一直陪着你✨"
        ]
        
        for response_text in test_responses:
            # 创建一个临时的WarmResponse来测试分数计算
            # 这里我们直接调用私有方法（在实际测试中可能需要重构）
            score = engine._calculate_warmth_score(response_text)
            assert 0.0 <= score <= 1.0
    
    def test_personalization(self, engine, emotion_result):
        """测试个性化适配"""
        user_context = {
            "preferences": {
                "style": "warm",
                "emoji_level": "high",
                "warmth_intensity": 0.9
            },
            "time_of_day": "evening"
        }
        
        response = engine.generate(
            emotion_result=emotion_result,
            user_context=user_context
        )
        
        # 高温暖度应该有更多个性化元素
        assert len(response.personalized_elements) > 0
        assert response.warmth_score > 0.5


class TestWarmAgentTriggers:
    """Warm Agent触发器测试"""
    
    @pytest.fixture
    def triggers(self):
        return WarmAgentTriggers()
    
    def test_trigger_positive(self, triggers):
        """测试正面触发"""
        text = "今天很难过"
        should_trigger, info = triggers.should_trigger_warm_mode(text)
        
        assert should_trigger is True
        assert info["trigger_type"] == "keyword"
        assert "难过" in info.get("trigger_words", [])
    
    def test_trigger_negative(self, triggers):
        """测试负面触发（不应该触发）"""
        text = "今天天气不错"
        should_trigger, info = triggers.should_trigger_warm_mode(text)
        
        assert should_trigger is False
    
    def test_explicit_open_command(self, triggers):
        """测试显式开启指令"""
        text = "开启情感模式"
        should_trigger, info = triggers.should_trigger_warm_mode(text)
        
        assert should_trigger is True
        assert info["trigger_type"] == "explicit_open"
    
    def test_explicit_close_command(self, triggers):
        """测试显式关闭指令"""
        text = "关闭情感模式"
        should_trigger, info = triggers.should_trigger_warm_mode(text)
        
        assert should_trigger is False
        assert info["trigger_type"] == "explicit_close"
    
    def test_negation_handling(self, triggers):
        """测试否定词处理"""
        text = "我不难过"
        should_trigger, info = triggers.should_trigger_warm_mode(text)
        
        # 有否定词，不应该触发
        assert should_trigger is False
    
    def test_need_words_trigger(self, triggers):
        """测试需求词触发"""
        text = "需要安慰"
        should_trigger, info = triggers.should_trigger_warm_mode(text)
        
        assert should_trigger is True
        assert "need" in info.get("trigger_categories", [])
    
    def test_physical_sensation_trigger(self, triggers):
        """测试身体感受触发"""
        text = "有点累"
        should_trigger, info = triggers.should_trigger_warm_mode(text)
        
        assert should_trigger is True
        assert info["trigger_type"] == "physical_sensation"
    
    def test_get_warm_response_template(self, triggers):
        """测试获取温暖回应模板"""
        trigger_info = {
            "trigger_type": "keyword",
            "trigger_words": ["难过"],
            "trigger_categories": ["emotion_negative"]
        }
        
        template = triggers.get_warm_response_template(trigger_info)
        assert template
        assert isinstance(template, str)
        assert len(template) > 0


if __name__ == "__main__":
    """运行测试"""
    print("运行核心模块测试...")
    
    # 创建测试实例
    analyzer = EmotionAnalyzer()
    engine = WarmResponseEngine()
    triggers = WarmAgentTriggers()
    
    # 测试情感分析器
    print("\n=== 测试情感分析器 ===")
    test_texts = [
        "今天很开心！",
        "工作压力好大",
        "需要安慰",
        "我不难过"
    ]
    
    for text in test_texts:
        result = analyzer.analyze(text)
        print(f"\n输入: {text}")
        print(f"情感: {result.primary_emotion} (强度: {result.intensity})")
        print(f"关键词: {result.keywords}")
        print(f"需要支持: {result.needs_support}")
    
    # 测试温暖回应引擎
    print("\n=== 测试温暖回应引擎 ===")
    emotion_result = analyzer.analyze("今天很难过")
    response = engine.generate(
        emotion_result=emotion_result,
        base_response="建议你休息一下"
    )
    
    print(f"情感: {emotion_result.primary_emotion}")
    print(f"温暖回应: {response.text}")
    print(f"温暖度分数: {response.warmth_score:.2f}")
    
    # 测试触发器
    print("\n=== 测试触发器 ===")
    test_inputs = [
        "开启情感模式",
        "今天很难过",
        "需要安慰",
        "关闭情感模式"
    ]
    
    for text in test_inputs:
        should_trigger, info = triggers.should_trigger_warm_mode(text)
        print(f"\n输入: {text}")
        print(f"触发: {should_trigger}")
        print(f"类型: {info.get('trigger_type')}")
        
        if should_trigger and info.get("trigger_type") not in ["explicit_close"]:
            template = triggers.get_warm_response_template(info)
            print(f"模板: {template}")
    
    print("\n✅ 所有测试完成！")