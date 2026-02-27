# 📚 Warm Agent API 文档

## 概述

Warm Agent 提供完整的RESTful API，用于情感分析、温暖回应生成和情感记忆管理。

## 基础信息

- **基础URL**: `https://api.warm-agent.com/v1`
- **认证**: API Key认证，通过 `Authorization: Bearer YOUR_API_KEY` 头部传递
- **响应格式**: JSON
- **编码**: UTF-8

## 快速开始

### 获取API Key
1. 访问 [Warm Agent官网](https://warm-agent.com)
2. 注册账户
3. 在控制台获取API Key

### 免费额度
- **免费用户**: 每月1000次情感分析 + 500次温暖回应
- **专业版**: 无限调用 + 高级功能

## API端点

### 1. 情感分析

分析用户输入的情感状态。

**端点**: `POST /analyze/emotion`

**请求**:
```json
{
  "text": "今天工作压力好大，感觉有点焦虑",
  "language": "zh-CN",
  "detailed": false
}
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| text | string | 是 | 要分析的文本 |
| language | string | 否 | 语言代码，默认"zh-CN" |
| detailed | boolean | 否 | 是否返回详细分析，默认false |

**响应** (detailed=false):
```json
{
  "success": true,
  "data": {
    "primary_emotion": "anxiety",
    "intensity": 0.85,
    "secondary_emotions": ["stress", "tiredness"],
    "keywords": ["压力", "焦虑"],
    "suggested_response_type": "comforting"
  }
}
```

**响应** (detailed=true):
```json
{
  "success": true,
  "data": {
    "primary_emotion": "anxiety",
    "intensity": 0.85,
    "emotion_breakdown": {
      "anxiety": 0.85,
      "stress": 0.78,
      "tiredness": 0.65,
      "frustration": 0.42
    },
    "keywords": ["压力", "焦虑", "工作"],
    "triggers": ["工作压力", "时间紧迫"],
    "suggested_response_type": "comforting",
    "response_templates": [
      "听起来你今天工作很辛苦呢...",
      "压力大的时候确实需要放松一下"
    ]
  }
}
```

### 2. 温暖回应生成

将标准AI回应转化为温暖版本。

**端点**: `POST /generate/warm-response`

**请求**:
```json
{
  "user_input": "今天工作压力好大",
  "base_response": "建议你休息一下",
  "emotion_data": {
    "primary_emotion": "anxiety",
    "intensity": 0.85
  },
  "style": "caring",
  "include_emoji": true
}
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_input | string | 是 | 用户原始输入 |
| base_response | string | 是 | 基础AI回应 |
| emotion_data | object | 否 | 情感分析结果（如已分析） |
| style | string | 否 | 回应风格：caring/friendly/playful/professional |
| include_emoji | boolean | 否 | 是否包含emoji，默认true |

**响应**:
```json
{
  "success": true,
  "data": {
    "warm_response": "听起来你今天工作很辛苦呢...💼 压力大的时候确实需要放松一下。要不要试试听点轻松的音乐？我在这里陪着你✨",
    "enhancement_type": "emotional_support",
    "added_elements": ["empathy", "suggestion", "companionship"],
    "emoji_used": ["💼", "✨"]
  }
}
```

### 3. 关键词触发检测

检测用户输入是否包含情感关键词，应触发温暖模式。

**端点**: `POST /detect/triggers`

**请求**:
```json
{
  "text": "今天心情有点低落，需要一些安慰",
  "check_emotion": true
}
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| text | string | 是 | 要检测的文本 |
| check_emotion | boolean | 否 | 是否进行情感分析，默认true |

**响应**:
```json
{
  "success": true,
  "data": {
    "should_trigger": true,
    "trigger_type": "explicit_keyword",
    "keywords_found": ["心情", "低落", "安慰"],
    "emotion_if_checked": {
      "primary_emotion": "sadness",
      "intensity": 0.72
    },
    "suggested_action": "switch_to_warm_mode"
  }
}
```

### 4. 情感记忆管理

存储和检索用户的情感历史。

**端点**: `POST /memory/store`

**请求**:
```json
{
  "user_id": "user_123",
  "interaction": {
    "timestamp": "2026-02-27T12:00:00Z",
    "user_input": "今天工作压力好大",
    "emotion_data": {
      "primary_emotion": "anxiety",
      "intensity": 0.85
    },
    "response_given": "听起来你今天工作很辛苦呢..."
  },
  "tags": ["work", "stress", "weekday"]
}
```

**端点**: `GET /memory/retrieve?user_id=user_123&limit=10`

**响应**:
```json
{
  "success": true,
  "data": {
    "user_id": "user_123",
    "memory_count": 15,
    "recent_interactions": [
      {
        "timestamp": "2026-02-27T12:00:00Z",
        "primary_emotion": "anxiety",
        "intensity": 0.85,
        "summary": "工作压力大，感到焦虑"
      }
    ],
    "emotional_patterns": {
      "most_common_emotion": "anxiety",
      "peak_hours": ["10:00", "15:00"],
      "common_triggers": ["work", "deadlines"]
    }
  }
}
```

### 5. 智声云配集成

将文本转换为情感语音（需要专业版）。

**端点**: `POST /voice/generate`

**请求**:
```json
{
  "text": "听起来你今天工作很辛苦呢，压力大的时候确实需要放松一下。",
  "emotion": "caring",
  "voice_type": "female_warm",
  "output_format": "mp3"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "audio_url": "https://cdn.warm-agent.com/audio/abc123.mp3",
    "duration_seconds": 8.5,
    "emotion_applied": "caring",
    "expires_at": "2026-02-28T12:00:00Z"
  }
}
```

## 错误处理

### 错误响应格式
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API调用次数超出限制",
    "details": {
      "limit": 1000,
      "used": 1000,
      "reset_at": "2026-03-01T00:00:00Z"
    }
  }
}
```

### 常见错误码
| 错误码 | HTTP状态 | 说明 |
|--------|-----------|------|
| INVALID_API_KEY | 401 | API Key无效或过期 |
| RATE_LIMIT_EXCEEDED | 429 | 调用次数超出限制 |
| INSUFFICIENT_QUOTA | 402 | 额度不足（需要升级） |
| INVALID_PARAMETERS | 400 | 参数无效 |
| SERVICE_UNAVAILABLE | 503 | 服务暂时不可用 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

## 速率限制

### 免费用户
- **情感分析**: 1000次/月
- **温暖回应**: 500次/月
- **请求频率**: 10次/分钟

### 专业版用户
- **情感分析**: 无限制
- **温暖回应**: 无限制  
- **请求频率**: 60次/分钟

### 头部信息
响应中包含速率限制信息：
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 850
X-RateLimit-Reset: 1735689600
```

## SDK和客户端

### Python SDK
```python
pip install warm-agent
```

### JavaScript SDK
```bash
npm install warm-agent
```

### OpenClaw集成
```yaml
skills:
  warm-agent:
    enabled: true
    apiKey: "your_api_key"
```

## 更新日志

### v1.0.0 (2026-02-27)
- 初始版本发布
- 基础情感分析和温暖回应生成
- 关键词触发检测
- 基础情感记忆

### v1.1.0 (计划中)
- 智声云配语音集成
- 高级情感模式识别
- 多语言支持
- 性能优化

## 支持与联系

- **技术支持**: support@warm-agent.com
- **文档**: https://docs.warm-agent.com
- **GitHub**: https://github.com/warm-agent/warm-agent
- **社区**: https://discord.gg/warm-agent