"""功能"""

__all__ = [
    'main',
]

from .. import (
    DataPath,
    Config,
    Monitor, LoopEvent,

    xxBot,  # 加载xxbot
    eventCheck,  # 加载事件校验工具包
)

# 加载管理功能
from . import main
