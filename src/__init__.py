"""
Warm Agent - 为AI注入温度与情感

让冰冷的AI回应变得温暖、有同理心，真正理解用户的情感需求。
"""

__version__ = "1.0.0"
__author__ = "Warm Agent Team"
__email__ = "contact@warm-agent.com"
__license__ = "MIT"

# 核心导入
from .core.triggers import WarmAgentTriggers, get_warm_agent_triggers

# 可选：延迟导入其他模块（性能优化）
def __getattr__(name):
    if name == "OpenClawWarmAgentSkill":
        from .integrations.openclaw import OpenClawWarmAgentSkill
        return OpenClawWarmAgentSkill
    elif name == "WarmAgentClient":
        from .api.client import WarmAgentClient
        return WarmAgentClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# 版本信息
def get_version():
    """获取版本信息"""
    return {
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "license": __license__,
        "description": "为AI注入温度与情感"
    }


# 快速初始化
def create_warm_agent(config: dict = None):
    """
    快速创建Warm Agent实例
    
    Args:
        config: 配置字典
        
    Returns:
        WarmAgentTriggers实例
    """
    return get_warm_agent_triggers()


__all__ = [
    "WarmAgentTriggers",
    "get_warm_agent_triggers",
    "create_warm_agent",
    "get_version",
    "__version__",
]