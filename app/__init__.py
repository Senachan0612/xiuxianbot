"""功能"""

from .. import (
    DataPath,
    Config,
    Monitor, LoopEvent,

    xxBot,  # 加载xxbot
    eventCheck,  # 加载事件校验工具包
)

# 加载功能
from . import yaocao
from . import zongmen
from . import diaoxiang
from . import tupo

# xxBot同步配置
xxBot.save_configs()
