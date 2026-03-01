#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 集成模块
提供与OpenClaw的无缝集成
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from ..core.emotion_analyzer import get_emotion_analyzer, EmotionResult
from ..core.warm_response_engine import get_warm_response_engine, WarmResponse
from ..core.triggers import get_warm_agent_triggers


@dataclass
class OpenClawMessage:
    """OpenClaw消息"""
    content: str
    base_response: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class OpenClawContext:
    """OpenClaw上下文"""
    user_id: str
    channel: str
    user_context: Dict[str, Any] = None
    session_id: str = None
    
    def __post_init__(self):
        if self.user_context is None:
            self.user_context = {}


@dataclass
class ProcessedMessage:
    """处理后的消息"""
    original: OpenClawMessage
    enhanced_response: str
    emotion_data: EmotionResult
    should_enhance: bool
    enhancement_metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.enhancement_metadata is None:
            self.enhancement_metadata = {}


class OpenClawIntegration:
    """
    OpenClaw 集成
    提供与OpenClaw的无缝集成
    """
    
    def __init__(self, config: Dict):
        """
        初始化集成
        
        Args:
            config: 配置字典
        """
        self.config = config
        
        # 初始化核心组件
        self.emotion_analyzer = get_emotion_analyzer()
        self.warm_engine = get_warm_response_engine()
        self.triggers = get_warm_agent_triggers()
        
        # OpenClaw特定配置
        self.skill_config = config.get("openclaw", {})
        self.auto_detect = self.skill_config.get("auto_detect", True)
        self.enhance_all = self.skill_config.get("enhance_all", False)
        self.default_warm_mode = self.skill_config.get("default_warm_mode", False)
        
        # 用户状态管理
        self.user_states = {}  # user_id -> UserState
        
        print(f"✅ OpenClaw集成初始化完成")
        print(f"   自动检测: {self.auto_detect}")
        print(f"   增强所有: {self.enhance_all}")
        print(f"   默认温暖模式: {self.default_warm_mode}")
    
    def process_message(self,
                       message: OpenClawMessage,
                       context: OpenClawContext) -> ProcessedMessage:
        """
        处理OpenClaw消息
        
        Args:
            message: OpenClaw消息
            context: OpenClaw上下文
            
        Returns:
            ProcessedMessage: 处理后的消息
        """
        user_id = context.user_id
        
        # 1. 获取或创建用户状态
        user_state = self._get_user_state(user_id)
        
        # 2. 检查显式指令
        explicit_command = self._check_explicit_command(message.content)
        if explicit_command is not None:
            return self._process_explicit_command(
                message, context, user_state, explicit_command
            )
        
        # 3. 情感分析
        emotion_result = self.emotion_analyzer.analyze(
            message.content,
            context=context.user_context
        )
        
        # 4. 检查是否应该触发温暖模式
        should_enhance = self._should_enhance_response(
            message, emotion_result, context, user_state
        )
        
        # 5. 生成温暖回应
        if should_enhance:
            warm_response = self.warm_engine.generate(
                emotion_result=emotion_result,
                base_response=message.base_response,
                user_context=context.user_context
            )
            
            # 6. 更新用户状态
            self._update_user_state(user_state, {
                "last_emotion": emotion_result.primary_emotion,
                "last_intensity": emotion_result.intensity,
                "warm_mode": True,
                "last_interaction": datetime.utcnow().isoformat()
            })
            
            # 7. 记录交互（实际实现中会存储到数据库）
            self._record_interaction(user_id, message, emotion_result, warm_response)
            
            return ProcessedMessage(
                original=message,
                enhanced_response=warm_response.text,
                emotion_data=emotion_result,
                should_enhance=True,
                enhancement_metadata={
                    "warmth_score": warm_response.warmth_score,
                    "personalized": warm_response.personalized_elements,
                    "enhancement_details": warm_response.enhancement_details
                }
            )
        else:
            # 不增强，返回原始回应
            self._update_user_state(user_state, {
                "warm_mode": False,
                "last_interaction": datetime.utcnow().isoformat()
            })
            
            return ProcessedMessage(
                original=message,
                enhanced_response=message.base_response,
                emotion_data=emotion_result,
                should_enhance=False
            )
    
    def _get_user_state(self, user_id: str) -> Dict:
        """获取用户状态"""
        if user_id not in self.user_states:
            # 初始化用户状态
            self.user_states[user_id] = {
                "warm_mode": self.default_warm_mode,
                "preferences": self._get_default_preferences(),
                "interaction_count": 0,
                "last_interaction": None,
                "emotion_history": []
            }
        
        return self.user_states[user_id]
    
    def _get_default_preferences(self) -> Dict:
        """获取默认偏好"""
        return {
            "style": "balanced",
            "emoji_level": "moderate",
            "warmth_intensity": 0.7,
            "language": "zh-CN",
            "always_warm": False
        }
    
    def _check_explicit_command(self, text: str) -> Optional[str]:
        """检查显式指令"""
        open_commands = ["开启情感模式", "warm agent", "温暖模式", "开启温暖模式"]
        close_commands = ["关闭情感模式", "关闭温暖模式", "恢复正常模式", "退出情感支持"]
        
        for cmd in open_commands:
            if cmd in text:
                return "open"
        
        for cmd in close_commands:
            if cmd in text:
                return "close"
        
        return None
    
    def _process_explicit_command(self,
                                 message: OpenClawMessage,
                                 context: OpenClawContext,
                                 user_state: Dict,
                                 command: str) -> ProcessedMessage:
        """处理显式指令"""
        user_id = context.user_id
        
        if command == "open":
            # 开启温暖模式
            self._update_user_state(user_state, {
                "warm_mode": True,
                "last_interaction": datetime.utcnow().isoformat()
            })
            
            response = "✅ 好的，温暖模式已开启！✨ 从现在开始，我会用更温暖的方式回应你～"
            
            return ProcessedMessage(
                original=message,
                enhanced_response=response,
                emotion_data=EmotionResult(
                    primary_emotion="neutral",
                    secondary_emotions=[],
                    intensity=0.0,
                    confidence=0.0,
                    keywords=[],
                    context_hints=[],
                    needs_support=False,
                    suggested_response=response
                ),
                should_enhance=True,
                enhancement_metadata={
                    "command_processed": "open_warm_mode",
                    "warmth_score": 0.8
                }
            )
        
        else:  # command == "close"
            # 关闭温暖模式
            self._update_user_state(user_state, {
                "warm_mode": False,
                "last_interaction": datetime.utcnow().isoformat()
            })
            
            response = "✅ 好的，情感模式已关闭。需要的时候随时说'开启情感模式'或使用情感词触发哦！😊"
            
            return ProcessedMessage(
                original=message,
                enhanced_response=response,
                emotion_data=EmotionResult(
                    primary_emotion="neutral",
                    secondary_emotions=[],
                    intensity=0.0,
                    confidence=0.0,
                    keywords=[],
                    context_hints=[],
                    needs_support=False,
                    suggested_response=response
                ),
                should_enhance=False,
                enhancement_metadata={
                    "command_processed": "close_warm_mode"
                }
            )
    
    def _should_enhance_response(self,
                                message: OpenClawMessage,
                                emotion_result: EmotionResult,
                                context: OpenClawContext,
                                user_state: Dict) -> bool:
        """
        判断是否应该增强回应
        
        Args:
            message: OpenClaw消息
            emotion_result: 情感分析结果
            context: OpenClaw上下文
            user_state: 用户状态
            
        Returns:
            bool: 是否应该增强
        """
        # 1. 如果配置为增强所有回应
        if self.enhance_all:
            return True
        
        # 2. 如果用户处于温暖模式
        if user_state.get("warm_mode", False):
            return True
        
        # 3. 如果用户偏好总是温暖
        preferences = user_state.get("preferences", {})
        if preferences.get("always_warm", False):
            return True
        
        # 4. 检查情感触发
        if self.auto_detect:
            # 使用关键词触发器
            should_trigger, trigger_info = self.triggers.should_trigger_warm_mode(
                message.content
            )
            
            if should_trigger:
                # 触发温暖模式
                self._update_user_state(user_state, {"warm_mode": True})
                return True
        
        # 5. 检查情感分析结果
        if emotion_result.confidence > 0.5 and emotion_result.intensity > 0.3:
            # 情感明确且强度足够
            return True
        
        # 6. 检查是否需要支持
        if emotion_result.needs_support:
            return True
        
        return False
    
    def _update_user_state(self, user_state: Dict, updates: Dict):
        """更新用户状态"""
        user_state.update(updates)
        
        # 更新交互计数
        if "interaction_count" in user_state:
            user_state["interaction_count"] += 1
        
        # 更新情感历史
        if "last_emotion" in updates:
            emotion = updates["last_emotion"]
            intensity = updates.get("last_intensity", 0.0)
            
            if "emotion_history" not in user_state:
                user_state["emotion_history"] = []
            
            user_state["emotion_history"].append({
                "emotion": emotion,
                "intensity": intensity,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # 只保留最近50条记录
            if len(user_state["emotion_history"]) > 50:
                user_state["emotion_history"] = user_state["emotion_history"][-50:]
    
    def _record_interaction(self,
                           user_id: str,
                           message: OpenClawMessage,
                           emotion_result: EmotionResult,
                           warm_response: WarmResponse):
        """记录交互（模拟实现）"""
        # 在实际实现中，这里会存储到数据库
        interaction = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "user_input": message.content,
            "emotion_data": emotion_result.to_dict(),
            "response": warm_response.text,
            "metadata": message.metadata
        }
        
        # 这里只是打印，实际实现中会存储
        print(f"📝 记录交互: {json.dumps(interaction, ensure_ascii=False, indent=2)}")
    
    def get_user_summary(self, user_id: str) -> Dict:
        """获取用户摘要"""
        if user_id not in self.user_states:
            return {"error": "User not found"}
        
        user_state = self.user_states[user_id]
        
        # 分析情感历史
        emotion_history = user_state.get("emotion_history", [])
        if emotion_history:
            emotions = [e["emotion"] for e in emotion_history]
            intensities = [e["intensity"] for e in emotion_history]
            
            from collections import Counter
            emotion_counter = Counter(emotions)
            
            summary = {
                "user_id": user_id,
                "total_interactions": user_state.get("interaction_count", 0),
                "warm_mode": user_state.get("warm_mode", False),
                "most_common_emotion": emotion_counter.most_common(1)[0] if emotion_counter else None,
                "average_intensity": sum(intensities) / len(intensities) if intensities else 0,
                "recent_emotions": emotions[-10:] if len(emotions) > 10 else emotions,
                "last_interaction": user_state.get("last_interaction"),
                "preferences": user_state.get("preferences", {})
            }
        else:
            summary = {
                "user_id": user_id,
                "total_interactions": user_state.get("interaction_count", 0),
                "warm_mode": user_state.get("warm_mode", False),
                "message": "暂无情感记录",
                "last_interaction": user_state.get("last_interaction"),
                "preferences": user_state.get("preferences", {})
            }
        
        return summary
    
    def update_user_preferences(self, user_id: str, preferences: Dict) -> Dict:
        """更新用户偏好"""
        if user_id not in self.user_states:
            return {"error": "User not found"}
        
        user_state = self.user_states[user_id]
        
        # 合并偏好
        current_preferences = user_state.get("preferences", {})
        current_preferences.update(preferences)
        user_state["preferences"] = current_preferences
        
        return {
            "success": True,
            "user_id": user_id,
            "updated_preferences": current_preferences
        }


# 单例实例
_openclaw_integration = None

def get_openclaw_integration(config: Dict = None) -> OpenClawIntegration:
    """获取OpenClaw集成单例"""
    global _openclaw_integration
    if _openclaw_integration is None:
        if config is None:
            config = {
                "openclaw": {
                    "auto_detect": True,
                    "enhance_all": False,
                    "default_warm_mode": False
                }
            }
        _openclaw_integration = OpenClawIntegration(config)
    return _openclaw_integration


if __name__ == "__main__":
    """测试代码"""
    print("=" * 60)
    print("OpenClaw集成测试")
    print("=" * 60)
    
    # 创建集成实例
    config = {
        "openclaw": {
            "auto_detect": True,
            "enhance_all": False,
            "default_warm_mode": False
        }
    }
    
    integration = OpenClawIntegration(config)
    
    # 测试用例
    test_cases = [
        {
            "message": OpenClawMessage(
                content="今天工作压力好大",
                base_response="建议你休息一下"
            ),
            "context": OpenClawContext(
                user_id="test_user_1",
                channel="qqbot",
                user_context={
                    "preferences": {
                        "style": "warm",
                        "emoji_level": "moderate"
                    }
                }
            )
        },
        {
            "message": OpenClawMessage(
                content="开启情感模式",
                base_response="好的"
            ),
            "context": OpenClawContext(
                user_id="test_user_2",
                channel="qqbot"
            )
        },
        {
            "message": OpenClawMessage(
                content="我很难过",
                base_response="难过的时候可以找朋友聊聊天"
            ),
            "context": OpenClawContext(
                user_id="test_user_1",
                channel="qqbot"
            )
        },
        {
            "message": OpenClawMessage(
                content="关闭情感模式",
                base_response="好的"
            ),
            "context": OpenClawContext(
                user_id="test_user_2",
                channel="qqbot"
            )
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}:")
        print(f"用户: {test_case['context'].user_id}")
        print(f"输入: {test_case['message'].content}")
        print(f"基础回应: {test_case['message'].base_response}")
        
        # 处理消息
        result = integration.process_message(
            test_case['message'],
            test_case['context']
        )
        
        print(f"是否增强: {result.should_enhance}")
        print(f"最终回应: {result.enhanced_response}")
        print(f"主要情感: {result.emotion_data.primary_emotion}")
        
        if result.should_enhance:
            print(f"温暖度分数: {result.enhancement_metadata.get('warmth_score', 'N/A')}")
        
        print("-" * 40)
    
    # 获取用户摘要
    print("\n📊 用户摘要:")
    for user_id in ["test_user_1", "test_user_2"]:
        summary = integration.get_user_summary(user_id)
        print(f"\n用户 {user_id}:")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    
    print("\n✅ 测试完成！")