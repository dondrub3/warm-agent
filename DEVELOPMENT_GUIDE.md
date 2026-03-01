# Warm Agent 开发指南

## 项目概述

Warm Agent 是一个为AI助手添加情感智能的开源项目。它让冰冷的AI回应变得温暖、有同理心，真正理解用户的情感需求。

## 开发环境设置

### 1. 系统要求

- Python 3.8+
- PostgreSQL 15+
- Redis 7+
- Docker 和 Docker Compose（可选）

### 2. 快速开始

#### 使用 Docker Compose（推荐）

```bash
# 克隆项目
git clone https://github.com/dondrub3/warm-agent.git
cd warm-agent

# 启动开发环境
docker-compose up -d

# 查看日志
docker-compose logs -f api

# 运行测试
docker-compose run --rm test
```

#### 手动安装

```bash
# 克隆项目
git clone https://github.com/dondrub3/warm-agent.git
cd warm-agent

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt -r requirements-dev.txt

# 设置环境变量
export DATABASE_URL=postgresql://postgres:password@localhost:5432/warm_agent
export REDIS_URL=redis://localhost:6379/0

# 启动服务
uvicorn src.api.main:app --reload
```

### 3. 数据库设置

```bash
# 创建数据库
createdb warm_agent

# 运行迁移（如果使用Alembic）
alembic upgrade head

# 创建测试数据库
createdb warm_agent_test
```

## 项目结构

```
warm-agent/
├── src/                    # 源代码
│   ├── api/               # API层
│   │   └── main.py        # FastAPI主应用
│   ├── core/              # 核心业务逻辑
│   │   ├── emotion_analyzer.py    # 情感分析引擎
│   │   ├── warm_response_engine.py # 温暖回应引擎
│   │   └── triggers.py    # 触发器系统
│   ├── integrations/      # 集成模块
│   │   └── openclaw.py    # OpenClaw集成
│   ├── models/            # 数据模型
│   ├── services/          # 业务服务
│   ├── tasks/             # 异步任务
│   └── utils/             # 工具函数
├── tests/                 # 测试代码
├── docs/                  # 文档
├── migrations/            # 数据库迁移
├── monitoring/            # 监控配置
├── docker-compose.yml     # Docker Compose配置
├── Dockerfile            # Docker配置
├── requirements.txt      # 生产依赖
├── requirements-dev.txt  # 开发依赖
└── setup.py             # 安装脚本
```

## 核心模块开发

### 1. 情感分析引擎

#### 架构设计

情感分析引擎采用多层级分析策略：

1. **关键词匹配层**：快速识别情感关键词
2. **上下文分析层**：分析文本上下文和用户历史
3. **强度计算层**：计算情感强度
4. **需求识别层**：识别用户需求

#### 扩展情感词库

编辑 `src/core/emotion_analyzer.py` 中的情感词库：

```python
# 添加新的情感类别
self.emotion_categories["new_category"] = {
    "emotion_type": ["关键词1", "关键词2", "关键词3"]
}

# 添加新的需求类别
self.need_categories["new_need"] = ["需求词1", "需求词2"]
```

#### 添加新的分析规则

```python
def _custom_analysis_rule(self, text: str, keyword_results: Dict) -> Dict:
    """自定义分析规则"""
    # 实现自定义分析逻辑
    pass
```

### 2. 温暖回应引擎

#### 模板系统

温暖回应引擎使用模板系统生成回应：

```python
# 添加新的回应模板
self.templates["new_emotion_low"] = [
    "模板1 {keyword}",
    "模板2 {keyword}"
]

self.templates["new_emotion_high"] = [
    "高强度模板1 {keyword}",
    "高强度模板2 {keyword}"
]
```

#### 个性化适配

个性化适配器根据用户偏好调整回应：

```python
# 添加新的个性化规则
def _custom_personalization(self, text: str, user_context: Dict) -> str:
    """自定义个性化规则"""
    # 实现自定义个性化逻辑
    pass
```

### 3. OpenClaw 集成

#### 集成配置

编辑 `src/integrations/openclaw.py` 中的配置：

```python
config = {
    "openclaw": {
        "auto_detect": True,      # 自动检测情感
        "enhance_all": False,     # 增强所有回应
        "default_warm_mode": False # 默认温暖模式
    }
}
```

#### 添加新的触发器

```python
# 在WarmAgentTriggers中添加新的触发词
self.trigger_words["new_category"] = ["触发词1", "触发词2"]
```

## API 开发

### 1. 添加新的API端点

```python
# 在 src/api/main.py 中添加新端点
@app.post("/v1/new-endpoint")
async def new_endpoint(
    request: NewRequestModel,
    user: Dict = Depends(get_current_user)
):
    """新端点描述"""
    try:
        # 业务逻辑
        result = await some_service.process(request)
        
        return {
            "success": True,
            "data": result,
            "metadata": {
                "user_id": user["user_id"],
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理失败: {str(e)}"
        )
```

### 2. 数据模型验证

使用Pydantic进行数据验证：

```python
from pydantic import BaseModel, Field, validator

class NewRequestModel(BaseModel):
    """新请求模型"""
    field1: str = Field(..., min_length=1, max_length=100)
    field2: int = Field(..., ge=0, le=100)
    
    @validator('field1')
    def validate_field1(cls, v):
        # 自定义验证逻辑
        if "invalid" in v:
            raise ValueError("字段包含无效内容")
        return v
```

## 测试开发

### 1. 单元测试

```python
# tests/test_new_module.py
import pytest
from src.core.new_module import NewModule

class TestNewModule:
    """新模块测试"""
    
    @pytest.fixture
    def module(self):
        return NewModule()
    
    def test_feature(self, module):
        """测试功能"""
        result = module.process("输入")
        assert result == "预期输出"
    
    @pytest.mark.parametrize("input,expected", [
        ("输入1", "输出1"),
        ("输入2", "输出2"),
    ])
    def test_multiple_cases(self, module, input, expected):
        """多用例测试"""
        result = module.process(input)
        assert result == expected
```

### 2. 集成测试

```python
# tests/test_api_integration.py
from fastapi.testclient import TestClient

def test_new_endpoint(client):
    """测试新端点"""
    headers = {"X-API-Key": "test_api_key"}
    data = {"field1": "测试", "field2": 50}
    
    response = client.post("/v1/new-endpoint",
                          json=data,
                          headers=headers)
    
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
```

### 3. 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_core.py -v

# 运行测试并生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 运行Docker中的测试
docker-compose run --rm test
```

## 数据库开发

### 1. 数据模型

```python
# src/models/user.py
from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    preferences = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 2. 数据库迁移

```bash
# 创建新迁移
alembic revision --autogenerate -m "添加新表"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 部署

### 1. 开发环境部署

```bash
# 使用Docker Compose
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f api
```

### 2. 生产环境部署

#### 使用Docker

```bash
# 构建生产镜像
docker build -t warm-agent-api:latest -f Dockerfile --target production .

# 运行容器
docker run -d \
  --name warm-agent-api \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@host:5432/db \
  -e REDIS_URL=redis://host:6379/0 \
  warm-agent-api:latest
```

#### 使用Kubernetes

```bash
# 应用Kubernetes配置
kubectl apply -f k8s/

# 查看部署状态
kubectl get pods,svc,ingress
```

### 3. 环境变量配置

| 变量名 | 描述 | 默认值 | 必需 |
|--------|------|--------|------|
| DATABASE_URL | 数据库连接URL | - | 是 |
| REDIS_URL | Redis连接URL | - | 是 |
| API_KEY_SECRET | API密钥加密密钥 | - | 是 |
| ENVIRONMENT | 环境 (development/production) | development | 否 |
| LOG_LEVEL | 日志级别 | INFO | 否 |
| CORS_ORIGINS | CORS允许的源 | * | 否 |

## 监控和日志

### 1. 日志配置

```python
# src/utils/logger.py
import structlog

logger = structlog.get_logger()

# 使用日志
logger.info("处理请求", user_id=user_id, endpoint=endpoint)
logger.error("处理失败", error=str(e), user_id=user_id)
```

### 2. 监控指标

```python
# src/utils/metrics.py
from prometheus_client import Counter, Histogram

# 定义指标
API_REQUESTS = Counter('api_requests_total', 'Total API requests', ['endpoint', 'method'])
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration', ['endpoint'])

# 记录指标
API_REQUESTS.labels(endpoint='/v1/emotion/analyze', method='POST').inc()
```

### 3. 健康检查

```bash
# 检查API健康
curl http://localhost:8000/health

# 检查数据库连接
curl http://localhost:8000/health/db

# 检查Redis连接
curl http://localhost:8000/health/redis
```

## 代码规范

### 1. 代码风格

- 使用Black进行代码格式化
- 使用Flake8进行代码检查
- 使用MyPy进行类型检查

```bash
# 格式化代码
black src/ tests/

# 检查代码
flake8 src/ tests/

# 类型检查
mypy src/
```

### 2. 提交规范

使用Conventional Commits：

```
feat: 添加新功能
fix: 修复bug
docs: 更新文档
style: 代码格式调整
refactor: 代码重构
test: 添加或修改测试
chore: 构建过程或辅助工具的变动
```

### 3. 分支策略

- `main`: 生产环境代码
- `develop`: 开发分支
- `feature/*`: 功能分支
- `bugfix/*`: Bug修复分支
- `release/*`: 发布分支

## 故障排除

### 1. 常见问题

#### 数据库连接失败

```bash
# 检查数据库服务
docker-compose ps postgres

# 检查连接
psql -h localhost -U postgres -d warm_agent

# 查看日志
docker-compose logs postgres
```

#### Redis连接失败

```bash
# 检查Redis服务
docker-compose ps redis

# 测试连接
redis-cli -h localhost ping

# 查看日志
docker-compose logs redis
```

#### API服务启动失败

```bash
# 查看错误日志
docker-compose logs api

# 检查依赖
pip list | grep fastapi

# 检查端口占用
lsof -i :8000
```

### 2. 调试技巧

```python
# 启用调试模式
import pdb; pdb.set_trace()

# 使用日志调试
import logging
logging.basicConfig(level=logging.DEBUG)

# 使用环境变量
import os
print(os.environ.get('DATABASE_URL'))
```

## 贡献指南

### 1. 如何贡献

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加新功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

### 2. 代码审查

- 确保代码通过所有测试
- 遵循代码规范
- 添加适当的文档
- 更新CHANGELOG.md

### 3. 报告问题

使用GitHub Issues报告问题，包括：
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息

## 学习资源

### 1. 相关技术

- [FastAPI文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- [Redis文档](https://redis.io/documentation)
- [Docker文档](https://docs.docker.com/)
- [Kubernetes文档](https://kubernetes.io/docs/)

### 2. 情感分析

- [情感分析基础](https://en.wikipedia.org/wiki/Sentiment_analysis)
- [自然语言处理](https://www.nltk.org/)
- [情感词典](https://sentiwordnet.isti.cnr.it/)

### 3. 社区支持

- [GitHub Discussions](https://github.com/dondrub3/warm-agent/discussions)
- [Discord频道](https://discord.gg/your-channel)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/warm-agent)

---

**Happy Coding!** 🚀

如果你有任何问题或建议，请随时联系我们或提交Issue。