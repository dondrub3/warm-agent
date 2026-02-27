#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Warm Agent OpenClaw 集成示例
演示如何在OpenClaw中集成Warm Agent
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

# 假设的Warm Agent客户端
class WarmAgentClient:
    """Warm Agent API客户端（简化版）"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.warm-agent.com/v1"
        
    def analyze_emotion(self, text: str) -> Dict[str, Any]:
        """分析情感"""
        # 实际实现中会调用API
        return {
            "primary_emotion": "anxiety",
            "intensity": 0.85,
            "keywords": ["压力", "焦虑"]
        }
    
    def generate_warm_response(self, user_input: str, base_response: str) -> str:
        """生成温暖回应"""
        # 实际实现中会调用API
        return f"听起来你今天工作很辛苦呢...💼 {base_response} 我在这里陪着你✨"


class OpenClawWarmAgentSkill:
    """
    OpenClaw Warm Agent 技能
    集成到OpenClaw的AI助手中
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化技能
        
        Args:
            config: 配置字典，包含api_key等
        """
        self.config = config
        self.api_key = config.get("api_key", "")
        self.auto_enhance = config.get("auto_enhance", True)
        self.warm_mode = config.get("warm_mode", False)
        
        # 初始化客户端
        self.client = WarmAgentClient(self.api_key)
        
        # 情感记忆存储
        self.emotion_memory = {}
        
        # 加载关键词触发器
        from src.core.triggers import get_warm_agent_triggers
        self.triggers = get_warm_agent_triggers()
        
        print(f"✅ Warm Agent技能初始化完成")
        print(f"   自动增强: {self.auto_enhance}")
        print(f"   温暖模式: {self.warm_mode}")
    
    def process_message(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理用户消息
        
        Args:
            user_input: 用户输入
            context: 对话上下文
            
        Returns:
            处理结果
        """
        if context is None:
            context = {}
        
        # 1. 检查是否应该触发温暖模式
        should_trigger, trigger_info = self.triggers.should_trigger_warm_mode(user_input)
        
        # 2. 处理关闭指令
        if trigger_info.get("trigger_type") == "explicit_close":
            self.warm_mode = False
            return {
                "action": "respond",
                "response": "✅ 好的，情感模式已关闭。需要的时候随时说'开启情感模式'或使用情感词触发哦！😊",
                "warm_mode": False,
                "trigger_info": trigger_info
            }
        
        # 3. 处理开启指令
        if trigger_info.get("trigger_type") == "explicit_open":
            self.warm_mode = True
            template = self.triggers.get_warm_response_template(trigger_info)
            return {
                "action": "respond",
                "response": template,
                "warm_mode": True,
                "trigger_info": trigger_info
            }
        
        # 4. 如果检测到关键词触发，开启温暖模式
        if should_trigger and not self.warm_mode:
            self.warm_mode = True
            print(f"🔔 检测到关键词触发，开启温暖模式: {trigger_info}")
        
        # 5. 如果处于温暖模式，进行情感分析
        emotion_data = None
        if self.warm_mode:
            emotion_data = self.client.analyze_emotion(user_input)
            
            # 存储情感记忆
            user_id = context.get("user_id", "default")
            self._store_emotion_memory(user_id, user_input, emotion_data)
        
        return {
            "action": "enhance_response" if self.warm_mode else "pass_through",
            "user_input": user_input,
            "emotion_data": emotion_data,
            "warm_mode": self.warm_mode,
            "trigger_info": trigger_info if should_trigger else None
        }
    
    def enhance_response(self, base_response: str, processing_result: Dict[str, Any]) -> str:
        """
        增强AI回应
        
        Args:
            base_response: 基础AI回应
            processing_result: 处理结果
            
        Returns:
            增强后的温暖回应
        """
        if not processing_result.get("warm_mode", False):
            return base_response
        
        user_input = processing_result.get("user_input", "")
        emotion_data = processing_result.get("emotion_data")
        trigger_info = processing_result.get("trigger_info")
        
        # 如果有触发信息，使用对应的模板
        if trigger_info:
            template = self.triggers.get_warm_response_template(trigger_info)
            # 将基础回应融入模板
            enhanced = template.replace("。", f"。{base_response}")
            return enhanced
        
        # 否则使用API生成温暖回应
        try:
            warm_response = self.client.generate_warm_response(user_input, base_response)
            return warm_response
        except Exception as e:
            print(f"⚠️ 生成温暖回应失败: {e}")
            # 失败时返回基础回应，但添加温暖前缀
            return f"我理解你的感受...🤗 {base_response}"
    
    def _store_emotion_memory(self, user_id: str, user_input: str, emotion_data: Dict[str, Any]):
        """存储情感记忆"""
        if user_id not in self.emotion_memory:
            self.emotion_memory[user_id] = []
        
        memory_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "emotion_data": emotion_data,
            "primary_emotion": emotion_data.get("primary_emotion"),
            "intensity": emotion_data.get("intensity", 0)
        }
        
        self.emotion_memory[user_id].append(memory_entry)
        
        # 只保留最近50条记录
        if len(self.emotion_memory[user_id]) > 50:
            self.emotion_memory[user_id] = self.emotion_memory[user_id][-50:]
    
    def get_emotion_summary(self, user_id: str = "default") -> Dict[str, Any]:
        """获取情感摘要"""
        if user_id not in self.emotion_memory:
            return {"message": "暂无情感记录"}
        
        memories = self.emotion_memory[user_id]
        if not memories:
            return {"message": "暂无情感记录"}
        
        # 分析情感模式
        emotions = [m["primary_emotion"] for m in memories if m["primary_emotion"]]
        intensities = [m["intensity"] for m in memories]
        
        from collections import Counter
        emotion_counter = Counter(emotions)
        
        return {
            "total_interactions": len(memories),
            "most_common_emotion": emotion_counter.most_common(1)[0] if emotion_counter else None,
            "average_intensity": sum(intensities) / len(intensities) if intensities else 0,
            "recent_emotions": emotions[-10:] if len(emotions) > 10 else emotions,
            "last_interaction": memories[-1]["timestamp"] if memories else None
        }


# OpenClaw配置示例
OPENCLAW_CONFIG = {
    "skills": {
        "warm-agent": {
            "enabled": True,
            "apiKey": "wa_free_xxxxxxxxxxxx",  # 替换为你的API Key
            "autoEnhance": True,
            "defaultWarmMode": False,
            "personality": {
                "style": "caring",
                "emojiLevel": "moderate",
                "warmthIntensity": 0.7
            }
        }
    }
}


def main():
    """主函数 - 演示集成效果"""
    print("=" * 60)
    print("Warm Agent OpenClaw 集成演示")
    print("=" * 60)
    
    # 1. 初始化技能
    config = {
        "api_key": "demo_key",
        "auto_enhance": True,
        "warm_mode": False
    }
    
    skill = OpenClawWarmAgentSkill(config)
    
    # 2. 测试对话
    test_conversations = [
        {
            "user": "今天工作压力好大",
            "ai_base": "建议你休息一下，听听音乐放松"
        },
        {
            "user": "我有点难过",
            "ai_base": "难过的时候可以找朋友聊聊天"
        },
        {
            "user": "关闭情感模式",
            "ai_base": "好的"
        },
        {
            "user": "今天很开心！",
            "ai_base": "为你感到高兴"
        },
        {
            "user": "开启温暖模式",
            "ai_base": "模式已切换"
        }
    ]
    
    for conv in test_conversations:
        print(f"\n👤 用户: {conv['user']}")
        
        # 处理用户消息
        result = skill.process_message(conv['user'])
        
        print(f"🔧 处理结果:")
        print(f"   温暖模式: {result.get('warm_mode')}")
        print(f"   触发类型: {result.get('trigger_info', {}).get('trigger_type', 'none')}")
        
        # 增强回应
        enhanced_response = skill.enhance_response(conv['ai_base'], result)
        
        print(f"🤖 AI基础回应: {conv['ai_base']}")
        print(f"❤️ 温暖增强后: {enhanced_response}")
        print("-" * 50)
    
    # 3. 显示情感摘要
    print("\n📊 情感记忆摘要:")
    summary = skill.get_emotion_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()