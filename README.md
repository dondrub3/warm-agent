# Warm Agent 🌟

**为AI注入温度与情感的开源项目**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-20.10%2B-blue)](https://www.docker.com/)
[![Code Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)](https://codecov.io/gh/dondrub3/warm-agent)

## ✨ 特性

### 🧠 情感智能
- **多层级情感分析**：关键词匹配 + 上下文理解 + 强度计算
- **丰富的情感词库**：支持6种基础情感和多种复杂情感
- **智能需求识别**：自动识别用户的情感需求和支持需求

### ❤️ 温暖回应
- **同理心表达**：生成有温度、有同理心的回应
- **个性化适配**：根据用户偏好调整回应风格
- **模板系统**：可扩展的回应模板库

### 🔌 无缝集成
- **OpenClaw 集成**：作为技能无缝集成到OpenClaw
- **RESTful API**：提供完整的API服务
- **WebSocket 支持**：实时情感分析和回应

### 🚀 企业级特性
- **高性能**：异步处理、缓存优化、数据库分区
- **可扩展**：微服务架构，支持水平扩展
- **监控告警**：完整的监控体系和告警系统
- **安全可靠**：API认证、数据加密、网络安全

## 📦 快速开始

### 使用 Docker（推荐）

```bash
# 克隆项目
git clone https://github.com/dondrub3/warm-agent.git
cd warm-agent

# 启动开发环境
docker-compose up -d

# 访问API文档
open http://localhost:8000/docs

# 运行测试
docker-compose run --rm test
```

### 手动安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn src.api.main:app --reload
```

## 🏗️ 架构设计

### 核心模块

```
┌─────────────────────────────────────────┐
│            Warm Agent 架构               │
├─────────────────────────────────────────┤
│  API层 (FastAPI)                        │
│  ├── 情感分析端点                        │
│  ├── 温暖回应端点                        │
│  └── OpenClaw集成端点                    │
├─────────────────────────────────────────┤
│  核心业务层                              │
│  ├── 情感分析引擎 (EmotionAnalyzer)      │
│  ├── 温暖回应引擎 (WarmResponseEngine)   │
│  └── 情感记忆系统 (EmotionMemorySystem)  │
├─────────────────────────────────────────┤
│  数据访问层                              │
│  ├── PostgreSQL (情感记录)               │
│  ├── Redis (缓存)                        │
│  └── 文件存储 (日志/模型)                 │
├─────────────────────────────────────────┤
│  基础设施层                              │
│  ├── Docker容器化                        │
│  ├── 监控告警 (Prometheus+Grafana)       │
│  └── CI/CD流水线                         │
└─────────────────────────────────────────┘
```

### 情感分析流程

```python
# 情感分析示例
from warm_agent.core.emotion_analyzer import get_emotion_analyzer

analyzer = get_emotion_analyzer()
result = analyzer.analyze("今天工作压力好大")

print(f"主要情感: {result.primary_emotion}")      # anxiety
print(f"情感强度: {result.intensity}")           # 0.85
print(f"需要支持: {result.needs_support}")       # True
print(f"建议回应: {result.suggested_response}")  # "听到你提到压力..."
```

### 温暖回应生成

```python
# 温暖回应生成示例
from warm_agent.core.warm_response_engine import get_warm_response_engine

engine = get_warm_response_engine()
response = engine.generate(
    emotion_result=result,
    base_response="建议你休息一下",
    user_context={"preferences": {"style": "warm"}}
)

print(f"温暖回应: {response.text}")
print(f"温暖度分数: {response.warmth_score}")  # 0.78
```

## 🔌 集成指南

### OpenClaw 集成

Warm Agent 可以作为 OpenClaw 的技能无缝集成：

```python
# OpenClaw技能配置
from warm_agent.integrations.openclaw import get_openclaw_integration

config = {
    "openclaw": {
        "auto_detect": True,
        "enhance_all": False,
        "default_warm_mode": False
    }
}

integration = get_openclaw_integration(config)

# 处理OpenClaw消息
result = integration.process_message(
    message=OpenClawMessage(
        content="今天心情不好",
        base_response="建议听听音乐"
    ),
    context=OpenClawContext(
        user_id="user_123",
        channel="qqbot"
    )
)

print(f"增强回应: {result.enhanced_response}")
```

### RESTful API

Warm Agent 提供完整的 RESTful API：

```bash
# 情感分析
curl -X POST "http://localhost:8000/v1/emotion/analyze" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"text": "今天很开心"}'

# 温暖回应生成
curl -X POST "http://localhost:8000/v1/warm-response/generate" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "今天工作压力大",
    "base_response": "建议休息一下"
  }'
```

## 📊 API 文档

### 主要端点

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/v1/emotion/analyze` | POST | 情感分析 | ✅ |
| `/v1/warm-response/generate` | POST | 温暖回应生成 | ✅ |
| `/v1/openclaw/process` | POST | OpenClaw集成 | ✅ |
| `/v1/user/{user_id}/summary` | GET | 用户情感摘要 | ✅ |
| `/v1/batch/emotion/analyze` | POST | 批量情感分析 | ✅ |
| `/health` | GET | 健康检查 | ❌ |
| `/metrics` | GET | Prometheus指标 | ❌ |

### 请求示例

```json
{
  "text": "今天工作压力好大",
  "language": "zh-CN",
  "context": {
    "previous_emotions": ["stress"],
    "time_of_day": "morning"
  }
}
```

### 响应示例

```json
{
  "success": true,
  "data": {
    "primary_emotion": "anxiety",
    "secondary_emotions": ["stress", "tiredness"],
    "intensity": 0.85,
    "confidence": 0.92,
    "keywords": ["压力", "大"],
    "context_hints": ["工作", "职场"],
    "needs_support": true,
    "suggested_response": "听到你提到压力，我也跟着有点担心呢...😔"
  },
  "metadata": {
    "user_id": "user_123",
    "timestamp": "2024-02-28T10:30:00Z"
  }
}
```

## 🚀 部署方案

### 单机部署（开发）

```bash
# 使用Docker Compose
docker-compose up -d

# 访问服务
# API: http://localhost:8000
# API文档: http://localhost:8000/docs
# Grafana: http://localhost:3000 (admin/admin)
```

### Kubernetes 部署（生产）

```bash
# 应用Kubernetes配置
kubectl apply -f k8s/

# 检查部署状态
kubectl get all -n warm-agent

# 获取Ingress地址
kubectl get ingress -n warm-agent
```

### 云平台部署

- **AWS**: ECS/Fargate + RDS + ElastiCache
- **Google Cloud**: Cloud Run + Cloud SQL + Memorystore
- **Azure**: Container Instances + Azure SQL + Redis Cache

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_core.py -v

# 运行测试并生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 在Docker中运行测试
docker-compose run --rm test
```

### 测试覆盖率

```
tests/test_core.py .................. 100%
tests/test_api.py ................... 100%
tests/test_integrations.py .......... 95%
-----------------------------------------
TOTAL .............................. 98%
```

## 📈 监控和告警

### 监控指标

- **API性能**: 请求率、响应时间、错误率
- **业务指标**: 情感分析分布、温暖度分数、用户互动
- **系统指标**: CPU、内存、磁盘、网络
- **数据库指标**: 连接数、查询性能、缓存命中率

### 告警规则

```yaml
# 高错误率告警
- alert: HighErrorRate
  expr: rate(api_requests_total{status=~"5.."}[5m]) > 0.05
  for: 5m
  labels:
    severity: critical

# 高延迟告警
- alert: HighLatency
  expr: histogram_quantile(0.95, rate(request_duration_seconds_bucket[5m])) > 2
  for: 10m
  labels:
    severity: warning
```

## 🔧 配置管理

### 环境变量

| 变量名 | 描述 | 默认值 | 必需 |
|--------|------|--------|------|
| `DATABASE_URL` | 数据库连接URL | - | ✅ |
| `REDIS_URL` | Redis连接URL | - | ✅ |
| `API_KEY_SECRET` | API密钥加密密钥 | - | ✅ |
| `ENVIRONMENT` | 环境 (development/production) | development | ❌ |
| `LOG_LEVEL` | 日志级别 | INFO | ❌ |
| `CORS_ORIGINS` | CORS允许的源 | * | ❌ |

### 配置文件

```yaml
# config/production.yaml
database:
  url: ${DATABASE_URL}
  pool_size: 20

redis:
  url: ${REDIS_URL}
  pool_size: 10

api:
  port: 8000
  workers: 4

security:
  api_key_secret: ${API_KEY_SECRET}
  rate_limit: 100/分钟
```

## 🤝 贡献指南

我们欢迎各种形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与。

### 开发流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加新功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 代码规范

- 使用 Black 进行代码格式化
- 使用 Flake8 进行代码检查
- 使用 MyPy 进行类型检查
- 遵循 Conventional Commits

## 📚 文档

- [开发指南](DEVELOPMENT_GUIDE.md) - 详细的开发说明
- [部署方案](DEPLOYMENT.md) - 各种部署方案
- [OpenClaw集成](docs/openclaw-integration/README.md) - OpenClaw集成指南
- [API文档](http://localhost:8000/docs) - 交互式API文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为这个项目做出贡献的人！

- **东周** - 项目发起人和主要开发者
- **OpenClaw社区** - 提供了优秀的AI助手平台
- **所有贡献者** - 感谢你们的代码、文档和反馈

## 📞 支持

- **问题反馈**: [GitHub Issues](https://github.com/dondrub3/warm-agent/issues)
- **讨论交流**: [GitHub Discussions](https://github.com/dondrub3/warm-agent/discussions)
- **文档**: [项目Wiki](https://github.com/dondrub3/warm-agent/wiki)

## 🌟 Star 历史

[![Star History Chart](https://api.star-history.com/svg?repos=dondrub3/warm-agent&type=Date)](https://star-history.com/#dondrub3/warm-agent&Date)

---

**让AI更有温度，让世界更温暖** ❤️

如果你喜欢这个项目，请给它一个 ⭐️！