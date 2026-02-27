# 核心概念详解 📚

## 1. 情感记忆 (Emotion Memory)

### 1.1 定义
情感记忆是一种特殊的长期记忆，它不仅存储**事件内容**，还存储**情绪状态**和**表达方式**。

### 1.2 与传统记忆的区别

| 维度 | 传统记忆 | 情感记忆 |
|------|---------|---------|
| 存储内容 | "说了什么" | "怎么说" + "什么情绪" |
| 检索方式 | 关键词匹配 | 情绪模式匹配 |
| 时间特性 | 静态快照 | 动态趋势 |
| 关联维度 | 话题、时间 | 话题、时间、情绪、环境 |

### 1.3 数据结构

```typescript
interface EmotionMemory {
  // 基础信息
  id: string;
  timestamp: number;
  userId: string;
  
  // 内容层
  content: {
    text: string;           // 说了什么
    topic: string;          // 话题
    intent: string;         // 意图
  };
  
  // 情绪层
  emotion: {
    primary: EmotionType;   // 主要情绪：开心/悲伤/愤怒/焦虑/平静...
    intensity: number;      // 强度：0-1
    valence: number;        // 正负：-1 到 1
    arousal: number;        // 激活度：0-1
    
    // 声学特征
    features: {
      tone: string;         // 语调：平缓/急促/颤抖...
      pitch: number;        // 音高：Hz
      speed: number;        // 语速：字/秒
      volume: number;       // 音量：dB
      pauses: number[];     // 停顿模式
    };
  };
  
  // 环境层
  context: {
    time: TimeContext;      // 时间：早/中/晚/深夜
    location: string;       // 地点
    activity: string;       // 活动
    biometrics: {           // 生物信号
      heartRate?: number;
      stressLevel?: number;
    };
    environment: {          // 环境信息
      noise?: number;       // 噪音水平
      light?: number;       // 光照强度
      temperature?: number; // 温度
    };
  };
  
  // 关联层
  relations: {
    prevEvent?: string;     // 前一个事件
    relatedTopics: string[];// 相关话题
    similarEmotions: string[];// 相似情绪历史
  };
  
  // 元数据
  meta: {
    importance: number;     // 重要程度
    recallCount: number;    // 被回忆次数
    lastRecalled: number;   // 上次回忆时间
  };
}
```

### 1.4 情绪类型体系

```
情绪空间 (Emotion Space)
├── 正向高能量 (Positive High)
│   ├── 兴奋 (Excited)
│   ├── 开心 (Happy)
│   └── 期待 (Anticipated)
├── 正向低能量 (Positive Low)
│   ├── 平静 (Calm)
│   ├── 满足 (Content)
│   └── 放松 (Relaxed)
├── 负向高能量 (Negative High)
│   ├── 愤怒 (Angry)
│   ├── 焦虑 (Anxious)
│   └── 恐惧 (Fearful)
└── 负向低能量 (Negative Low)
    ├── 悲伤 (Sad)
    ├── 疲惫 (Tired)
    └── 沮丧 (Frustrated)
```

---

## 2. 共情生成 (Empathy Generation)

### 2.1 定义
根据用户的情绪状态和上下文，生成恰当的、有温度的回应。

### 2.2 共情层次

```
Level 0: 无共情
"我听到了。"

Level 1: 认知共情 (Cognitive Empathy)
"你今天看起来很累。"

Level 2: 情感共情 (Affective Empathy)
"听起来你今天压力很大，我能感受到你的焦虑。"

Level 3:  compassionate 共情 (Compassionate Empathy)
"你今天第三次提到这个策略了，每次语气都很焦虑。
 上次调整参数后你放松了一些，这次要不要试试类似的方法？
 或者我们先休息 5 分钟？"
```

### 2.3 共情生成流程

```
用户输入
    ↓
[情绪识别] → 情绪类型 + 强度
    ↓
[记忆检索] → 相似情绪历史 + 有效应对策略
    ↓
[情境分析] → 当前情境 + 用户状态
    ↓
[回应生成] → 共情回应 + 建议/行动
    ↓
用户反馈 → [学习优化]
```

### 2.4 共情策略库

| 情绪 | 共情策略 | 示例回应 |
|------|---------|---------|
| 焦虑 | 正常化 + 提供控制感 | "这种不确定感很正常，我们可以一起理清思路" |
| 愤怒 | 认可 + 转移焦点 | "这确实让人沮丧，你想聊聊怎么解决吗？" |
| 悲伤 | 陪伴 + 给予时间 | "我在这里陪着你，想哭就哭吧" |
| 兴奋 | 分享 + 适度降温 | "太棒了！和我说说细节，但也别忘了休息" |
| 疲惫 | 关怀 + 建议休息 | "听起来你很累了，先休息一下吧" |

---

## 3. 情绪反馈与可视化

### 3.1 概念
通过多种方式向用户反馈情绪分析和历史记录

### 3.2 反馈模式

#### 模式 1: 实时情绪反馈
对话过程中显示当前情绪状态
```
💬 用户: "这个策略回撤太大了..."

🤖 Warm Agent:
"我听到你的担忧了" 
[检测到: 焦虑 0.7, 挫败感 0.6]
```

#### 模式 2: 情绪日报
每日推送情绪总结
```
📊 你的今日情绪报告

😊 开心: 2次 (收到好消息时)
😰 焦虑: 3次 (讨论策略时)
😐 平静: 5次

💡 发现: 提到"量化策略"时你容易焦虑，
   需要我调整提醒方式吗？
```

#### 模式 3: 情绪时间线
回顾一段时间的情绪变化
```
📈 本周情绪趋势

😄 ──── 😐 ── 😟 ──── 😌
周一    周三  周四   今天

📝 备注: 周四策略调整时情绪波动最大
   建议: 下次重大决策前先深呼吸
```

### 3.3 主动关怀机制
基于情绪模式主动发起关怀
- 检测到持续负面情绪 → 主动询问是否需要帮助
- 发现情绪改善 → 正向强化
- 识别情绪循环 → 提供打破循环的建议

---

## 4. 记忆图谱 (Memory Graph)

### 4.1 概念
用图数据库构建用户的长期记忆网络。

### 4.2 节点类型

```
记忆图谱节点
├── 事件节点 (Event)
│   └── 属性：时间、地点、内容、情绪
├── 话题节点 (Topic)
│   └── 属性：类型、频次、关联情绪
├── 人物节点 (Person)
│   └── 属性：关系、互动情绪模式
├── 地点节点 (Location)
│   └── 属性：空间坐标、发生事件
└── 情绪节点 (Emotion)
    └── 属性：类型、强度、触发因素
```

### 4.3 关系类型

```
关系边
├── 时间关系: happened_before, happened_after
├── 因果关系: caused, resulted_in
├── 相似关系: similar_to, reminds_of
├── 包含关系: part_of, contains
└── 情绪关系: triggered, alleviated
```

### 4.4 查询示例

```cypher
// 查询：用户讨论"量化策略"时的情绪模式
MATCH (u:User)-[:experienced]->(e:Event)-[:about]->(t:Topic {name: "量化策略"})
MATCH (e)-[:has_emotion]->(em:Emotion)
RETURN em.type, count(*) as frequency, avg(em.intensity) as avg_intensity
ORDER BY frequency DESC

// 结果：
// 焦虑: 15次, 平均强度 0.7
// 兴奋: 8次, 平均强度 0.8
// 沮丧: 5次, 平均强度 0.6
```

---

## 5. 隐私与伦理

### 5.1 核心原则
- **数据最小化**: 只收集必要数据
- **本地优先**: 敏感数据本地处理
- **用户控制**: 用户完全掌控自己的数据
- **透明可解释**: AI 决策可解释

### 5.2 技术措施
- 端侧情绪识别（不上传原始语音）
- 差分隐私（统计数据脱敏）
- 加密存储（端到端加密）
- 定期遗忘（用户可设置遗忘周期）

---

*文档创建时间: 2026-02-26*  
*状态: 概念阶段，持续完善*
