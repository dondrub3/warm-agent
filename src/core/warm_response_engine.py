"""
温暖回应引擎 - Warm Agent核心模块

基于情感分析结果生成有温度、有同理心的回应。
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import random
import re

from .emotion_analyzer import EmotionResult


@dataclass
class WarmResponse:
    """温暖回应结果"""
    text: str
    warmth_score: float
    style: str
    personalized_elements: List[str]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "text": self.text,
            "warmth_score": self.warmth_score,
            "style": self.style,
            "personalized_elements": self.personalized_elements
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "WarmResponse":
        """从字典创建"""
        return cls(
            text=data.get("text", ""),
            warmth_score=data.get("warmth_score", 0.0),
            style=data.get("style", "balanced"),
            personalized_elements=data.get("personalized_elements", [])
        )


class WarmResponseEngine:
    """温暖回应引擎"""
    
    # 同理心开场白
    EMPATHY_OPENERS = {
        "sadness": [
            "听到你这样说，我也感到很难过...",
            "能感受到你的心情，这确实不容易...",
            "理解你的感受，这种时刻确实需要支持..."
        ],
        "anger": [
            "换作是我也会感到很生气...",
            "理解你的愤怒，这确实让人恼火...",
            "能感受到你的不满，这种经历确实不好受..."
        ],
        "anxiety": [
            "焦虑的感觉确实很难受...",
            "理解你的担心，这种不确定性确实让人不安...",
            "能感受到你的紧张，这种感觉我懂..."
        ],
        "fear": [
            "害怕是正常的反应...",
            "理解你的恐惧，这种时候确实需要勇气...",
            "能感受到你的不安，你不是一个人..."
        ],
        "joy": [
            "听到这个好消息，我也为你感到开心！",
            "真替你高兴！",
            "能感受到你的喜悦，这真是太棒了！"
        ],
        "surprise": [
            "哇，这确实让人意外！",
            "听到这个消息，我也感到很吃惊！",
            "这确实出乎意料！"
        ],
        "neutral": [
            "我在用心倾听...",
            "理解你的想法...",
            "感受到你想表达的..."
        ]
    }
    
    # 安慰和支持语句
    SUPPORT_CLOSERS = {
        "sadness": [
            "记住，我一直在这里陪着你。",
            "需要倾诉的话，我随时都在。",
            "相信一切都会好起来的，加油！"
        ],
        "anger": [
            "深呼吸，一切都会过去的。",
            "保持冷静，你比想象中更强大。",
            "发泄出来会好受一些，我支持你。"
        ],
        "anxiety": [
            "慢慢来，一步一步会好起来的。",
            "相信自己，你有能力面对这一切。",
            "深呼吸，当下就是最好的时刻。"
        ],
        "fear": [
            "你很勇敢，我相信你能克服。",
            "不管发生什么，我都会支持你。",
            "恐惧只是暂时的，勇气才是永恒的。"
        ],
        "joy": [
            "继续保持这份美好心情！",
            "让快乐一直延续下去吧！",
            "享受这美好的时刻！"
        ],
        "neutral": [
            "有什么想聊的，我都在。",
            "愿意分享更多吗？",
            "我在这里陪着你。"
        ]
    }
    
    # 风格模板
    STYLE_TEMPLATES = {
        "warm": {
            "prefix": "",
            "suffix": "",
            "emoji_level": "moderate"
        },
        "professional": {
            "prefix": "",
            "suffix": "",
            "emoji_level": "low"
        },
        "casual": {
            "prefix": "",
            "suffix": "",
            "emoji_level": "high"
        },
        "balanced": {
            "prefix": "",
            "suffix": "",
            "emoji_level": "moderate"
        }
    }
    
    # 表情符号映射
    EMOJI_MAP = {
        "joy": ["😊", "✨", "🎉", "💖", "🌟"],
        "sadness": ["😢", "💙", "🫂", "🌙", "💫"],
        "anger": ["😤", "💪", "🔥", "⚡", "🌊"],
        "anxiety": ["😰", "🌸", "💆", "🍃", "🌱"],
        "fear": ["😨", "💪", "🛡️", "✨", "🌟"],
        "surprise": ["😲", "✨", "🎊", "💫", "🌟"],
        "love": ["❤️", "💖", "💕", "✨", "🌹"],
        "gratitude": ["🙏", "💝", "✨", "🌟", "💫"],
        "loneliness": ["🌙", "💫", "🫂", "✨", "🌟"],
        "neutral": ["✨", "💫", "🌟", "💙", "🌸"]
    }
    
    def __init__(self):
        """初始化温暖回应引擎"""
        pass
    
    def generate(self, emotion_result: EmotionResult, base_response: str,
                 user_context: Optional[Dict] = None) -> WarmResponse:
        """
        生成温暖回应
        
        Args:
            emotion_result: 情感分析结果
            base_response: 基础回应
            user_context: 用户上下文（可选）
            
        Returns:
            WarmResponse: 温暖回应结果
        """
        if user_context is None:
            user_context = {}
        
        # 获取用户偏好
        preferences = user_context.get("preferences", {})
        style = preferences.get("style", "warm")
        emoji_level = preferences.get("emoji_level", "moderate")
        
        # 1. 添加同理心开场白
        opener = self._select_opener(emotion_result)
        
        # 2. 增强基础回应
        enhanced_response = self._enhance_response(
            base_response, emotion_result, style
        )
        
        # 3. 添加支持性结尾
        closer = self._select_closer(emotion_result)
        
        # 4. 组合回应
        warm_text = self._compose_response(opener, enhanced_response, closer)
        
        # 5. 添加表情符号
        warm_text = self._add_emojis(warm_text, emotion_result, emoji_level)
        
        # 6. 应用风格调整
        warm_text = self._apply_style(warm_text, style)
        
        # 7. 计算温暖度分数
        warmth_score = self._calculate_warmth_score(
            emotion_result, style, len(opener) > 0, len(closer) > 0
        )
        
        # 8. 识别个性化元素
        personalized_elements = self._identify_personalized_elements(
            emotion_result, style, emoji_level
        )
        
        return WarmResponse(
            text=warm_text,
            warmth_score=warmth_score,
            style=style,
            personalized_elements=personalized_elements
        )
    
    def _select_opener(self, emotion_result: EmotionResult) -> str:
        """选择同理心开场白"""
        emotion = emotion_result.primary_emotion
        openers = self.EMPATHY_OPENERS.get(emotion, self.EMPATHY_OPENERS["neutral"])
        
        # 根据强度选择
        if emotion_result.intensity > 0.7:
            return random.choice(openers)
        elif emotion_result.intensity > 0.4:
            return random.choice(openers) if random.random() > 0.3 else ""
        else:
            return ""
    
    def _enhance_response(self, base_response: str, emotion_result: EmotionResult,
                          style: str) -> str:
        """增强基础回应"""
        enhanced = base_response
        
        # 根据情感类型调整
        if emotion_result.primary_emotion == "sadness":
            enhanced = self._make_more_supportive(enhanced)
        elif emotion_result.primary_emotion == "anger":
            enhanced = self._make_more_calming(enhanced)
        elif emotion_result.primary_emotion == "anxiety":
            enhanced = self._make_more_reassuring(enhanced)
        elif emotion_result.primary_emotion == "joy":
            enhanced = self._make_more_celebratory(enhanced)
        
        # 根据风格调整
        if style == "casual":
            enhanced = self._make_casual(enhanced)
        elif style == "professional":
            enhanced = self._make_professional(enhanced)
        elif style == "warm":
            enhanced = self._make_warmer(enhanced)
        
        return enhanced
    
    def _select_closer(self, emotion_result: EmotionResult) -> str:
        """选择支持性结尾"""
        emotion = emotion_result.primary_emotion
        closers = self.SUPPORT_CLOSERS.get(emotion, self.SUPPORT_CLOSERS["neutral"])
        
        # 如果需要支持或情感强度较高
        if emotion_result.needs_support or emotion_result.intensity > 0.6:
            return random.choice(closers)
        elif emotion_result.intensity > 0.3:
            return random.choice(closers) if random.random() > 0.5 else ""
        else:
            return ""
    
    def _compose_response(self, opener: str, enhanced_response: str, 
                          closer: str) -> str:
        """组合回应"""
        parts = []
        
        if opener:
            parts.append(opener)
        
        parts.append(enhanced_response)
        
        if closer:
            parts.append(closer)
        
        # 用合适的连接词组合
        if len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            return f"{parts[0]} {parts[1]}"
        else:
            return f"{parts[0]} {parts[1]} {parts[2]}"
    
    def _add_emojis(self, text: str, emotion_result: EmotionResult, 
                    level: str) -> str:
        """添加表情符号"""
        if level == "none":
            return text
        
        emotion = emotion_result.primary_emotion
        emojis = self.EMOJI_MAP.get(emotion, self.EMOJI_MAP["neutral"])
        
        if level == "low":
            # 只在结尾添加一个表情
            if not any(char in text for char in emojis):
                text = f"{text} {random.choice(emojis)}"
        elif level == "moderate":
            # 在开头和结尾添加表情
            if not text.startswith(tuple(emojis)):
                text = f"{random.choice(emojis)} {text}"
        elif level == "high":
            # 多处添加表情
            text = f"{random.choice(emojis)} {text} {random.choice(emojis)}"
        
        return text
    
    def _apply_style(self, text: str, style: str) -> str:
        """应用风格调整"""
        if style == "casual":
            # 添加一些口语化表达
            text = text.replace("。", "～")
        elif style == "professional":
            # 确保正式和专业
            text = text.replace("～", "。")
            text = text.replace("哈哈", "")
        
        return text
    
    def _calculate_warmth_score(self, emotion_result: EmotionResult, style: str,
                                has_opener: bool, has_closer: bool) -> float:
        """计算温暖度分数"""
        base_score = 0.5
        
        # 根据情感调整
        if emotion_result.primary_emotion in ["sadness", "anxiety", "fear", "loneliness"]:
            base_score += 0.1  # 对负面情感更需要温暖
        
        # 根据风格调整
        style_scores = {
            "warm": 0.2,
            "casual": 0.15,
            "balanced": 0.1,
            "professional": 0.0
        }
        base_score += style_scores.get(style, 0.1)
        
        # 根据元素调整
        if has_opener:
            base_score += 0.1
        if has_closer:
            base_score += 0.1
        
        # 根据情感强度调整
        base_score += emotion_result.intensity * 0.1
        
        return round(min(1.0, base_score), 2)
    
    def _identify_personalized_elements(self, emotion_result: EmotionResult,
                                        style: str, emoji_level: str) -> List[str]:
        """识别个性化元素"""
        elements = []
        
        if emotion_result.primary_emotion != "neutral":
            elements.append(f"情感识别: {emotion_result.primary_emotion}")
        
        if style != "balanced":
            elements.append(f"风格适配: {style}")
        
        if emoji_level != "moderate":
            elements.append(f"表情级别: {emoji_level}")
        
        if emotion_result.needs_support:
            elements.append("支持模式: 开启")
        
        return elements
    
    def _make_more_supportive(self, text: str) -> str:
        """使回应更有支持性"""
        supportive_phrases = [
            "别担心",
            "一切都会好起来的",
            "你并不孤单",
            "我相信你"
        ]
        
        if random.random() > 0.7:
            phrase = random.choice(supportive_phrases)
            text = f"{phrase}，{text}"
        
        return text
    
    def _make_more_calming(self, text: str) -> str:
        """使回应更 calming"""
        calming_phrases = [
            "冷静下来",
            "深呼吸",
            "放轻松",
            "慢慢来"
        ]
        
        if random.random() > 0.7:
            phrase = random.choice(calming_phrases)
            text = f"{phrase}，{text}"
        
        return text
    
    def _make_more_reassuring(self, text: str) -> str:
        """使回应更让人安心"""
        reassuring_phrases = [
            "不用担心",
            "没问题的",
            "一切都会顺利",
            "你可以的"
        ]
        
        if random.random() > 0.7:
            phrase = random.choice(reassuring_phrases)
            text = f"{phrase}，{text}"
        
        return text
    
    def _make_more_celebratory(self, text: str) -> str:
        """使回应更庆祝性"""
        celebratory_phrases = [
            "太棒了",
            "值得庆祝",
            "为你开心",
            "真替你高兴"
        ]
        
        if random.random() > 0.7:
            phrase = random.choice(celebratory_phrases)
            text = f"{phrase}！{text}"
        
        return text
    
    def _make_casual(self, text: str) -> str:
        """使回应更随意"""
        casual_additions = [
            "哈哈",
            "嗯嗯",
            "好的呢",
            "明白啦",
            "没问题"
        ]
        
        if random.random() > 0.7:
            addition = random.choice(casual_additions)
            text = f"{addition}，{text}"
        
        return text
    
    def _make_warmer(self, text: str) -> str:
        """使回应更温暖"""
        warm_additions = [
            "亲爱的",
            "朋友",
            "伙伴"
        ]
        
        if random.random() > 0.8:
            addition = random.choice(warm_additions)
            text = f"{addition}，{text}"
        
        return text
    
    def _make_professional(self, text: str) -> str:
        """使回应更专业"""
        # 移除过于口语化的表达
        text = re.sub(r'(哈哈|嗯嗯|呢|啦|哦)', '', text)
        return text.strip()


# 全局温暖回应引擎实例
_warm_response_engine: Optional[WarmResponseEngine] = None


def get_warm_response_engine() -> WarmResponseEngine:
    """获取全局温暖回应引擎实例（单例模式）"""
    global _warm_response_engine
    if _warm_response_engine is None:
        _warm_response_engine = WarmResponseEngine()
    return _warm_response_engine


# 便捷函数
def generate_warm_response(emotion_result: EmotionResult, base_response: str,
                           user_context: Optional[Dict] = None) -> WarmResponse:
    """便捷函数：生成温暖回应"""
    engine = get_warm_response_engine()
    return engine.generate(emotion_result, base_response, user_context)


if __name__ == "__main__":
    # 测试
    from emotion_analyzer import analyze_emotion
    
    test_cases = [
        ("今天工作压力好大", "建议你休息一下"),
        ("今天好开心啊", "那就好"),
        ("好难过，不知道该怎么办", "别担心")
    ]
    
    for text, base_response in test_cases:
        emotion_result = analyze_emotion(text)
        warm_response = generate_warm_response(emotion_result, base_response)
        
        print(f"输入: {text}")
        print(f"基础回应: {base_response}")
        print(f"温暖回应: {warm_response.text}")
        print(f"温暖度: {warm_response.warmth_score}")
        print("-" * 50)
