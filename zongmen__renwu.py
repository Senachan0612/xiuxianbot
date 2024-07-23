from nonebot.plugin.on import on_command, on_shell_command, on_regex
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, GROUP
from nonebot.params import CommandArg
from nonebot.rule import to_me, keyword

import re
import datetime
from dateutil.relativedelta import relativedelta
import asyncio

from . import (
    GroupIds, BotId, ManagerIds,
    AtBot, Task_Level,
)
from . import (
    LoopEvent, Monitor,
)
from . import (
    api_check_config,
    api_check_task__exec_by_bot_at,
    api_update_state__by_bot_at,
    api_update_state__by_at,
)
from . import xxbot

timing = xxbot['zmrw_timing']
monitor = Monitor(name='宗门任务监控', start=True)

TaskList = {
    # 2% 挑战
    1: [
        '最近有宗外势力抹黑宗门',  # 为了宗主
        '最近有人不敬环奈',  # 开启圣战
    ],
    # 2% 灵石
    2: [
        '请道友雇佣记者多加宣传',  # 舆论战
        '又到了一年一度集体突破的日子了',  # 修炼无宗界
        '为宗门打扫一下',  # 清理雕像
    ],
    # 2.2%
    3: [
        '为宗门提前五百年迎回弟子',  # 社会毒打
    ],
    # 4%
    4: [
        '宗门高层有个人给你了一个宗门采购清单',  # 正当采购
    ],
}


def get_task(_level=Task_Level):
    for _k, _v in TaskList.items():
        if not TaskList or _k in _level:
            yield from _v


# 有效任务内容
task_content_pattern = r'(%s)' % '|'.join(get_task())
# 有效任务完成反馈
task_finish_pattern = r'(道友为了完成任务购买宝物消耗灵石|道友大战一番，气血减少)'

local_monitor = Monitor(name='任务刷新监控', start=True)

"""宗门任务"""

Reply_Receive = AtBot + Message(f" 宗门任务接取")
Reply_Refresh = AtBot + Message(f" 宗门任务刷新")
Reply_Completed = AtBot + Message(f" 宗门任务完成")

command = on_command("宗门任务", aliases={"宗门任务", "zmrw"}, rule=to_me(), priority=60, block=True)
exit_command = on_command("关闭宗门任务", aliases={"!宗门任务", "!zmrw"}, rule=to_me(), priority=60, block=True)

command_ture_task = on_regex(pattern=task_content_pattern, flags=re.I, permission=GROUP)
command_ture_task_finish = on_regex(pattern=task_finish_pattern, flags=re.I, permission=GROUP)

command_false_finish = on_command("", aliases={""}, rule=keyword('道友已接取3次，今日无法再获取宗门任务了'), priority=100, block=True)
command_false_no_task = on_command("", aliases={""}, rule=keyword('道友目前还没有宗门任务'), priority=100, block=True)
command_false_no_hp = on_command("", aliases={""}, rule=keyword('重伤未愈，动弹不得'), priority=100, block=True)
command_false_no_money = on_command("", aliases={""}, rule=keyword('道友的灵石不足以完成宗门任务'), priority=100, block=True)
command_false_time = on_command("", aliases={""}, rule=keyword('剩余CD'), priority=100, block=True)

"""成功"""


@command_ture_task.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if api_check_task__exec_by_bot_at(event, timing, local_monitor):
        return
    local_monitor('done')


@command_ture_task_finish.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if api_check_task__exec_by_bot_at(event, timing, monitor):
        return
    monitor('done')


"""失败"""


@command_false_finish.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if api_check_task__exec_by_bot_at(event, timing, local_monitor):
        return

    # 次日凌晨00:30再启
    now_dt = datetime.datetime.now()
    next_dt = now_dt.replace(hour=0, minute=30, second=0, microsecond=0) + relativedelta(days=1)
    time = (next_dt - now_dt).seconds

    timing('regular', msg='定时任务')
    timing.set_time(time)
    local_monitor('regular')


@command_false_no_task.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if api_check_task__exec_by_bot_at(event, timing, local_monitor):
        return

    await command_false_no_task.send(Reply_Receive)


@command_false_no_hp.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if api_check_task__exec_by_bot_at(event, timing, monitor):
        return

    monitor('pause', msg='状态异常')


@command_false_no_money.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if api_check_task__exec_by_bot_at(event, timing, monitor):
        return

    monitor('pause', msg='灵石不足')


@command_false_time.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    """刷新与完成返回信息一样 但是刷新cd未使用"""
    if api_check_task__exec_by_bot_at(event, timing):
        return
    if not monitor.check('is_waiting'):
        return

    msg_str = str(msg)

    pattern = r'剩余CD:([\d.]+)秒'
    time = float(re.search(pattern, msg_str).group(1))

    monitor.set_time(time)
    monitor('error')


"""core"""


@command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not api_check_config(event, at_me=True):
        return

    # 启动
    if not timing.check('is_usable'):
        return
    timing('start')

    """监听"""
    while True:
        if timing.check('is_finish'):
            break

        timing('running')
        monitor('init', start=True)
        local_monitor('init', start=True)

        """ 宗门任务 接取 """
        await _task_receive(_cmd=command)

        """ 宗门任务 刷新 """
        await _task_refresh(_cmd=command, _event=event)

        """ 宗门任务 完成 """
        await _task_completed(_cmd=command, _event=event)

        # 执行等待
        if timing.check('is_finish'):
            break

        if timing.check('is_regular'):
            await asyncio.sleep(timing.time)

    timing('init', msg='自动结束')


async def _task_receive(_cmd):
    """接取任务"""
    timing(msg='宗门任务 接取')
    await _cmd.send(Reply_Receive)
    await asyncio.sleep(5)


async def _task_refresh(_cmd, _event):
    """刷新任务"""
    if local_monitor.check('is_mutual'):
        timing(msg='宗门任务 刷新')
        # 加载异步监听
        loop = LoopEvent(_event, name='zmrw_sx_loop')

        went_await = loop.add(loop.loop_await_cmd('宗门任务 刷新', monitor=local_monitor))
        went_send = loop.add(loop.loop_send_cmd('宗门任务 刷新', cmd=_cmd, msg=Reply_Refresh, time=5 * 60))
        await went_await
        await went_send


async def _task_completed(_cmd, _event):
    """完成任务"""
    if local_monitor.check('is_done'):
        timing(msg='宗门任务 完成')
        # 加载异步监听
        loop = LoopEvent(_event, name='zmrw_wc_loop')
        while True:
            went_await = loop.add(loop.loop_await_cmd('宗门任务 完成', monitor=monitor))
            went_send = loop.add(loop.loop_send_cmd('宗门任务 完成', cmd=_cmd, msg=Reply_Completed))

            await went_await
            await went_send

            if monitor.check('is_done'):
                break
            elif monitor.check('is_pause'):
                # 暂停状态 等待状态解除
                timing('pause', msg=monitor.msg)
                await loop.add(loop.loop_pause_cmd('pause zmrw wc', monitor=timing))
            else:
                timing.set_time(monitor.time)
                monitor('waiting')

            # 执行等待
            if timing.check('is_finish'):
                break
            timing('waiting')
            await timing.sleep()


@exit_command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    api_update_state__by_at(event, timing, state={
        'state': 'done',
        'msg': '计划退出',
    })
