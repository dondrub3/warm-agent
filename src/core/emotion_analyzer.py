"""
情感分析引擎 - Warm Agent核心模块

提供多层级情感分析功能，包括关键词匹配、上下文理解和强度计算。
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import re
import jieba


class EmotionType(Enum):
    """情感类型枚举"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    ANXIETY = "anxiety"
    FEAR = "fear"
    NEUTRAL = "neutral"


@dataclass
class EmotionResult:
    """情感分析结果"""
    primary_emotion: str
    secondary_emotions: List[str]
    intensity: float
    confidence: float
    keywords: List[str]
    context_hints: List[str]
    needs_support: bool
    suggested_response: str
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "primary_emotion": self.primary_emotion,
            "secondary_emotions": self.secondary_emotions,
            "intensity": self.intensity,
            "confidence": self.confidence,
            "keywords": self.keywords,
            "context_hints": self.context_hints,
            "needs_support": self.needs_support,
            "suggested_response": self.suggested_response
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "EmotionResult":
        """从字典创建"""
        return cls(
            primary_emotion=data.get("primary_emotion", "neutral"),
            secondary_emotions=data.get("secondary_emotions", []),
            intensity=data.get("intensity", 0.0),
            confidence=data.get("confidence", 0.5),
            keywords=data.get("keywords", []),
            context_hints=data.get("context_hints", []),
            needs_support=data.get("needs_support", False),
            suggested_response=data.get("suggested_response", "")
        )


class EmotionAnalyzer:
    """情感分析器"""
    
    # 情感词库
    EMOTION_KEYWORDS = {
        "joy": ["开心", "高兴", "快乐", "幸福", "兴奋", "喜悦", "愉快", "满足", "爽", "棒", "赞", "太好了", "哈哈"],
        "sadness": ["难过", "伤心", "悲伤", "痛苦", "失落", "沮丧", "委屈", "想哭", "emo", "down"],
        "anger": ["生气", "愤怒", "恼火", "烦躁", "不爽", "讨厌", "恨", "气死我了", "烦死了"],
        "anxiety": ["焦虑", "担心", "紧张", "压力", "害怕", "恐惧", "慌", "不知所措", "迷茫"],
        "surprise": ["惊讶", "震惊", "意外", "没想到", "天哪", "哇塞", "OMG"],
        "disgust": ["恶心", "厌恶", "反感", "受不了", "想吐"],
        "love": ["爱", "喜欢", "心动", "思念", "想念", "在乎", "珍惜"],
        "gratitude": ["感谢", "感激", "谢谢", "感恩", "铭记"],
        "loneliness": ["孤独", "寂寞", "空虚", "没人懂", "一个人"],
    }
    
    # 否定词
    NEGATION_WORDS = ["不", "没", "无", "非", "莫", "勿", "别", "没有", "不是", "不能", "不会"]
    
    # 程度词
    INTENSITY_MODIFIERS = {
        "very": ["非常", "特别", "十分", "极其", "超级", "太", "很", "特别", "超级", "巨"],
        "slightly": ["有点", "稍微", "略", " somewhat", "一点点"],
        "extremely": ["极度", "崩溃", "要死", "疯了", "受不了了"]
    }
    
    # 需求词 - 表示用户需要情感支持
    NEED_SUPPORT_KEYWORDS = [
        "怎么办", "好难", "坚持不住了", "救救", "帮帮我", "好痛苦",
        "想死", "活着没意思", "没人理解", "好累", "想放弃"
    ]
    
    def __init__(self):
        """初始化情感分析器"""
        # 加载jieba词典
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            for word in keywords:
                jieba.add_word(word)
    
    def analyze(self, text: str, context: Optional[Dict] = None) -> EmotionResult:
        """
        分析文本情感
        
        Args:
            text: 输入文本
            context: 上下文信息（可选）
            
        Returns:
            EmotionResult: 情感分析结果
        """
        if not text or not text.strip():
            return self._create_neutral_result()
        
        # 1. 关键词匹配
        emotion_scores = self._match_keywords(text)
        
        # 2. 处理否定词
        emotion_scores = self._handle_negation(text, emotion_scores)
        
        # 3. 计算强度
        intensity = self._calculate_intensity(text, emotion_scores)
        
        # 4. 提取关键词
        keywords = self._extract_keywords(text)
        
        # 5. 分析上下文
        context_hints = self._analyze_context(text, context)
        
        # 6. 确定主要情感和次要情感
        primary_emotion, secondary_emotions = self._determine_emotions(emotion_scores)
        
        # 7. 判断是否需要支持
        needs_support = self._check_needs_support(text, primary_emotion, intensity)
        
        # 8. 生成建议回应
        suggested_response = self._generate_suggested_response(
            primary_emotion, intensity, needs_support, keywords
        )
        
        # 9. 计算置信度
        confidence = self._calculate_confidence(emotion_scores, text)
        
        return EmotionResult(
            primary_emotion=primary_emotion,
            secondary_emotions=secondary_emotions,
            intensity=intensity,
            confidence=confidence,
            keywords=keywords,
            context_hints=context_hints,
            needs_support=needs_support,
            suggested_response=suggested_response
        )
    
    def _match_keywords(self, text: str) -> Dict[str, float]:
        """匹配情感关键词"""
        scores = {emotion: 0.0 for emotion in self.EMOTION_KEYWORDS.keys()}
        
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    # 基础分 + 词频
                    count = text.count(keyword)
                    scores[emotion] += 0.3 * count
        
        return scores
    
    def _handle_negation(self, text: str, scores: Dict[str, float]) -> Dict[str, float]:
        """处理否定词"""
        # 简单的否定处理：如果在情感词前有否定词，降低该情感分数
        words = list(jieba.cut(text))
        
        for i, word in enumerate(words):
            if word in self.NEGATION_WORDS and i + 1 < len(words):
                # 检查后面的词是否是情感词
                next_word = words[i + 1]
                for emotion, keywords in self.EMOTION_KEYWORDS.items():
                    if next_word in keywords:
                        scores[emotion] *= 0.3  # 降低分数
                        # 可能转向中性或相反情感
                        if emotion == "joy":
                            scores["sadness"] += 0.2
                        elif emotion == "sadness":
                            scores["joy"] += 0.2
        
        return scores
    
    def _calculate_intensity(self, text: str, scores: Dict[str, float]) -> float:
        """计算情感强度"""
        base_intensity = max(scores.values()) if scores else 0.5
        
        # 根据程度词调整
        for modifier in self.INTENSITY_MODIFIERS["extremely"]:
            if modifier in text:
                base_intensity = min(1.0, base_intensity * 1.5)
                break
        
        for modifier in self.INTENSITY_MODIFIERS["very"]:
            if modifier in text:
                base_intensity = min(1.0, base_intensity * 1.2)
                break
        
        for modifier in self.INTENSITY_MODIFIERS["slightly"]:
            if modifier in text:
                base_intensity = max(0.1, base_intensity * 0.7)
                break
        
        # 标点符号影响
        if "!!" in text or "！" in text:
            base_intensity = min(1.0, base_intensity * 1.2)
        
        return round(base_intensity, 2)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        keywords = []
        
        # 提取情感关键词
        for emotion_words in self.EMOTION_KEYWORDS.values():
            for word in emotion_words:
                if word in text and word not in keywords:
                    keywords.append(word)
        
        # 提取需求关键词
        for word in self.NEED_SUPPORT_KEYWORDS:
            if word in text and word not in keywords:
                keywords.append(word)
        
        return keywords[:5]  # 最多返回5个关键词
    
    def _analyze_context(self, text: str, context: Optional[Dict]) -> List[str]:
        """分析上下文"""
        hints = []
        
        # 时间上下文
        if any(word in text for word in ["今天", "昨天", "刚才", "现在"]):
            hints.append("time_specific")
        
        # 地点上下文
        if any(word in text for word in ["家", "公司", "学校", "路上"]):
            hints.append("location_specific")
        
        # 人物上下文
        if any(word in text for word in ["他", "她", "他们", "朋友", "家人", "同事"]):
            hints.append("social_context")
        
        # 事件上下文
        if any(word in text for word in ["工作", "学习", "感情", "健康", "钱", "考试"]):
            hints.append("life_event")
        
        return hints
    
    def _determine_emotions(self, scores: Dict[str, float]) -> Tuple[str, List[str]]:
        """确定主要情感和次要情感"""
        sorted_emotions = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_emotions or sorted_emotions[0][1] == 0:
            return "neutral", []
        
        primary = sorted_emotions[0][0]
        
        # 次要情感：分数大于0且与主要情感差距不太大
        secondary = [
            emotion for emotion, score in sorted_emotions[1:]
            if score > 0 and score > sorted_emotions[0][1] * 0.5
        ]
        
        return primary, secondary[:2]  # 最多2个次要情感
    
    def _check_needs_support(self, text: str, primary_emotion: str, intensity: float) -> bool:
        """判断是否需要情感支持"""
        # 高强度负面情绪
        if primary_emotion in ["sadness", "anger", "anxiety", "fear", "loneliness"]:
            if intensity > 0.6:
                return True
        
        # 需求关键词
        for keyword in self.NEED_SUPPORT_KEYWORDS:
            if keyword in text:
                return True
        
        # 疑问句可能需要支持
        if "?" in text or "？" in text:
            if primary_emotion in ["sadness", "anxiety", "confusion"]:
                return True
        
        return False
    
    def _generate_suggested_response(self, emotion: str, intensity: float, 
                                     needs_support: bool, keywords: List[str]) -> str:
        """生成建议回应"""
        keyword = keywords[0] if keywords else "这件事"
        
        templates = {
            "joy": [
                "听到你{keyword}，我也感到很开心呢！😊",
                "哇，{keyword}的事情真让人高兴！✨",
                "能感受到你的喜悦，{keyword}的时候确实很幸福～"
            ],
            "sadness": [
                "听到你{keyword}，我也感到很难过...😢 想聊聊吗？",
                "{keyword}的感觉确实不好受，我在这里陪着你",
                "能感受到你的悲伤，{keyword}的时候确实需要安慰"
            ],
            "anger": [
                "理解你的愤怒，{keyword}确实让人生气！😤",
                "{keyword}的事情换谁都会恼火，想发泄一下吗？",
                "感受到你的不满了，{keyword}的时候确实需要冷静"
            ],
            "anxiety": [
                "{keyword}的时候感到焦虑很正常，深呼吸，慢慢来...🌸",
                "理解你的担心，{keyword}确实让人不安",
                "焦虑的时候需要放松，{keyword}的事情会好起来的"
            ],
            "fear": [
                "{keyword}的时候感到害怕是正常的，你很勇敢！💪",
                "理解你的恐惧，{keyword}确实让人担心",
                "{keyword}的时候确实需要勇气，我会一直支持你"
            ],
            "surprise": [
                "哇！{keyword}的事情确实让人意外！😲",
                "听到这个{keyword}的消息，我也感到吃惊！",
                "{keyword}的瞬间总是让人难忘呢～"
            ],
            "disgust": [
                "感受到你的{keyword}了...🤢 这种反感确实让人不舒服",
                "听到你{keyword}，我能理解这种感受",
                "{keyword}的时候确实需要调整心态"
            ],
            "love": [
                "感受到你的{keyword}了...❤️ 爱是最美好的情感",
                "听到你{keyword}，我也被温暖到了～",
                "{keyword}的力量真是强大呢！✨"
            ],
            "gratitude": [
                "感受到你的{keyword}之心了...🙏 感恩是最美的品质",
                "听到你{keyword}，我也被感动了",
                "{keyword}的时候，世界都变得更美好了"
            ],
            "loneliness": [
                "感受到你的{keyword}了...🌙 孤独的时候确实需要陪伴",
                "听到你{keyword}，我的心也跟着揪了一下",
                "{keyword}的滋味不好受，但请记得我在这里"
            ],
            "neutral": [
                "我在这里用心倾听～✨",
                "感受到你想和我连接的心意了...❤️",
                "愿意分享更多吗？我在这里陪着你"
            ]
        }
        
        # 选择模板
        emotion_templates = templates.get(emotion, templates["neutral"])
        
        # 根据强度调整
        if intensity > 0.8 and needs_support:
            # 高强度且需要支持，选择更有同理心的模板
            template = emotion_templates[0] if emotion_templates else templates["neutral"][0]
        elif intensity < 0.3:
            # 低强度，选择轻松的模板
            template = emotion_templates[-1] if emotion_templates else templates["neutral"][-1]
        else:
            # 中等强度
            template = emotion_templates[1] if len(emotion_templates) > 1 else emotion_templates[0]
        
        return template.format(keyword=keyword)
    
    def _calculate_confidence(self, scores: Dict[str, float], text: str) -> float:
        """计算置信度"""
        if not scores:
            return 0.5
        
        max_score = max(scores.values())
        total_score = sum(scores.values())
        
        if total_score == 0:
            return 0.5
        
        # 最高分占比越高，置信度越高
        confidence = max_score / total_score if total_score > 0 else 0.5
        
        # 文本长度影响（太短或太长都降低置信度）
        text_length = len(text)
        if text_length < 5:
            confidence *= 0.8
        elif text_length > 500:
            confidence *= 0.9
        
        return round(min(1.0, confidence), 2)
    
    def _create_neutral_result(self) -> EmotionResult:
        """创建中性情感结果"""
        return EmotionResult(
            primary_emotion="neutral",
            secondary_emotions=[],
            intensity=0.0,
            confidence=0.5,
            keywords=[],
            context_hints=[],
            needs_support=False,
            suggested_response="我在这里用心倾听～✨"
        )


# 全局情感分析器实例
_emotion_analyzer: Optional[EmotionAnalyzer] = None


def get_emotion_analyzer() -> EmotionAnalyzer:
    """获取全局情感分析器实例（单例模式）"""
    global _emotion_analyzer
    if _emotion_analyzer is None:
        _emotion_analyzer = EmotionAnalyzer()
    return _emotion_analyzer


# 便捷函数
def analyze_emotion(text: str, context: Optional[Dict] = None) -> EmotionResult:
    """便捷函数：分析文本情感"""
    analyzer = get_emotion_analyzer()
    return analyzer.analyze(text, context)


if __name__ == "__main__":
    # 测试
    test_texts = [
        "今天好开心啊！",
        "工作压力好大，好焦虑",
        "今天被老板批评了，好难过",
        "不知道该怎么办才好",
        "普通的天气"
    ]
    
    analyzer = get_emotion_analyzer()
    for text in test_texts:
        result = analyzer.analyze(text)
        print(f"文本: {text}")
        print(f"情感: {result.primary_emotion} (强度: {result.intensity})")
        print(f"关键词: {result.keywords}")
        print(f"建议回应: {result.suggested_response}")
        print("-" * 50)
