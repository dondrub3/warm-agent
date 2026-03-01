  auto_detect: true                 # 自动检测情感
  enhance_all: false                # 增强所有回应
  default_warm_mode: false          # 默认温暖模式
  
  # 响应配置
  min_warmth_score: 0.3             # 最小温暖度分数
  max_response_length: 500          # 最大回应长度
  
  # 用户偏好默认值
  default_preferences:
    style: "balanced"               # 风格: warm/professional/casual/balanced
    emoji_level: "moderate"         # 表情符号: none/low/moderate/high
    warmth_intensity: 0.7           # 温暖强度: 0.0-1.0
  
  # 高级配置
  cache_enabled: true               # 启用缓存
  cache_ttl: 300                    # 缓存时间(秒)
  retry_count: 3                    # 重试次数
  fallback_to_original: true        # 失败时回退到原始回应
```

### OpenClaw 技能配置

```yaml
# OpenClaw技能配置
skills:
  warm_agent:
    enabled: true
    priority: 50                    # 技能优先级
    triggers:                       # 触发条件
      - emotion_keywords            # 情感关键词
      - explicit_commands           # 显式命令
      - user_preference             # 用户偏好
    
    # 集成方式
    integration_type: "api"         # api/embedded/websocket
    
    # API集成配置
    api:
      url: "http://localhost:8000"
      key: "${WARM_AGENT_API_KEY}"
    
    # 嵌入式集成配置
    embedded:
      data_path: "./data/emotion_words.json"
      model_path: "./models/emotion_model.pkl"
    
    # WebSocket集成配置
    websocket:
      url: "ws://localhost:8765"
      reconnect_interval: 5
```

## 使用示例

### 1. 基本使用

```python
# 在OpenClaw消息处理器中使用
async def handle_message(message: str, context: Dict) -> str:
    """处理消息"""
    # 获取基础AI回应
    base_response = await get_ai_response(message)
    
    # 使用Warm Agent增强回应
    warm_agent = WarmAgentSkill(config)
    enhanced_response = await warm_agent.process_message(
        message=message,
        context={
            "base_response": base_response,
            "user_id": context.user_id,
            "preferences": context.preferences
        }
    )
    
    return enhanced_response
```

### 2. 情感分析独立使用

```python
# 仅使用情感分析功能
async def analyze_emotion_only(text: str) -> Dict:
    """分析文本情感"""
    warm_agent = WarmAgentSkill(config)
    
    # 调用情感分析API
    emotion_data = await warm_agent._analyze_emotion(
        text=text,
        context={"user_id": "analyzer"}
    )
    
    return {
        "emotion": emotion_data["primary_emotion"],
        "intensity": emotion_data["intensity"],
        "needs_support": emotion_data["needs_support"],
        "keywords": emotion_data["keywords"]
    }
```

### 3. 批量处理

```python
# 批量处理消息
async def batch_process(messages: List[str]) -> List[str]:
    """批量处理消息"""
    warm_agent = WarmAgentSkill(config)
    results = []
    
    for message in messages:
        base_response = await get_ai_response(message)
        
        enhanced = await warm_agent.process_message(
            message=message,
            context={"base_response": base_response}
        )
        
        results.append(enhanced)
    
    return results
```

## 性能优化

### 1. 缓存策略

```python
# 实现响应缓存
import hashlib
import json
from functools import lru_cache

class CachedWarmAgentSkill(WarmAgentSkill):
    """带缓存的Warm Agent技能"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.cache_enabled = config.get("cache_enabled", True)
        self.cache_ttl = config.get("cache_ttl", 300)
        self.cache = {}
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """带缓存的消息处理"""
        # 生成缓存键
        cache_key = self._generate_cache_key(message, context)
        
        # 检查缓存
        if self.cache_enabled and cache_key in self.cache:
            cached_item = self.cache[cache_key]
            if time.time() - cached_item["timestamp"] < self.cache_ttl:
                return cached_item["response"]
        
        # 处理消息
        response = await super().process_message(message, context)
        
        # 缓存结果
        if self.cache_enabled:
            self.cache[cache_key] = {
                "response": response,
                "timestamp": time.time()
            }
            
            # 清理过期缓存
            self._cleanup_cache()
        
        return response
    
    def _generate_cache_key(self, message: str, context: Dict[str, Any]) -> str:
        """生成缓存键"""
        key_data = {
            "message": message,
            "user_id": context.get("user_id", ""),
            "preferences_hash": hash(json.dumps(context.get("preferences", {}), sort_keys=True))
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _cleanup_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, item in self.cache.items()
            if current_time - item["timestamp"] > self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
```

### 2. 异步批处理

```python
# 异步批处理实现
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncBatchWarmAgent:
    """异步批处理Warm Agent"""
    
    def __init__(self, config: Dict[str, Any], max_workers: int = 4):
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_batch(self, messages: List[Dict]) -> List[Dict]:
        """批量处理消息"""
        # 创建任务列表
        tasks = [
            self._process_single_async(message)
            for message in messages
        ]
        
        # 并发执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # 出错时使用原始回应
                processed_results.append({
                    "original": messages[i],
                    "enhanced": messages[i].get("base_response", ""),
                    "error": str(result),
                    "success": False
                })
            else:
                processed_results.append({
                    "original": messages[i],
                    "enhanced": result,
                    "success": True
                })
        
        return processed_results
    
    async def _process_single_async(self, message_data: Dict) -> str:
        """异步处理单个消息"""
        loop = asyncio.get_event_loop()
        
        # 在线程池中执行阻塞操作
        return await loop.run_in_executor(
            self.executor,
            self._process_single_sync,
            message_data
        )
    
    def _process_single_sync(self, message_data: Dict) -> str:
        """同步处理单个消息"""
        # 这里调用同步的Warm Agent处理逻辑
        warm_agent = WarmAgentSkill(self.config)
        
        # 注意：这里需要同步版本的process_message
        # 实际实现中可能需要调整
        return warm_agent.process_message_sync(
            message=message_data["text"],
            context={
                "base_response": message_data.get("base_response", ""),
                "user_id": message_data.get("user_id", ""),
                "preferences": message_data.get("preferences", {})
            }
        )
```

## 监控和日志

### 1. 集成监控

```python
# 监控装饰器
import time
from functools import wraps
from prometheus_client import Counter, Histogram

# 定义监控指标
WARM_AGENT_REQUESTS = Counter(
    'warm_agent_requests_total',
    'Total Warm Agent requests',
    ['endpoint', 'status']
)

WARM_AGENT_LATENCY = Histogram(
    'warm_agent_request_duration_seconds',
    'Warm Agent request duration',
    ['endpoint']
)

def monitor_warm_agent(endpoint: str):
    """监控装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                WARM_AGENT_REQUESTS.labels(endpoint=endpoint, status='success').inc()
                return result
            
            except Exception as e:
                WARM_AGENT_REQUESTS.labels(endpoint=endpoint, status='error').inc()
                raise e
            
            finally:
                duration = time.time() - start_time
                WARM_AGENT_LATENCY.labels(endpoint=endpoint).observe(duration)
        
        return wrapper
    return decorator

# 使用监控
@monitor_warm_agent("process_message")
async def process_message_with_monitoring(message: str, context: Dict) -> str:
    """带监控的消息处理"""
    warm_agent = WarmAgentSkill(config)
    return await warm_agent.process_message(message, context)
```

### 2. 详细日志

```python
# 结构化日志
import structlog

logger = structlog.get_logger()

class LoggingWarmAgentSkill(WarmAgentSkill):
    """带日志的Warm Agent技能"""
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """带日志的消息处理"""
        user_id = context.get("user_id", "unknown")
        
        logger.info(
            "开始处理消息",
            user_id=user_id,
            message_length=len(message),
            has_base_response="base_response" in context
        )
        
        try:
            result = await super().process_message(message, context)
            
            logger.info(
                "消息处理成功",
                user_id=user_id,
                result_length=len(result),
                enhanced=result != context.get("base_response", "")
            )
            
            return result
        
        except Exception as e:
            logger.error(
                "消息处理失败",
                user_id=user_id,
                error=str(e),
                message_preview=message[:100]
            )
            
            # 失败时返回原始回应
            return context.get("base_response", "")
```

## 故障排除

### 常见问题

#### 1. API连接失败

**症状**: Warm Agent服务无法连接
**解决方案**:
```bash
# 检查服务状态
curl http://localhost:8000/health

# 检查网络连接
ping localhost

# 查看服务日志
docker-compose logs warm-agent-api
```

#### 2. 响应时间过长

**症状**: 处理消息耗时过长
**解决方案**:
- 启用缓存
- 调整超时时间
- 优化情感分析模型
- 使用异步处理

#### 3. 情感分析不准确

**症状**: 情感识别错误
**解决方案**:
- 更新情感词库
- 调整分析参数
- 添加自定义规则
- 收集反馈并改进

#### 4. 内存使用过高

**症状**: 内存占用持续增长
**解决方案**:
- 清理缓存
- 限制并发数
- 使用流式处理
- 监控内存使用

### 调试技巧

```python
# 启用调试模式
import logging
logging.basicConfig(level=logging.DEBUG)

# 添加调试信息
def debug_warm_agent(message: str, context: Dict) -> str:
    """调试Warm Agent"""
    print(f"输入消息: {message}")
    print(f"上下文: {context}")
    
    # 逐步调试
    emotion_result = emotion_analyzer.analyze(message)
    print(f"情感分析结果: {emotion_result}")
    
    warm_response = warm_engine.generate(emotion_result)
    print(f"温暖回应: {warm_response.text}")
    
    return warm_response.text
```

## 最佳实践

### 1. 渐进式增强

```python
# 渐进式增强策略
class ProgressiveWarmAgent:
    """渐进式增强的Warm Agent"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enhancement_levels = [
            self._level1_basic_empathy,      # 基础同理心
            self._level2_emotional_support,  # 情感支持
            self._level3_personalized_care,  # 个性化关怀
            self._level4_deep_connection     # 深度连接
        ]
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """渐进式增强处理"""
        base_response = context.get("base_response", "")
        
        # 根据用户互动历史决定增强级别
        user_id = context.get("user_id", "")
        interaction_count = self._get_interaction_count(user_id)
        
        # 选择增强级别
        enhancement_level = min(
            interaction_count // 10,  # 每10次互动提升一级
            len(self.enhancement_levels) - 1
        )
        
        # 应用增强
        enhanced_response = base_response
        for level in range(enhancement_level + 1):
            enhanced_response = await self.enhancement_levels[level](
                message, enhanced_response, context
            )
        
        # 更新互动计数
        self._update_interaction_count(user_id)
        
        return enhanced_response
    
    async def _level1_basic_empathy(self, message: str, response: str, context: Dict[str, Any]) -> str:
        """基础同理心级别"""
        # 添加简单的情感认可
        emotion_result = emotion_analyzer.analyze(message)
        
        if emotion_result.primary_emotion != "neutral":
            return f"感受到你的{emotion_result.primary_emotion}了... {response}"
        
        return response
    
    async def _level2_emotional_support(self, message: str, response: str, context: Dict[str, Any]) -> str:
        """情感支持级别"""
        # 添加情感支持表达
        emotion_result = emotion_analyzer.analyze(message)
        
        if emotion_result.needs_support:
            support_phrases = [
                "我在这里支持你",
                "你不是一个人",
                "我会陪着你"
            ]
            import random
            support = random.choice(support_phrases)
            return f"{response} {support}～"
        
        return response
    
    # ... 其他级别实现
```

### 2. A/B测试

```python
# A/B测试实现
class ABTestWarmAgent:
    """A/B测试的Warm Agent"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.variants = {
            "control": ControlVariant(),      # 控制组：原始回应
            "variant_a": VariantA(),          # 变体A：基础温暖
            "variant_b": VariantB(),          # 变体B：深度温暖
            "variant_c": VariantC()           # 变体C：个性化温暖
        }
        
        # 分配比例
        self.allocation = {
            "control": 0.25,
            "variant_a": 0.25,
            "variant_b": 0.25,
            "variant_c": 0.25
        }
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """A/B测试处理"""
        user_id = context.get("user_id", "")
        
        # 为用户分配变体（保持一致性）
        variant = self._assign_variant(user_id)
        
        # 记录分配
        self._record_allocation(user_id, variant)
        
        # 使用对应变体处理
        result = await self.variants[variant].process_message(
            message, context
        )
        
        # 记录结果（用于后续分析）
        self._record_result(user_id, variant, message, result)
        
        return result
    
    def _assign_variant(self, user_id: str) -> str:
        """为用户分配变体"""
        # 使用用户ID的哈希值确保一致性分配
        import hashlib
        hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        random_value = hash_value % 100 / 100.0
        
        cumulative = 0
        for variant, probability in self.allocation.items():
            cumulative += probability
            if random_value <= cumulative:
                return variant
        
        return "control"
```

### 3. 用户反馈收集

```python
# 用户反馈系统
class FeedbackWarmAgent:
    """带反馈收集的Warm Agent"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.feedback_storage = FeedbackStorage()
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """处理消息并收集反馈"""
        # 处理消息
        warm_agent = WarmAgentSkill(self.config)
        response = await warm_agent.process_message(message, context)
        
        # 添加反馈收集提示
        if self._should_ask_for_feedback(context):
            response = self._add_feedback_prompt(response, message)
        
        return response
    
    def _should_ask_for_feedback(self, context: Dict[str, Any]) -> bool:
        """判断是否应该请求反馈"""
        user_id = context.get("user_id",