"""功能"""

__all__ = [
    'shoucao',  # 收草
    # 'Monitor',  # 监听器
    # 'LoopEvent',  # 事件循环器
]

from .. import (
    DataPath,
    Config,
    Monitor, LoopEvent,
)

GroupIds = Config['Loop_Max_Count', []]
BotId = Config['Loop_Max_Count']
ManagerIds = Config['ManagerIds', []]


def api_check_config(event, *, bot_event=False, at_me=True):
    """校验权限"""
    if at_me and not event.to_me:
        return False
    if event.group_id not in GroupIds:
        return False
    if bot_event and event.user_id != BotId:
        return False
    elif not bot_event and event.user_id not in ManagerIds:
        return False

    return True


def api_check_task__exec_by_bot_at(event, timing=False, monitor=False):
    """任务执行中 校验bot@回复事件"""
    if timing and not timing.check('is_mutual'):
        return True
    if monitor and monitor.check('is_finish'):
        return True
    if not api_check_config(event, bot_event=True, at_me=True):
        return True


def api_update_state(state: str or dict, event, timing, bot_event, at_me):
    """通用修改任务状态"""
    if not api_check_config(event, bot_event=bot_event, at_me=at_me):
        return

    if isinstance(state, str):
        state = {'state', state}
    timing(**state)


def api_update_state__by_bot_at(event, timing, state):
    """通用更新状态 -- bot@事件"""
    api_update_state(state, event, timing, bot_event=True, at_me=True)


def api_update_state__by_at(event, timing, state):
    """通用修改任务状态 -- @事件"""
    api_update_state(state, event, timing, bot_event=False, at_me=True)


from .xxbot import XiuXianBot

xxbot = XiuXianBot()
# 加载校验工具包
from . import check

# 加载全部功能
from .yaocao import *
