        return escape(text)
    
    def validate_api_request(self, request_data: dict) -> tuple[bool, dict]:
        """验证API请求"""
        errors = {}
        
        # 验证必需字段
        required_fields = ["text"]
        for field in required_fields:
            if field not in request_data:
                errors[field] = "This field is required"
        
        # 验证文本字段
        if "text" in request_data:
            is_valid, error_msg = self.validate_text(request_data["text"])
            if not is_valid:
                errors["text"] = error_msg
        
        # 验证可选字段
        if "language" in request_data:
            valid_languages = ["zh-CN", "en-US", "ja-JP"]
            if request_data["language"] not in valid_languages:
                errors["language"] = f"Invalid language. Must be one of: {valid_languages}"
        
        return len(errors) == 0, errors

## 8. 测试策略

### 8.1 测试金字塔
```
        ┌─────────────────┐
        │   E2E Tests     │  (10%)
        │  (UI/API集成)    │
        └─────────────────┘
                │
        ┌─────────────────┐
        │ Integration     │  (20%)
        │ Tests           │
        │ (组件集成)       │
        └─────────────────┘
                │
        ┌─────────────────┐
        │   Unit Tests    │  (70%)
        │  (单元测试)      │
        └─────────────────┘
```

### 8.2 单元测试示例
```python
# tests/test_emotion_analyzer.py
import pytest
from app.services.emotion_analyzer import EmotionAnalyzer

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
    
    def test_analyze_negative_emotion(self, analyzer):
        """测试负面情感分析"""
        text = "工作压力好大"
        result = analyzer.analyze(text)
        
        assert result.primary_emotion in ["anxiety", "stress"]
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
    
    @pytest.mark.parametrize("text,expected_emotion", [
        ("我很难过", "sadness"),
        ("我很高兴", "happiness"),
        ("我有点焦虑", "anxiety"),
        ("需要安慰", "comfort_needed"),
    ])
    def test_multiple_emotions(self, analyzer, text, expected_emotion):
        """测试多种情感"""
        result = analyzer.analyze(text)
        assert result.primary_emotion == expected_emotion
```

### 8.3 集成测试示例
```python
# tests/test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

class TestAPI:
    """API集成测试"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def valid_api_key(self):
        return "test_api_key_123"
    
    def test_emotion_analysis_endpoint(self, client, valid_api_key):
        """测试情感分析端点"""
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
    
    def test_warm_response_generation(self, client, valid_api_key):
        """测试温暖回应生成"""
        headers = {"X-API-Key": valid_api_key}
        data = {
            "text": "今天工作压力大",
            "base_response": "建议休息一下",
            "emotion_data": {
                "primary_emotion": "anxiety",
                "intensity": 0.8
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
        assert result["data"]["warmth_score"] > 0.5
    
    def test_api_key_authentication(self, client):
        """测试API Key认证"""
        data = {"text": "测试"}
        
        # 没有API Key
        response = client.post("/v1/emotion/analyze", json=data)
        assert response.status_code == 401
        
        # 无效的API Key
        headers = {"X-API-Key": "invalid_key"}
        response = client.post("/v1/emotion/analyze", 
                              json=data, 
                              headers=headers)
        assert response.status_code == 401
    
    def test_rate_limiting(self, client, valid_api_key):
        """测试限流"""
        headers = {"X-API-Key": valid_api_key}
        data = {"text": "测试"}
        
        # 发送多个请求
        for i in range(15):  # 超过免费用户限制
            response = client.post("/v1/emotion/analyze",
                                  json=data,
                                  headers=headers)
            
            if i >= 10:  # 免费用户限制是10次
                assert response.status_code == 429
            else:
                assert response.status_code == 200
```

### 8.4 E2E测试示例
```python
# tests/test_e2e.py
import pytest
import asyncio
from playwright.async_api import async_playwright

class TestE2E:
    """端到端测试"""
    
    @pytest.fixture(scope="class")
    def event_loop(self):
        """创建事件循环"""
        loop = asyncio.get_event_loop_policy().new_event_loop()
        yield loop
        loop.close()
    
    @pytest.mark.asyncio
    async def test_web_interface(self):
        """测试Web界面"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # 访问网站
            await page.goto("http://localhost:3000")
            
            # 检查页面标题
            title = await page.title()
            assert "Warm Agent" in title
            
            # 测试情感分析功能
            await page.fill("#text-input", "今天心情很好")
            await page.click("#analyze-button")
            
            # 等待结果
            await page.wait_for_selector(".result-container", timeout=5000)
            
            # 检查结果
            result_text = await page.text_content(".emotion-result")
            assert "开心" in result_text or "高兴" in result_text
            
            await browser.close()
    
    @pytest.mark.asyncio
    async def test_api_documentation(self):
        """测试API文档"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # 访问API文档
            await page.goto("http://localhost:8000/docs")
            
            # 检查Swagger UI加载
            await page.wait_for_selector(".swagger-ui", timeout=5000)
            
            # 检查端点列表
            endpoints = await page.query_selector_all(".opblock-tag")
            assert len(endpoints) >= 3  # 至少3个端点
            
            await browser.close()
```

## 9. 性能优化

### 9.1 缓存策略
```python
# app/cache.py
from redis import Redis
from functools import wraps
import json
import hashlib

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    def cache_result(self, ttl: int = 3600):
        """缓存装饰器"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 生成缓存键
                cache_key = self._generate_cache_key(func, args, kwargs)
                
                # 尝试从缓存获取
                cached = await self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)
                
                # 执行函数
                result = await func(*args, **kwargs)
                
                # 缓存结果
                await self.redis.setex(
                    cache_key,
                    ttl,
                    json.dumps(result)
                )
                
                return result
            return wrapper
        return decorator
    
    def _generate_cache_key(self, func, args, kwargs) -> str:
        """生成缓存键"""
        # 基于函数名和参数生成唯一键
        key_parts = [
            func.__module__,
            func.__name__,
            str(args),
            str(sorted(kwargs.items()))
        ]
        
        key_string = ":".join(key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"cache:{key_hash}"

# 使用示例
@cache_manager.cache_result(ttl=300)  # 缓存5分钟
async def analyze_emotion_cached(text: str) -> dict:
    """带缓存的情感分析"""
    return await emotion_analyzer.analyze(text)
```

### 9.2 数据库优化
```sql
-- 1. 创建适当的索引
CREATE INDEX idx_emotion_records_user_timestamp 
ON emotion_records(user_id, timestamp DESC);

CREATE INDEX idx_api_calls_user_endpoint 
ON api_calls(user_id, endpoint, created_at DESC);

-- 2. 使用物化视图加速查询
CREATE MATERIALIZED VIEW emotion_summary_daily AS
SELECT 
    user_id,
    DATE(timestamp) as date,
    COUNT(*) as total_interactions,
    AVG((emotion_data->>'intensity')::FLOAT) as avg_intensity,
    MODE() WITHIN GROUP (ORDER BY emotion_data->>'primary_emotion') as most_common_emotion
FROM emotion_records
GROUP BY user_id, DATE(timestamp);

-- 定期刷新物化视图
REFRESH MATERIALIZED VIEW CONCURRENTLY emotion_summary_daily;

-- 3. 查询优化示例
EXPLAIN ANALYZE
SELECT *
FROM emotion_records
WHERE user_id = 'user_123'
  AND timestamp >= NOW() - INTERVAL '7 days'
  AND (emotion_data->>'primary_emotion') = 'anxiety'
ORDER BY timestamp DESC
LIMIT 100;
```

### 9.3 异步处理
```python
# app/tasks.py
from celery import Celery
from app.database import get_db
from app.services.emotion_analyzer import EmotionAnalyzer

# 创建Celery应用
celery_app = Celery(
    'warm_agent',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

@celery_app.task
def analyze_emotion_async(text: str, user_id: str):
    """异步情感分析任务"""
    analyzer = EmotionAnalyzer()
    result = analyzer.analyze(text)
    
    # 存储结果到数据库
    db = next(get_db())
    
    # 创建记录
    record = EmotionRecord(
        user_id=user_id,
        user_input=text,
        emotion_data=result.to_dict(),
        response="",  # 稍后填充
        timestamp=datetime.utcnow()
    )
    
    db.add(record)
    db.commit()
    
    return result.to_dict()

@celery_app.task
def generate_warm_response_async(text: str, emotion_data: dict, user_id: str):
    """异步生成温暖回应"""
    from app.services.warm_response_engine import WarmResponseEngine
    
    engine = WarmResponseEngine()
    response = engine.generate(
        emotion_data=emotion_data,
        base_response="",  # 如果没有基础回应
        user_context={"user_id": user_id}
    )
    
    # 更新数据库记录
    db = next(get_db())
    
    record = db.query(EmotionRecord).filter_by(
        user_id=user_id,
        user_input=text
    ).order_by(EmotionRecord.timestamp.desc()).first()
    
    if record:
        record.response = response.text
        db.commit()
    
    return response.to_dict()

# 使用示例
@app.post("/v1/emotion/analyze/async")
async def analyze_emotion_async_endpoint(
    request: EmotionRequest,
    user: User = Depends(get_current_user)
):
    """异步情感分析端点"""
    # 立即返回任务ID
    task = analyze_emotion_async.delay(
        text=request.text,
        user_id=user.id
    )
    
    return {
        "success": True,
        "task_id": task.id,
        "status": "processing",
        "message": "Analysis started. Use task_id to check status."
    }

@app.get("/v1/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """获取任务状态"""
    task = analyze_emotion_async.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'result': task.result if task.ready() else None
        }
    else:
        # task.state == 'FAILURE'
        response = {
            'state': task.state,
            'status': str(task.info)  # 异常信息
        }
    
    return response
```

## 10. 部署和运维

### 10.1 CI/CD流水线
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379/0
      run: |
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
  
  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/warm-agent-api:latest
          ${{ secrets.DOCKER_USERNAME }}/warm-agent-api:${{ github.sha }}
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to Kubernetes
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.K8S_HOST }}
        username: ${{ secrets.K8S_USERNAME }}
        key