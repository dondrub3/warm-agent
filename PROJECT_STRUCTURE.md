# Warm Agent 项目目录结构

## 总体结构

```
warm-agent/
├── README.md                      # 项目总览
├── PROJECT_CHARTER.md             # 项目章程
├── PROJECT_START.md               # 项目启动记录
├── ROADMAP.md                     # 项目路线图
├── PHASE_0_PLAN.md                # Phase 0详细计划
├── PROJECT_STRUCTURE.md           # 本项目结构文档
├── docs/                          # 项目文档
│   ├── concepts.md                # 核心概念详解
│   ├── tech-spec.md               # 技术规格文档
│   ├── business-model.md          # 商业模式文档
│   └── api/                       # API文档
├── src/                           # 源代码
│   ├── emotion-engine/            # 情感记忆引擎
│   ├── voice-analysis/            # 语音分析模块
│   ├── empathy-generator/         # 共情生成模块
│   ├── memory-store/              # 记忆存储模块
│   ├── api/                       # API服务
│   └── utils/                     # 工具函数
├── prototypes/                    # 原型代码
│   ├── mvp-emotion-memory/        # MVP: 情感记忆原型
│   ├── demo-empathy/              # Demo: 共情对话原型
│   └── voice-analysis-test/       # 语音分析测试
├── references/                    # 参考资料
│   ├── papers/                    # 学术论文
│   ├── apis/                      # API文档
│   └── competitors/               # 竞品资料
├── project-management/            # 项目管理文件
│   ├── PROGRESS_TRACKER.md        # 进度跟踪
│   ├── COMMUNICATION_PLAN.md      # 沟通计划
│   ├── TECH_RESEARCH_TEMPLATE.md  # 技术调研模板
│   ├── MEETING_TEMPLATE.md        # 会议记录模板
│   ├── meetings/                  # 会议记录
│   │   ├── 2026-02-26-kickoff.md  # 启动会议
│   │   └── weekly/                # 周会记录
│   ├── progress/                  # 进度报告
│   │   ├── weekly/                # 周报
│   │   └── monthly/               # 月报
│   ├── tasks/                     # 任务管理
│   │   ├── phase-0-tasks.md       # Phase 0任务
│   │   └── backlog.md             # 待办事项
│   └── resources/                 # 资源管理
│       ├── budget.md              # 预算管理
│       └── team.md                # 团队管理
├── tests/                         # 测试文件
│   ├── unit/                      # 单元测试
│   ├── integration/               # 集成测试
│   └── performance/               # 性能测试
├── config/                        # 配置文件
│   ├── development/               # 开发环境配置
│   ├── staging/                   # 测试环境配置
│   └── production/                # 生产环境配置
├── scripts/                       # 脚本文件
│   ├── setup.sh                   # 环境设置脚本
│   ├── deploy.sh                  # 部署脚本
│   └── test.sh                    # 测试脚本
└── .github/                       # GitHub配置
    ├── workflows/                 # CI/CD工作流
    └── ISSUE_TEMPLATE/            # Issue模板
```

## 详细说明

### 1. 根目录文件
| 文件 | 用途 | 维护人 |
|------|------|--------|
| `README.md` | 项目总览，新成员入门指南 | 技术负责人 |
| `PROJECT_CHARTER.md` | 项目章程，定义项目目标范围 | 项目负责人 |
| `PROJECT_START.md` | 项目启动记录，记录项目起源 | 技术负责人 |
| `ROADMAP.md` | 项目路线图，阶段规划 | 技术负责人 |
| `PHASE_0_PLAN.md` | Phase 0详细计划 | 技术负责人 |
| `PROJECT_STRUCTURE.md` | 目录结构说明 | 技术负责人 |

### 2. docs/ - 项目文档
| 目录/文件 | 用途 | 维护人 |
|-----------|------|--------|
| `concepts.md` | 核心概念详解 | 产品负责人 |
| `tech-spec.md` | 技术规格文档 | 技术负责人 |
| `business-model.md` | 商业模式文档 | 项目负责人 |
| `api/` | API接口文档 | 开发工程师 |

### 3. src/ - 源代码
| 目录 | 用途 | 技术栈 | 负责人 |
|------|------|--------|--------|
| `emotion-engine/` | 情感记忆引擎核心算法 | Python | AI算法工程师 |
| `voice-analysis/` | 语音分析模块集成 | Python | 后端工程师 |
| `empathy-generator/` | 共情生成模块 | Python | AI算法工程师 |
| `memory-store/` | 记忆存储系统 | Python + 向量数据库 | 后端工程师 |
| `api/` | RESTful API服务 | FastAPI/Flask | 后端工程师 |
| `utils/` | 工具函数库 | Python | 开发工程师 |

### 4. prototypes/ - 原型代码
| 目录 | 用途 | 状态 | 负责人 |
|------|------|------|--------|
| `mvp-emotion-memory/` | MVP情感记忆原型 | 计划中 | AI算法工程师 |
| `demo-empathy/` | 共情对话演示 | 计划中 | AI算法工程师 |
| `voice-analysis-test/` | 语音分析测试 | 进行中 | 技术负责人 |

### 5. project-management/ - 项目管理
| 目录/文件 | 用途 | 更新频率 | 负责人 |
|-----------|------|----------|--------|
| `PROGRESS_TRACKER.md` | 进度跟踪 | 每日 | 技术负责人 |
| `COMMUNICATION_PLAN.md` | 沟通计划 | 季度 | 技术负责人 |
| `TECH_RESEARCH_TEMPLATE.md` | 技术调研模板 | 按需 | 技术负责人 |
| `MEETING_TEMPLATE.md` | 会议记录模板 | 按需 | 技术负责人 |
| `meetings/` | 会议记录 | 每次会议后 | 记录人 |
| `progress/` | 进度报告 | 每周/每月 | 技术负责人 |
| `tasks/` | 任务管理 | 每日 | 技术负责人 |
| `resources/` | 资源管理 | 每月 | 项目负责人 |

### 6. tests/ - 测试文件
| 目录 | 测试类型 | 覆盖率目标 | 负责人 |
|------|----------|------------|--------|
| `unit/` | 单元测试 | ≥80% | 开发工程师 |
| `integration/` | 集成测试 | ≥90% | 测试工程师 |
| `performance/` | 性能测试 | 满足SLA | 测试工程师 |

### 7. config/ - 配置文件
| 目录 | 环境 | 用途 | 负责人 |
|------|------|------|--------|
| `development/` | 开发环境 | 本地开发配置 | 开发工程师 |
| `staging/` | 测试环境 | 集成测试配置 | 测试工程师 |
| `production/` | 生产环境 | 线上运行配置 | 运维工程师 |

## 文件命名规范

### 1. 文档文件
- 使用英文命名，单词间用连字符分隔
- 格式: `小写-单词-描述.md`
- 示例: `tech-research-template.md`, `meeting-2026-02-26.md`

### 2. 代码文件
- Python: 使用蛇形命名法，`module_name.py`
- 配置文件: 使用点分隔，`config.dev.yaml`
- 测试文件: 以`test_`开头，`test_module.py`

### 3. 会议记录
- 格式: `YYYY-MM-DD-会议类型.md`
- 示例: `2026-02-26-kickoff.md`, `2026-03-04-weekly.md`

### 4. 进度报告
- 周报: `weekly-YYYY-MM-DD.md`
- 月报: `monthly-YYYY-MM.md`

## 版本控制规范

### 1. Git分支策略
- `main`: 生产环境代码，受保护分支
- `develop`: 开发分支，功能集成
- `feature/*`: 功能开发分支
- `bugfix/*`: 缺陷修复分支
- `release/*`: 发布准备分支

### 2. Commit消息规范
```
类型(范围): 简短描述

详细描述（可选）

- 变更点1
- 变更点2

关联Issue: #123
```

**类型**:
- `feat`: 新功能
- `fix`: 缺陷修复
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具更新

### 3. 版本标签
- 格式: `v主版本.次版本.修订版本`
- 示例: `v1.0.0`, `v1.1.0`, `v1.1.1`

## 文档更新流程

### 1. 技术文档更新
1. 在`feature/*`分支中更新文档
2. 提交Pull Request到`develop`分支
3. 技术负责人评审
4. 合并到`develop`分支
5. 发布时同步到`main`分支

### 2. 项目文档更新
1. 直接更新`main`分支中的文档
2. 提交Commit，描述更新内容
3. 通知相关成员

### 3. 会议记录更新
1. 会议后24小时内完成记录
2. 保存到`project-management/meetings/`
3. 分发会议记录链接
4. 更新行动项到进度跟踪

## 访问权限

### 1. 代码仓库权限
| 角色 | 读取 | 写入 | 合并 | 管理 |
|------|------|------|------|------|
| 项目负责人 | ✅ | ✅ | ✅ | ✅ |
| 技术负责人 | ✅ | ✅ | ✅ | ✅ |
| 开发工程师 | ✅ | ✅ | ❌ | ❌ |
| 外部合作方 | ✅ | ❌ | ❌ | ❌ |

### 2. 文档访问权限
| 文档类型 | 项目团队 | 外部合作方 | 公众 |
|----------|----------|------------|------|
| 技术文档 | ✅ | ✅ | ❌ |
| 项目文档 | ✅ | ✅ | ❌ |
| 商业文档 | ✅ | ❌ | ❌ |
| 会议记录 | ✅ | ❌ | ❌ |

## 备份策略

### 1. 代码备份
- 主仓库: GitHub私有仓库
- 镜像仓库: 每周自动备份
- 本地备份: 开发人员本地备份

### 2. 文档备份
- 在线存储: Git仓库
- 本地备份: 每周导出PDF版本
- 云备份: 重要文档加密备份到云存储

### 3. 数据备份
- 数据库: 每日全量备份 + 实时增量备份
- 用户数据: 加密存储，定期备份
- 日志数据: 保留90天，压缩归档

## 扩展说明

### 未来扩展目录
随着项目发展，可能需要添加以下目录：
```
warm-agent/
├── mobile/                    # 移动端应用
├── web/                      # Web前端
├── hardware/                 # 硬件相关
├── data/                     # 数据集
├── models/                   # 训练好的模型
└── deployments/              # 部署配置
```

### 工具集成
- **代码质量**: SonarQube, CodeClimate
- **持续集成**: GitHub Actions, Jenkins
- **文档生成**: Sphinx, MkDocs
- **项目管理**: Jira, Trello, Notion

---

**文档版本**: v1.0  
**创建日期**: 2026年2月26日  
**更新记录**: 
- 2026-02-26: 创建初始目录结构
- 2026-02-26: 添加详细说明和规范

**负责人**: 安安  
**下次评审**: Phase 0结束时