# from nonebot.plugin.on import on_command, on_shell_command, on_regex
# from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
# from nonebot.params import CommandArg
# from nonebot.rule import to_me, keyword
#
# import re
# import asyncio
#
# from . import (
#     GroupIds, BotId, ManagerIds,
#     LoopEvent, Monitor,
#     api_check_config, check_at_by_msg
# )
#
# """悬赏"""
#
# xs_command = on_command("悬赏", aliases={"悬赏", "xs", "xuanshang"}, rule=to_me(), priority=60, block=True)
# xs_command_success = on_command("", aliases={""}, rule=keyword('悬赏令结算'), priority=100, block=True)
# '''
# '[markdown:data=[](%7B%22version%22%3A2%7D)\n悬赏令结算，获得报酬3746枚灵石。额外获得奖励：霸王花！以肉身硬抗涅槃圣祖，...][at:qq=1307228732]悬赏令结算，获得报酬3746枚灵石。额外获得奖励：霸王花！以肉身硬抗涅槃圣祖，威震真魔界！'
# '''
# xs_command_false = on_command("", aliases={""}, rule=keyword('进行中的悬赏令'), priority=100, block=True)
# '''
# '[at:qq=1307228732]进行中的悬赏令【重伤真灵阳鹿】，预计66.0分钟后可结束'
# '''
#
# xs_timing = Monitor(time=12 * 60 * 60)
# xs_monitor = Monitor()
#
#
# def _monitor_command_check(event, to_me=True):
#     if xs_timing.is_except():
#         return True
#     if not xs_monitor.is_waiting():
#         return True
#     if not api_check_config(event, bot_event=True, to_me=to_me):
#         return True
#
#
# @xs_command_success.handle()
# async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
#     if not check_at_by_msg(event, msg, uid=1):
#         return
#
#     if _monitor_command_check(event, to_me=False):
#         return
#
#     xs_monitor.set_time(0)
#     xs_monitor.done()
#
#
# @xs_command_false.handle()
# async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
#     if _monitor_command_check(event):
#         return
#
#     msg_str = str(msg)
#
#     pattern = r'：([\d.]+)(\D+)之后'
#     match = re.search(pattern, msg_str)
#     time, unit = float(match.group(1)), match.group(2).strip()
#
#     if unit == '小时':
#         time *= 60 * 60
#
#     sc_monitor.set_time(time)
#     sc_monitor.done()
#
#
# @sc_command.handle()
# async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
#     if not api_check_config(event, to_me=True):
#         return
#
#     # 启动
#     if not sc_timing.start():
#         return
#
#     reply = Message(f"[CQ:at,qq={BotId}]") + Message(f" 灵田收取")
#
#     # 加载异步监听
#     loop = LoopEvent(event)
#
#     """监听"""
#     while True:
#         if sc_timing.is_finish():
#             break
#
#         went_await = loop.add(loop.loop_await_cmd('shoucao', monitor=sc_monitor))
#         went_send = loop.add(loop.loop_send_cmd('shoucao', cmd=sc_command, msg=reply))
#
#         # 执行监听
#         sc_timing.running()
#         await went_await
#         await went_send
#
#         if sc_monitor.is_done():
#             # 循环等待
#             time = sc_monitor.time
#         else:
#             time = sc_timing.time
#
#         sc_monitor.init()
#         await asyncio.sleep(time)
#
#     sc_timing.init()
