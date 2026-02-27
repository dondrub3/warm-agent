# 🤝 贡献指南

感谢你对Warm Agent项目的兴趣！我们欢迎所有形式的贡献，无论是代码、文档、测试还是反馈。

## 📋 如何贡献

### 1. 报告问题

如果你发现了bug或有功能建议：

1. 搜索现有issue，确保问题未被报告
2. 创建新的issue，包含：
   - 问题描述
   - 复现步骤
   - 期望行为
   - 实际行为
   - 环境信息（操作系统、Python版本等）

### 2. 提交代码

#### 准备工作

```bash
# 1. Fork仓库
# 在GitHub上点击Fork按钮

# 2. 克隆你的fork
git clone https://github.com/YOUR_USERNAME/warm-agent.git
cd warm-agent

# 3. 添加upstream远程

git remote add upstream https://github.com/warm-agent/warm-agent.git

# 4. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或: venv\Scripts\activate  # Windows

# 5. 安装开发依赖
pip install -e ".[dev]"

# 6. 安装pre-commit钩子
pre-commit install
```

#### 开发流程

```bash
# 1. 更新main分支
git checkout main
git pull upstream main

# 2. 创建功能分支
git checkout -b feature/your-feature-name

# 3. 开发代码
# ... 编写代码 ...

# 4. 运行测试
pytest tests/

# 5. 检查代码格式
black src/ tests/
flake8 src/ tests/

# 6. 提交更改
git add .
git commit -m "feat: add your feature"

# 7. 推送到你的fork
git push origin feature/your-feature-name

# 8. 创建Pull Request
# 在GitHub上点击"New Pull Request"
```

### 3. 代码规范

#### Python代码规范

- 遵循PEP 8
- 使用Black格式化代码
- 使用类型注解
- 编写清晰的docstring

```python
def analyze_emotion(text: str, language: str = "zh-CN") -> dict:
    """
    分析用户输入的情感状态
    
    Args:
        text: 要分析的文本
        language: 语言代码，默认"zh-CN"
        
    Returns:
        包含情感分析结果的字典
        
    Example:
        >>> result = analyze_emotion("今天很开心")
        >>> print(result["primary_emotion"])
        "happiness"
    """
    # 实现代码
    pass
```

#### 提交信息规范

使用[Conventional Commits](https://www.conventionalcommits.org/)规范：

```
feat: add new emotion detection algorithm
fix: resolve memory leak in emotion cache
docs: update API documentation
style: format code with black
refactor: simplify trigger detection logic
test: add tests for new feature
chore: update dependencies
```

### 4. 文档贡献

- 更新README.md（如果修改了API）
- 更新docs/下的文档
- 添加示例代码到examples/
- 修复拼写和语法错误

### 5. 测试贡献

```python
# tests/test_triggers.py
def test_should_trigger_negative_emotion():
    """测试负面情绪触发"""
    triggers = WarmAgentTriggers()
    should_trigger, info = triggers.should_trigger_warm_mode("我今天很难过")
    
    assert should_trigger is True
    assert "emotion_negative" in info["trigger_categories"]
```

## 🎯 优先级任务

我们特别需要帮助的领域：

### 高优先级
- [ ] 改进情感分析算法
- [ ] 添加更多语言支持
- [ ] 优化响应速度
- [ ] 编写测试用例

### 中优先级
- [ ] 添加更多温暖回应模板
- [ ] 改进关键词触发逻辑
- [ ] 创建视频教程
- [ ] 改进文档

### 低优先级
- [ ] 添加Docker支持
- [ ] 创建Web界面
- [ ] 添加更多集成示例

## 💬 交流方式

- **GitHub Issues**: 报告bug或请求功能
- **GitHub Discussions**: 讨论想法或提问
- **Discord**: [加入我们的社区](https://discord.gg/warm-agent)
- **邮件**: contact@warm-agent.com

## 🏆 贡献者荣誉

我们会定期更新[CONTRIBUTORS.md](CONTRIBUTORS.md)，感谢所有贡献者！

## 📜 行为准则

参与本项目即表示你同意遵守我们的[行为准则](CODE_OF_CONDUCT.md)。

## 📝 许可

贡献即表示你同意你的贡献将在[MIT许可证](LICENSE)下发布。

## ❓ 常见问题

**Q: 我是新手，可以贡献吗？**  
A: 当然可以！我们标记了[good first issue](https://github.com/warm-agent/warm-agent/labels/good%20first%20issue)标签的issue，非常适合新手。

**Q: 需要签署贡献者协议吗？**  
A: 不需要，但需要遵守MIT许可证。

**Q: 可以添加我的母语支持吗？**  
A: 非常欢迎！请创建包含翻译的PR。

**Q: 发现安全问题怎么办？**  
A: 请通过邮件 security@warm-agent.com 私下报告，不要在公开issue中披露。

---

再次感谢你的贡献！让我们一起让AI更有温度 ❤️