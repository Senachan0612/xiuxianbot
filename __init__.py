"""修仙辅助插件"""
__author__ = "Sena"
__version__ = "1.0.1"

import os
import json
import asyncio
import ast
import re
import datetime
import operator
from dateutil.relativedelta import relativedelta

import nonebot
from nonebot import get_bot, require
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin.on import on_regex, on_command
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

from .data import DataPath
from .core import (
    Config,  # xxbot配置
    Monitor,  # 事件循环器
    LoopEvent,  # 监听器
)

from .app import *

# """常用工具"""
#
# config_dict = nonebot.get_driver().config.dict()
#
# # 定义支持的操作符
# operators = {
#     ast.Add: operator.add,
#     ast.Sub: operator.sub,
#     ast.Mult: operator.mul,
#     ast.Div: operator.truediv,
#     ast.Mod: operator.mod,
#     ast.Pow: operator.pow,
#     ast.BitXor: operator.xor,
#     ast.USub: operator.neg,
# }
#
#
# def safe_eval(_expr):
#     """
#     安全地评估算术表达式
#     :param _expr: 算术表达式字符串
#     :return: 计算结果
#     """
#
#     def _eval(_node):
#         if isinstance(_node, ast.Num):  # 数字
#             return _node.n
#         elif isinstance(_node, ast.BinOp):  # 二元运算符
#             return operators[type(_node.op)](_eval(_node.left), _eval(_node.right))
#         elif isinstance(_node, ast.UnaryOp):  # 一元运算符
#             return operators[type(_node.op)](_eval(_node.operand))
#         else:
#             raise TypeError(_node)
#
#     _node = ast.parse(_expr, mode='eval').body
#     return _eval(_node)
#
#
# def get_config(_key, _type='', _default=None):
#     """
#     格式化处理配置参数
#     :param _key: .env配置Key
#     :param _type: convert -> python转换
#                   eval -> 计算算式
#     :param _default: 异常时填充默认值
#     :return: 计算结果
#     """
#     # 获取配置
#     _val = config_dict[_key.lower()]
#
#     try:
#         # 去除注释
#         _val = re.sub(r'<\*.*?\*>', '', _val)
#
#         if _type == 'convert':
#             _val = ast.literal_eval(_val)
#         elif _type == 'eval':
#             _val = safe_eval(_val)
#     except TypeError:
#         if _default is not None:
#             _val = _default
#
#     return _val
#
#
# # 允许群组
# GroupIds = get_config('Group_Ids', _type='convert')
# BotId = get_config('Bot_Id', _type='eval')
# ManagerIds = get_config('Manager_Ids', _type='convert')
#
#
# def check_at_by_msg(event, msg, uid):
#     """判断是否at"""
#     if event.to_me:
#         return True
#     for m in msg:
#         if "[at:qq=%s]" % uid in str(m):
#             return True
#
#
# def covert_time(time, unit):
#     if unit == '小时':
#         time = time * 60 * 60 + 30
#     elif unit == '分钟':
#         time = time * 60 + 30
#
#     return time
#
#
# def api_check_config(event, *, bot_event=False, at_me=True):
#     """校验权限"""
#     if at_me and not event.to_me:
#         return False
#     if event.group_id not in GroupIds:
#         return False
#     if bot_event and event.user_id != BotId:
#         return False
#     elif not bot_event and event.user_id not in ManagerIds:
#         return False
#
#     return True
#
#
# def api_check_task__exec_by_bot_at(event, timing=False, monitor=False):
#     """任务执行中 校验bot@回复事件"""
#     if timing and not timing.check('is_mutual'):
#         return True
#     if monitor and monitor.check('is_finish'):
#         return True
#     if not api_check_config(event, bot_event=True, at_me=True):
#         return True
#
#
# def api_update_state(state: str or dict, event, timing, bot_event, at_me):
#     """通用修改任务状态"""
#     if not api_check_config(event, bot_event=bot_event, at_me=at_me):
#         return
#
#     if isinstance(state, str):
#         state = {'state', state}
#     timing(**state)
#
#
# def api_update_state__by_bot_at(event, timing, state):
#     """通用更新状态 -- bot@事件"""
#     api_update_state(state, event, timing, bot_event=True, at_me=True)
#
#
# def api_update_state__by_at(event, timing, state):
#     """通用修改任务状态 -- @事件"""
#     api_update_state(state, event, timing, bot_event=False, at_me=True)
#
#
# """常用参数"""
# # at bot 消息
# AtBot = Message(f"[CQ:at,qq={BotId}] ")
#
# """xxbot"""
#
#
# class XiuXianBot:
#     def __init__(self):
#         # 道号
#         self.name = False
#         # 境界
#         self.level = False
#         # 修为
#         self.exp = False
#         # HP
#         self.hp = False
#         # MP
#         self.mp = False
#         # 没有肚饿丹
#         self.no_due = False
#
#         self.is_use_due = False
#
#         self.tasks = self.load_tasks()
#
#     def __getitem__(self, item):
#         return self.tasks[item]
#
#     @staticmethod
#     def load_tasks():
#         return {
#             'cg_timing': Monitor(name='出关', time=get_config('Default_ChuGuan', _type='eval')),
#             'tp_timing': Monitor(name='突破', time=get_config('Default_TuPo', _type='eval')),
#             'gz_timing': Monitor(name='复读'),
#             'tpd_timing': Monitor(name='突破丹'),
#
#             'zmrw_timing': Monitor(name='宗门任务', time=get_config('Default_ZongMenRenWu', _type='eval')),
#             'xsl_timing': Monitor(name='悬赏令'),
#
#             'sc_timing': Monitor(name='收草', time=get_config('Default_ShouCao', _type='eval')),
#             'dx_timing': Monitor(name='雕像', time=24 * 60 * 60),
#             'zmdy_timing': Monitor(name='宗门丹药', time=24 * 60 * 60),
#         }
#
#     def status(self):
#         """打印状态"""
#         return (
#                 Message('####指令\n') + self.cmd_status()
#                 + Message('\n\n####状态\n') + self.bot_status()
#         )
#
#     def bot_status(self):
#         """bot状态"""
#         msg_list = [
#             ('肚饿丹', self.is_use_due and '允许' or '禁止'),
#         ]
#         msg_str = Message('\n'.join(''.join(self._right(m) for m in info) for info in msg_list))
#         return msg_str
#
#     def cmd_status(self):
#         """命令状态"""
#
#         msg_list = [
#             ['指令', '状态', '备注', '下次执行', ],
#             *[tk.log() for _, tk in self.tasks.items()]
#         ]
#         msg_str = Message('\n'.join(''.join(self._right(m) for m in info) for info in msg_list))
#         return msg_str
#
#     @staticmethod
#     def _right(text):
#         return '{: <10}'.format(text)
#
#
# xxbot = XiuXianBot()
#
# cmd_status = on_command("修仙信息", aliases={"修仙状态", "修仙信息", "xxzt", "xxxx"}, rule=to_me(), priority=60, block=True)
#
#
# @cmd_status.handle()
# async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
#     if not api_check_config(event, at_me=True):
#         return
#
#     msg = xxbot.status()
#     await cmd_status.send(msg)
#
#
# cmd_use_due = on_command("肚饿丹", aliases={"肚饿丹"}, rule=to_me(), priority=60, block=True)
#
#
# @cmd_use_due.handle()
# async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
#     if not api_check_config(event, at_me=True):
#         return
#
#     _msg = str(msg)
#     xxbot.is_use_due = '使用' in _msg and '不使用' not in _msg
#     await cmd_use_due.send(Message(f"已{'允许' if xxbot.is_use_due else '禁止'}使用肚饿丹"))
#
#
# """导入功能"""
# # 收草
# from . import shoucao
#
# # 突破
# from . import tupo
#
# # 突破丹
# from . import tupo_danyao
#
# # 宗门
# from . import zongmen__renwu
#
# # 宗门丹药
# from . import zongmen__danyao
#
# # 雕像
# from . import diaoxiang
#
# # 灌注
# from . import guanzhu
#
# # 出关
# from . import chuguan
#
# # 悬赏令
# from . import xuanshang
