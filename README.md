# 🌟 Warm Agent - 为AI注入温度与情感

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenClaw Compatible](https://img.shields.io/badge/OpenClaw-Compatible-green.svg)](https://openclaw.ai)

**Warm Agent** 是一个为AI助手添加情感智能的开源项目。它让冰冷的AI回应变得温暖、有同理心，真正理解用户的情感需求。

## 🧠 情绪芯片 - 核心技术

**情绪芯片（Emotion Chip）** 是Warm Agent的核心技术，它是一个轻量级的情感智能模块，为AI系统提供：

### 🔬 技术特性
- **实时情感分析**: 毫秒级情感状态识别
- **情感记忆网络**: 记住用户的情感偏好和互动历史
- **温暖回应引擎**: 将标准回应转化为有温度、有同理心的版本
- **情感调节器**: 根据对话上下文动态调整回应温度

### 🏗️ 架构设计
```
情绪芯片架构：
┌─────────────────────────────────────┐
│        情感分析层 (Emotion Layer)    │
│  • 情感关键词检测                   │
│  • 情绪强度评估                     │
│  • 上下文情感理解                   │
├─────────────────────────────────────┤
│        温暖引擎层 (Warm Engine)      │
│  • 回应温度调节                     │
│  • 同理心表达生成                   │
│  • 个性化情感适配                   │
├─────────────────────────────────────┤
│        记忆网络层 (Memory Network)   │
│  • 情感历史记录                     │
│  • 用户偏好学习                     │
│  • 长期情感模式识别                 │
└─────────────────────────────────────┘
```

### 🎯 应用场景
- **心理健康支持**: 为焦虑、抑郁用户提供温暖陪伴
- **客户服务**: 提升客服AI的情感理解能力
- **教育助手**: 为学习者提供有温度的学习支持
- **社交机器人**: 让AI互动更自然、更有人情味

## ✨ 核心特性

### 🎯 情感智能
- **情感分析**: 自动识别用户输入中的情绪状态
- **温暖回应生成**: 将标准回应转化为温暖、有同理心的版本
- **情感记忆**: 记住用户的情感偏好和历史互动

### 🔌 无缝集成
- **OpenClaw原生支持**: 一键安装，自动增强所有AI回应
- **多平台适配**: 支持各种AI助手和聊天机器人框架
- **API优先设计**: 简洁的RESTful API，易于集成

### 🛠️ 开发者友好
- **完全开源**: MIT许可证，自由使用和修改
- **详细文档**: 完整的API文档和集成指南
- **丰富示例**: 多种使用场景的代码示例

## 🚀 快速开始

### 安装
```bash
# 通过pip安装
pip install warm-agent

# 或者从源码安装
git clone https://github.com/dondrub3/warm-agent.git
cd warm-agent
pip install -e .
```

### 基础使用
```python
from warm_agent import WarmAgent

# 初始化Warm Agent
wa = WarmAgent(api_key="your_api_key")

# 分析用户情感
emotion = wa.analyze_emotion("今天工作压力好大")
print(f"情感: {emotion.primary}, 强度: {emotion.intensity}")

# 生成温暖回应
response = wa.generate_warm_response(
    "今天工作压力好大",
    base_response="建议你休息一下"
)
print(response)
# 输出: "听起来你今天工作很辛苦呢...💼 压力大的时候确实需要放松一下。要不要试试听点轻松的音乐？我在这里陪着你✨"
```

### OpenClaw集成
```yaml
# OpenClaw配置
skills:
  warm-agent:
    enabled: true
    apiKey: "your_api_key"
    autoEnhance: true  # 自动为所有回应添加温暖
```

## 📖 文档

- [API文档](docs/api/README.md) - 完整的API参考
- [集成指南](docs/guides/integration.md) - 如何集成到你的项目
- [示例项目](examples/) - 实际使用示例
- [开发指南](docs/guides/development.md) - 贡献代码指南

## 🎯 关键词触发机制

Warm Agent支持智能关键词触发，当用户使用情感词汇时自动切换到温暖模式：

### 触发词示例
```python
# 负面情绪词
难过、伤心、悲伤、痛苦、焦虑、压力、烦躁、失望、孤独、害怕

# 正面情绪词  
开心、高兴、兴奋、幸福、感动

# 需求词
安慰、支持、陪伴、倾听、温暖、情感、心情、情绪
```

### 使用示例
```
用户: "今天工作压力好大 😔"
AI检测到"压力"关键词 → 触发温暖模式
AI: "听起来你今天工作很辛苦呢...💼 压力大的时候确实需要放松一下。要不要和我聊聊具体是什么让你感到压力？我在这里陪着你✨"
```

### 关闭指令
```
用户: "关闭情感模式"
AI: "✅ 好的，情感模式已关闭。需要的时候随时说'开启情感模式'或使用情感词触发哦！😊"
```

## 🏗️ 项目结构

```
warm-agent/
├── src/                    # 源代码
│   ├── core/              # 核心模块
│   ├── api/               # API接口
│   ├── integrations/      # 集成模块
│   └── utils/             # 工具函数
├── docs/                  # 文档
├── examples/              # 示例代码
├── tests/                 # 测试代码
└── scripts/               # 构建和部署脚本
```

## 🤝 贡献

我们欢迎所有形式的贡献！请查看[贡献指南](CONTRIBUTING.md)了解如何开始。

### 开发环境设置
```bash
# 克隆仓库
git clone https://github.com/dondrub3/warm-agent.git
cd warm-agent

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e ".[dev]"
```

### 运行测试
```bash
pytest tests/
```

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 📞 联系与支持

- **GitHub Issues**: [报告问题或请求功能](https://github.com/dondrub3/warm-agent/issues)
- **文档**: [查看完整文档](docs/)
- **邮件**: support@warm-agent.com

## 🌟 特别感谢

感谢所有贡献者和用户的支持！特别感谢：
- [OpenClaw](https://openclaw.ai) 社区
- 所有早期测试用户
- 贡献代码的开发者们
- **GitHub仓库**: https://github.com/dondrub3/warm-agent

---

**让AI更有温度，让技术更有情感** ❤️