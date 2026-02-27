#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Warm Agent 关键词触发模块
包含情感词库和触发逻辑
"""

import re
from typing import List, Tuple, Optional, Dict, Any


class WarmAgentTriggers:
    """Warm Agent 关键词触发管理器"""
    
    def __init__(self):
        # 初始化情感词库
        self.emotion_words = self._load_emotion_words()
        self.need_words = self._load_need_words()
        self.intensity_words = self._load_intensity_words()
        self.physical_words = self._load_physical_words()
        self.context_words = self._load_context_words()
        
        # 关闭指令
        self.close_commands = [
            "关闭情感模式",
            "关闭warm agent",
            "关闭温暖模式", 
            "恢复正常模式",
            "退出情感支持",
            "关闭情感支持",
            "关闭温暖回应",
            "关闭情感回应"
        ]
        
        # 开启指令
        self.open_commands = [
            "开启情感模式",
            "开启warm agent",
            "开启温暖模式",
            "开启情感支持",
            "开启温暖回应"
        ]
        
        # 否定词（用于过滤）
        self.negation_words = ["不", "没", "无", "非", "未", "别", "莫", "勿"]
        
    def _load_emotion_words(self) -> Dict[str, List[str]]:
        """加载情感词库"""
        return {
            # 负面情绪
            "negative": [
                "难过", "伤心", "悲伤", "痛苦", "心痛", "心碎",
                "焦虑", "紧张", "担忧", "忧虑", "不安",
                "压力", "压抑", "沉重", "负担",
                "烦躁", "恼火", "生气", "愤怒", "气愤",
                "失望", "绝望", "沮丧", "失落",
                "孤独", "寂寞", "孤单", "孤立",
                "害怕", "恐惧", "惊恐", "恐慌", "畏惧",
                "疲惫", "疲倦", "疲劳", "累",
                "迷茫", "困惑", "疑惑", "不解",
                "愧疚", "内疚", "自责", "后悔",
                "嫉妒", "羡慕", "妒忌"
            ],
            
            # 正面情绪
            "positive": [
                "开心", "高兴", "快乐", "愉快", "喜悦",
                "兴奋", "激动", "振奋", "激昂",
                "幸福", "美满", "甜蜜", "温馨",
                "感动", "感激", "感恩", "感谢",
                "满足", "满意", "知足",
                "平静", "安宁", "宁静", "祥和",
                "自信", "自豪", "骄傲",
                "期待", "盼望", "希望", "渴望",
                "放松", "轻松", "舒畅", "舒心"
            ],
            
            # 中性/复杂情绪
            "neutral": [
                "惊讶", "惊奇", "吃惊", "诧异",
                "好奇", "兴趣", "关注",
                "犹豫", "迟疑", "纠结",
                "怀念", "思念", "想念",
                "同情", "怜悯", "心疼"
            ]
        }
    
    def _load_need_words(self) -> List[str]:
        """加载需求词"""
        return [
            "安慰", "抚慰", "慰藉",
            "支持", "鼓励", "鼓舞", "加油",
            "陪伴", "陪同", "伴随",
            "倾听", "聆听", "听听",
            "温暖", "温情", "温情",
            "情感", "情绪", "心情", "心境",
            "理解", "体谅", "体察",
            "帮助", "协助", "援助",
            "建议", "意见", "提议",
            "分享", "倾诉", "诉说"
        ]
    
    def _load_intensity_words(self) -> List[str]:
        """加载程度词"""
        return [
            "很", "非常", "特别", "极其", "极度", "极端",
            "有点", "有些", "稍微", "略微", "稍稍",
            "十分", "相当", "挺", "蛮",
            "太", "过于", "过分",
            "一点", "一些", "些许"
        ]
    
    def _load_physical_words(self) -> List[str]:
        """加载身体感受词"""
        return [
            "累", "疲惫", "疲倦", "疲劳",
            "困", "困倦", "想睡",
            "饿", "饥饿", "空腹",
            "渴", "口渴", "干渴",
            "冷", "寒冷", "冰凉",
            "热", "炎热", "闷热",
            "痛", "疼痛", "酸痛", "刺痛",
            "晕", "头晕", "眩晕",
            "恶心", "想吐", "反胃"
        ]
    
    def _load_context_words(self) -> List[str]:
        """加载上下文词"""
        return [
            "工作", "职场", "办公室", "上班",
            "学习", "考试", "功课", "作业",
            "感情", "恋爱", "爱情", "婚姻", "家庭",
            "朋友", "友谊", "友情", "人际",
            "未来", "前途", "前景", "发展",
            "过去", "回忆", "往事", "历史",
            "金钱", "财务", "经济", "收入",
            "健康", "身体", "疾病", "生病"
        ]
    
    def should_trigger_warm_mode(self, user_input: str) -> Tuple[bool, Dict[str, Any]]:
        """
        检查是否应该触发温暖模式
        
        Args:
            user_input: 用户输入文本
            
        Returns:
            Tuple[是否触发, 触发详情]
        """
        user_input_lower = user_input.lower()
        
        # 1. 检查显式开启指令
        for cmd in self.open_commands:
            if cmd in user_input:
                return True, {
                    "trigger_type": "explicit_open",
                    "trigger_word": cmd,
                    "confidence": 1.0
                }
        
        # 2. 检查显式关闭指令
        for cmd in self.close_commands:
            if cmd in user_input:
                return False, {
                    "trigger_type": "explicit_close", 
                    "trigger_word": cmd,
                    "action": "close_warm_mode"
                }
        
        # 3. 检查情感词和需求词
        found_words = []
        trigger_types = []
        
        # 检查所有情感词
        for category, words in self.emotion_words.items():
            for word in words:
                if word in user_input:
                    found_words.append(word)
                    trigger_types.append(f"emotion_{category}")
        
        # 检查需求词
        for word in self.need_words:
            if word in user_input:
                found_words.append(word)
                trigger_types.append("need")
        
        # 4. 检查否定词组合（避免误触发）
        if found_words:
            # 检查是否有否定词在情感词前面
            for word in found_words:
                word_index = user_input.find(word)
                if word_index > 0:
                    # 检查前面的字符是否包含否定词
                    preceding_text = user_input[:word_index]
                    if any(neg in preceding_text for neg in self.negation_words):
                        # 找到否定词，移除这个触发词
                        found_words.remove(word)
                        trigger_types = [t for t in trigger_types if not t.startswith("emotion_") and t != "need"]
        
        # 5. 判断是否触发
        if found_words:
            # 计算置信度（基于找到的词数量和类型）
            confidence = min(0.3 + len(found_words) * 0.2, 0.9)
            
            # 如果有程度词或上下文词，增加置信度
            for word in self.intensity_words + self.context_words:
                if word in user_input:
                    confidence = min(confidence + 0.1, 0.95)
            
            return True, {
                "trigger_type": "keyword",
                "trigger_words": found_words,
                "trigger_categories": list(set(trigger_types)),
                "confidence": confidence,
                "user_input": user_input
            }
        
        # 6. 检查身体感受词（较低优先级）
        physical_found = []
        for word in self.physical_words:
            if word in user_input:
                physical_found.append(word)
        
        if physical_found:
            return True, {
                "trigger_type": "physical_sensation",
                "trigger_words": physical_found,
                "confidence": 0.4,
                "user_input": user_input
            }
        
        # 默认不触发
        return False, {
            "trigger_type": "none",
            "confidence": 0.0,
            "user_input": user_input
        }
    
    def get_warm_response_template(self, trigger_info: Dict[str, Any]) -> str:
        """
        根据触发信息获取温暖回应模板
        
        Args:
            trigger_info: 触发详情
            
        Returns:
            温暖回应模板
        """
        trigger_type = trigger_info.get("trigger_type", "")
        trigger_words = trigger_info.get("trigger_words", [])
        
        # 根据触发类型选择模板
        if trigger_type == "explicit_open":
            return self._get_welcome_template()
        
        elif "emotion_negative" in trigger_info.get("trigger_categories", []):
            return self._get_negative_emotion_template(trigger_words)
        
        elif "emotion_positive" in trigger_info.get("trigger_categories", []):
            return self._get_positive_emotion_template(trigger_words)
        
        elif "need" in trigger_info.get("trigger_categories", []):
            return self._get_need_template(trigger_words)
        
        elif trigger_type == "physical_sensation":
            return self._get_physical_template(trigger_words)
        
        else:
            return self._get_general_warm_template()
    
    def _get_welcome_template(self) -> str:
        """欢迎模板"""
        templates = [
            "好的！温暖模式已开启～✨ 从现在开始，我会用更温暖的方式回应你，记得随时告诉我你的感受哦！",
            "情感模式启动成功！🎉 我会更加关注你的情绪和感受，用更有温度的方式陪伴你～",
            "温暖回应已激活！❤️ 我会用心倾听你的每一句话，用温暖回应你的每一个情绪～"
        ]
        import random
        return random.choice(templates)
    
    def _get_negative_emotion_template(self, trigger_words: List[str]) -> str:
        """负面情绪模板"""
        word = trigger_words[0] if trigger_words else "心情"
        
        templates = [
            f"听到你提到{word}，我也跟着有点担心呢...😔 想和我聊聊具体发生了什么吗？或者需要我给你一些温暖的小建议？",
            f"{word}的滋味确实不好受...💔 但请相信，每一次情绪波动都是成长的契机。我在这里陪着你，想说什么都可以。",
            f"感受到你的{word}情绪了...🤗 这种时候确实需要有人倾听和理解。我在这里，随时准备给你支持和陪伴～"
        ]
        import random
        return random.choice(templates)
    
    def _get_positive_emotion_template(self, trigger_words: List[str]) -> str:
        """正面情绪模板"""
        word = trigger_words[0] if trigger_words else "开心"
        
        templates = [
            f"哇！听到你{word}，我也跟着高兴起来！🎉 这种美好的时刻值得好好庆祝和分享～",
            f"真为你感到{word}！✨ 美好的情绪就像阳光，能照亮一整天～要不要和我分享更多细节？",
            f"{word}的情绪是最有感染力的！😊 看到你开心，我也觉得世界变得更美好了呢～"
        ]
        import random
        return random.choice(templates)
    
    def _get_need_template(self, trigger_words: List[str]) -> str:
        """需求词模板"""
        word = trigger_words[0] if trigger_words else "支持"
        
        templates = [
            f"感受到你需要{word}了...🤗 我在这里，随时准备给你最温暖的{word}和陪伴～",
            f"需要{word}的时候，记得我永远在这里～❤️ 无论是倾听、建议还是简单的陪伴，我都会用心对待。",
            f"{word}已就位！✨ 我会用最温暖的方式回应你的每一个需求，让你感受到被理解和关怀～"
        ]
        import random
        return random.choice(templates)
    
    def _get_physical_template(self, trigger_words: List[str]) -> str:
        """身体感受模板"""
        word = trigger_words[0] if trigger_words else "累"
        
        templates = [
            f"听起来你身体有点{word}呢...💤 身体是革命的本钱，要好好照顾自己哦！需要休息的建议吗？",
            f"感受到你的身体{word}了...🛌 这种时候最适合放松和恢复。要不要试试一些简单的放松方法？",
            f"{word}的时候确实需要格外关爱自己呢...🌿 我在这里陪你，一起找到最适合的恢复方式～"
        ]
        import random
        return random.choice(templates)
    
    def _get_general_warm_template(self) -> str:
        """通用温暖模板"""
        templates = [
            "我在这里用心倾听～✨ 无论你想分享什么，我都会用最温暖的方式回应你～",
            "感受到你想和我连接的心意了...❤️ 我会用全部的关注和温暖来回应你～",
            "欢迎来到温暖空间～🌼 在这里，每一个字都会被温柔对待，每一种情绪都会被理解～"
        ]
        import random
        return random.choice(templates)


# 单例实例
_warm_agent_triggers = None

def get_warm_agent_triggers() -> WarmAgentTriggers:
    """获取Warm Agent触发器单例"""
    global _warm_agent_triggers
    if _warm_agent_triggers is None:
        _warm_agent_triggers = WarmAgentTriggers()
    return _warm_agent_triggers


if __name__ == "__main__":
    # 测试代码
    triggers = WarmAgentTriggers()
    
    test_cases = [
        "今天工作压力好大",
        "我有点难过",
        "需要一些安慰",
        "今天很开心！",
        "我不难过，只是有点累",
        "关闭情感模式",
        "开启温暖模式"
    ]
    
    for test in test_cases:
        should_trigger, info = triggers.should_trigger_warm_mode(test)
        print(f"输入: {test}")
        print(f"触发: {should_trigger}")
        print(f"详情: {info}")
        if should_trigger and info.get("trigger_type") not in ["explicit_close", "explicit_open"]:
            template = triggers.get_warm_response_template(info)
            print(f"模板: {template}")
        print("-" * 50)