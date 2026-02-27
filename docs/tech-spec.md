# 技术规格 Tech Spec 🔧

## 系统架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                         用户层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  QQ Bot     │  │  微信 Bot   │  │  Web App           │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼────────────────────┼────────────┘
          │                │                    │
          └────────────────┴────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────┐
│                      接入层 │                                │
│  ┌─────────────────────────┴──────────────────────────────┐ │
│  │              API Gateway (OpenClaw)                    │ │
│  │  • 统一接入管理  • 身份认证  • 限流保护                 │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────┐
│                      服务层 │                                │
│  ┌─────────────────────────┴──────────────────────────────┐ │
│  │                    核心服务                             │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │          语音情绪分析服务                        │  │ │
│  │  │  • 音频上传  • 情绪识别  • 特征提取              │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  │                                                         │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │          情感记忆引擎                            │  │ │
│  │  │  • 记忆存储  • 检索匹配  • 模式学习              │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  │                                                         │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │          共情生成服务                            │  │ │
│  │  │  • 策略选择  • 回应生成  • 情感合成              │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────┐
│                      数据层 │                                │
│  ┌─────────────────────────┴──────────────────────────────┐ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │ PostgreSQL  │  │   Milvus    │  │    Redis    │    │ │
│  │  │  结构化数据  │  │  向量数据库  │  │   缓存层    │    │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────┐
│                      外部服务 │                              │
│  ┌─────────────────────────┴──────────────────────────────┐ │
│  │  智声云配 API  │  阿里云 OSS  │  腾讯云 TTS  │         │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## 核心模块设计

### 1. 语音情绪分析模块

#### 接口设计

```typescript
interface VoiceEmotionAnalyzer {
  // 分析音频情绪
  analyze(audioBuffer: Buffer): Promise<EmotionResult>;
  
  // 批量分析
  analyzeBatch(audioBuffers: Buffer[]): Promise<EmotionResult[]>;
  
  // 实时流分析（WebSocket）
  createStream(): EmotionStream;
}

interface EmotionResult {
  // 基础信息
  audioId: string;
  timestamp: number;
  duration: number;
  
  // 情绪识别结果
  emotion: {
    primary: EmotionType;      // 主要情绪
    secondary?: EmotionType;   // 次要情绪
    intensity: number;         // 强度 0-1
    confidence: number;        // 置信度
  };
  
  // 声学特征
  features: {
    pitch: {
      mean: number;      // 平均音高 (Hz)
      variation: number; // 音高变化
    };
    energy: {
      mean: number;      // 平均能量 (dB)
      variation: number; // 能量变化
    };
    speed: {
      wordsPerMinute: number;  // 语速
      pausePattern: number[];  // 停顿模式
    };
    tone: {
      contour: string;   // 语调轮廓
      emotionality: number; // 情绪色彩
    };
  };
  
  // 原始数据（用于调试）
  raw: {
    waveform: number[];  // 波形数据
    spectrogram: any;    // 频谱图
  };
}

type EmotionType = 
  | 'happy' | 'excited' | 'content'      // 正向
  | 'calm' | 'neutral'                   // 中性
  | 'sad' | 'tired' | 'frustrated'       // 负向低能量
  | 'angry' | 'anxious' | 'stressed';    // 负向高能量
```

#### 实现方案

**方案A: 直接使用智声云配API**
```javascript
class ZhishangYunpeiAnalyzer {
  async analyze(audioBuffer) {
    const response = await fetch('https://api.zhishangyunpei.com/v1/analyze', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${API_KEY}` },
      body: audioBuffer
    });
    return this.normalizeResult(await response.json());
  }
}
```

**方案B: 多引擎融合（推荐）**
```javascript
class HybridEmotionAnalyzer {
  async analyze(audioBuffer) {
    // 并行调用多个引擎
    const [zhishangResult, localResult] = await Promise.all([
      this.zhishang.analyze(audioBuffer),
      this.localModel.analyze(audioBuffer)
    ]);
    
    // 加权融合结果
    return this.fuseResults(zhishangResult, localResult);
  }
}
```

---

### 2. 情感记忆引擎

#### 数据模型

```typescript
// 情感记忆实体
interface EmotionMemory {
  id: string;
  userId: string;
  
  // 时间信息
  createdAt: Date;
  updatedAt: Date;
  
  // 内容信息
  content: {
    text: string;           // 转录文本
    summary: string;        // AI摘要
    topics: string[];       // 话题标签
    intent: string;         // 意图识别
  };
  
  // 情绪信息
  emotion: {
    primary: EmotionType;
    intensity: number;
    valence: number;        // 正负向 -1 to 1
    arousal: number;        // 激活度 0 to 1
    features: EmotionFeatures;
  };
  
  // 上下文信息
  context: {
    timeOfDay: 'morning' | 'afternoon' | 'evening' | 'night';
    dayOfWeek: number;
    location?: string;
    activity?: string;
    relatedMemories?: string[];
  };
  
  // 向量表示（用于相似度检索）
  embedding: number[];      // 768维向量
  
  // 元数据
  meta: {
    importance: number;     // 重要程度 0-1
    recallCount: number;    // 被回忆次数
    lastRecalled?: Date;
    isKeyMemory: boolean;   // 是否关键记忆
  };
}

// 情绪模式（聚合分析结果）
interface EmotionPattern {
  userId: string;
  topic: string;
  
  // 情绪分布
  distribution: {
    emotion: EmotionType;
    count: number;
    avgIntensity: number;
  }[];
  
  // 时间模式
  temporalPattern: {
    hourOfDay: number;      // 一天中什么时间容易出现
    dayOfWeek: number;      // 一周中哪一天
  };
  
  // 触发因素
  triggers: string[];
  
  // 有效应对策略（学习得到）
  effectiveResponses: {
    strategy: string;
    successRate: number;
    usedCount: number;
  }[];
}
```

#### 核心算法

**1. 记忆存储**
```javascript
class EmotionMemoryStore {
  async store(memory: EmotionMemory): Promise<void> {
    // 1. 生成向量嵌入
    memory.embedding = await this.generateEmbedding(memory);
    
    // 2. 存入PostgreSQL
    await this.pg.insert('emotion_memories', memory);
    
    // 3. 存入Milvus（向量检索）
    await this.milvus.insert({
      id: memory.id,
      vector: memory.embedding,
      userId: memory.userId
    });
    
    // 4. 更新情绪模式
    await this.updateEmotionPattern(memory);
  }
  
  private async generateEmbedding(memory: EmotionMemory): Promise<number[]> {
    // 使用文本+情绪特征生成嵌入
    const text = `${memory.content.text} ${memory.emotion.primary} ${memory.content.topics.join(' ')}`;
    return await this.embeddingModel.encode(text);
  }
}
```

**2. 记忆检索**
```javascript
class EmotionMemoryRetriever {
  // 相似情绪检索
  async retrieveSimilar(userId: string, queryMemory: EmotionMemory, limit: number = 5): Promise<EmotionMemory[]> {
    const embedding = await this.generateEmbedding(queryMemory);
    
    // Milvus向量检索
    const similarIds = await this.milvus.search({
      vector: embedding,
      filter: `userId == "${userId}"`,
      topK: limit * 2  // 多取一些用于重排序
    });
    
    // 获取完整记忆
    const memories = await this.pg.query(
      'SELECT * FROM emotion_memories WHERE id = ANY($1)',
      [similarIds]
    );
    
    // 重排序：考虑时间衰减、重要性
    return this.rerank(memories, queryMemory).slice(0, limit);
  }
  
  // 话题相关检索
  async retrieveByTopic(userId: string, topic: string, limit: number = 5): Promise<EmotionMemory[]> {
    return await this.pg.query(`
      SELECT * FROM emotion_memories 
      WHERE userId = $1 AND $2 = ANY(topics)
      ORDER BY createdAt DESC
      LIMIT $3
    `, [userId, topic, limit]);
  }
}
```

**3. 模式学习**
```javascript
class EmotionPatternLearner {
  // 学习用户的情绪模式
  async learnPatterns(userId: string): Promise<EmotionPattern[]> {
    const memories = await this.getAllMemories(userId);
    
    // 按话题聚类
    const clusters = this.clusterByTopic(memories);
    
    // 分析每个话题的情绪模式
    return clusters.map(cluster => ({
      userId,
      topic: cluster.topic,
      distribution: this.analyzeDistribution(cluster.memories),
      temporalPattern: this.analyzeTemporalPattern(cluster.memories),
      triggers: this.extractTriggers(cluster.memories),
      effectiveResponses: this.learnEffectiveResponses(cluster.memories)
    }));
  }
}
```

---

### 3. 共情生成模块

#### 策略体系

```typescript
interface EmpathyStrategy {
  id: string;
  name: string;
  
  // 触发条件
  conditions: {
    emotionType?: EmotionType[];
    intensityRange?: [number, number];
    topicContains?: string[];
    contextMatches?: ContextCondition[];
  };
  
  // 回应模板
  responseTemplates: {
    template: string;
    weight: number;
    conditions?: {
      memoryRecalled?: boolean;
      patternKnown?: boolean;
    };
  }[];
  
  // 行动建议
  suggestedActions?: {
    type: 'breathing' | 'music' | 'walk' | 'talk' | 'rest';
    description: string;
  }[];
  
  // 效果追踪
  effectiveness: {
    usedCount: number;
    positiveFeedback: number;
    negativeFeedback: number;
  };
}

// 共情策略库（部分示例）
const empathyStrategies: EmpathyStrategy[] = [
  {
    id: 'anxiety-comfort',
    name: '焦虑安抚策略',
    conditions: {
      emotionType: ['anxious', 'stressed'],
      intensityRange: [0.5, 1.0]
    },
    responseTemplates: [
      {
        template: '我能感受到你现在很焦虑，这种感觉确实不好受。',
        weight: 0.3
      },
      {
        template: '你上次遇到类似情况时，通过{{lastSolution}}调整过来了，这次也可以试试。',
        weight: 0.4,
        conditions: { memoryRecalled: true }
      },
      {
        template: '根据你的历史数据，这种焦虑通常在30分钟后会自然缓解，要不我们先深呼吸几分钟？',
        weight: 0.3,
        conditions: { patternKnown: true }
      }
    ],
    suggestedActions: [
      { type: 'breathing', description: '3分钟深呼吸练习' },
      { type: 'music', description: '播放你收藏的超然音乐' }
    ]
  },
  // ... 更多策略
];
```

#### 生成流程

```javascript
class EmpathyGenerator {
  async generate(userId: string, currentInput: UserInput): Promise<EmpathyResponse> {
    // 1. 分析当前情绪
    const currentEmotion = await this.analyzeEmotion(currentInput);
    
    // 2. 检索相关记忆
    const similarMemories = await this.memoryRetriever.retrieveSimilar(
      userId, 
      currentInput,
      3
    );
    
    // 3. 获取情绪模式
    const pattern = await this.getEmotionPattern(userId, currentInput.topic);
    
    // 4. 选择策略
    const strategy = this.selectStrategy(currentEmotion, pattern);
    
    // 5. 填充模板
    const response = this.fillTemplate(strategy, {
      emotion: currentEmotion,
      memories: similarMemories,
      pattern: pattern,
      userName: await this.getUserName(userId)
    });
    
    // 6. 添加行动建议
    const actions = this.suggestActions(strategy, currentEmotion);
    
    return {
      text: response,
      actions: actions,
      strategy: strategy.id,
      confidence: this.calculateConfidence(currentEmotion, similarMemories)
    };
  }
  
  private fillTemplate(template: string, context: RenderContext): string {
    return template
      .replace('{{userName}}', context.userName)
      .replace('{{emotion}}', this.translateEmotion(context.emotion.primary))
      .replace('{{lastSolution}}', this.extractLastSolution(context.memories))
      .replace('{{patternInsight}}', this.generateInsight(context.pattern));
  }
}
```

---

## 数据存储方案

### PostgreSQL 表结构

```sql
-- 情感记忆表
CREATE TABLE emotion_memories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id VARCHAR(64) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- 内容
  content_text TEXT,
  content_summary TEXT,
  content_topics TEXT[],
  content_intent VARCHAR(64),
  
  -- 情绪
  emotion_primary VARCHAR(32),
  emotion_secondary VARCHAR(32),
  emotion_intensity FLOAT CHECK (emotion_intensity BETWEEN 0 AND 1),
  emotion_valence FLOAT CHECK (emotion_valence BETWEEN -1 AND 1),
  emotion_arousal FLOAT CHECK (emotion_arousal BETWEEN 0 AND 1),
  emotion_features JSONB,
  
  -- 上下文
  context_time_of_day VARCHAR(16),
  context_day_of_week INTEGER CHECK (context_day_of_week BETWEEN 0 AND 6),
  context_location VARCHAR(128),
  context_activity VARCHAR(128),
  context_related_memories UUID[],
  
  -- 元数据
  meta_importance FLOAT DEFAULT 0.5,
  meta_recall_count INTEGER DEFAULT 0,
  meta_last_recalled TIMESTAMP WITH TIME ZONE,
  meta_is_key_memory BOOLEAN DEFAULT FALSE
);

-- 索引
CREATE INDEX idx_memories_user_time ON emotion_memories(user_id, created_at DESC);
CREATE INDEX idx_memories_emotion ON emotion_memories(user_id, emotion_primary, emotion_intensity);
CREATE INDEX idx_memories_topics ON emotion_memories USING GIN(content_topics);

-- 情绪模式表
CREATE TABLE emotion_patterns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id VARCHAR(64) NOT NULL,
  topic VARCHAR(128) NOT NULL,
  distribution JSONB,
  temporal_pattern JSONB,
  triggers TEXT[],
  effective_responses JSONB,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, topic)
);
```

### Milvus 集合设计

```python
# 向量检索集合
{
  "collection_name": "emotion_memories",
  "fields": [
    {"name": "id", "type": "VARCHAR", "is_primary": True, "max_length": 64},
    {"name": "user_id", "type": "VARCHAR", "max_length": 64},
    {"name": "embedding", "type": "FLOAT_VECTOR", "dim": 768},
    {"name": "emotion_type", "type": "VARCHAR", "max_length": 32},
    {"name": "created_at", "type": "INT64"}  # Unix timestamp
  ],
  "index_params": {
    "metric_type": "COSINE",
    "index_type": "HNSW"
  }
}
```

---

## API 设计

### RESTful API

```yaml
# 情感记忆相关
POST /api/v1/memories
  - 创建新的情感记忆
  - Body: { audioUrl, text, emotion, context }
  
GET /api/v1/memories
  - 查询用户的情感记忆
  - Query: { userId, topic, emotion, startTime, endTime, limit }
  
POST /api/v1/memories/search
  - 相似记忆检索
  - Body: { queryMemory, limit }

# 情绪分析相关
POST /api/v1/emotions/analyze
  - 分析音频情绪
  - Body: { audioData }
  
GET /api/v1/emotions/patterns/{userId}
  - 获取用户的情绪模式
  
# 共情生成相关
POST /api/v1/empathy/generate
  - 生成共情回应
  - Body: { userId, input, context }

# 用户配置相关
GET /api/v1/users/{userId}/profile
  - 获取用户画像
  
PUT /api/v1/users/{userId}/preferences
  - 更新用户偏好
```

### WebSocket 实时通信

```javascript
// 连接
ws://api.warmagent.com/v1/realtime?token=xxx

// 消息格式
{
  type: 'audio_stream',      // 音频流
  type: 'emotion_update',    // 情绪更新
  type: 'empathy_response',  // 共情回应
  type: 'memory_recall'      // 记忆回调
}
```

---

## 部署架构

### 开发环境

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  api:
    build: ./src/api
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://localhost:5432/warmagent
      - MILVUS_HOST=milvus
      - ZHISHANG_API_KEY=${ZHISHANG_API_KEY}
  
  postgres:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  milvus:
    image: milvusdb/milvus:v2.3.0
    volumes:
      - milvus_data:/var/lib/milvus
  
  redis:
    image: redis:7-alpine
```

### 生产环境

- **容器化**: Docker + Kubernetes
- **云服务**: 阿里云/腾讯云
- **CDN**: 阿里云OSS + CDN
- **监控**: Prometheus + Grafana
- **日志**: ELK Stack

---

## 关键技术选型

| 组件 | 选型 | 理由 |
|------|------|------|
| 后端框架 | Node.js + Fastify | 高性能、适合实时通信 |
| 数据库 | PostgreSQL 15 | 强大的JSON支持、向量插件 |
| 向量数据库 | Milvus | 专业的向量检索、高性能 |
| 缓存 | Redis | 会话管理、热点数据 |
| 消息队列 | Bull (Redis-based) | 异步任务处理 |
| 语音分析 | 智声云配 | 中文情绪识别效果好 |
| 嵌入模型 | BGE-large-zh | 中文语义理解强 |
| 部署 | Docker + K8s | 云原生、可扩展 |

---

## 开发里程碑

### MVP (4-6周)
- [x] 基础架构搭建
- [ ] 智声云配API对接
- [ ] 情感记忆存储
- [ ] 简单共情生成
- [ ] QQ Bot接入

### V1.0 (8-12周)
- [ ] 向量检索
- [ ] 情绪模式学习
- [ ] 多轮对话
- [ ] Web App

### V2.0 (16-20周)
- [ ] 个性化引擎
- [ ] 长期记忆
- [ ] API开放
- [ ] 企业版

---

**技术规格创建时间**: 2026-02-26  
**版本**: v0.1  
**状态**: 设计阶段
