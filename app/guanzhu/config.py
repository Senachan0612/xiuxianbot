"""灌注 用户信息"""

import asyncio
import os
import json
import re
from collections import namedtuple, defaultdict

from nonebot.plugin.on import on_regex, on_fullmatch, on_startswith
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, GROUP
from nonebot.params import CommandArg
from nonebot.rule import to_me, regex

from . import (
    DataPath,
    Monitor, LoopEvent,
    xxBot,
    eventCheck,
)

"""配置信息"""


class GuanZhuConfig:
    path = r'%s\%s' % (DataPath, 'GuanZhu.json')
    data = {}
    Goods = namedtuple('Goods', 'id, name, value, type')

    """解析相关"""
    solve_user = False
    solve_goods = {}
    solve_page_sets = {''}

    def __init__(self):
        self.load()

    def init(self):
        """灌注清单 生成"""
        if not os.path.isdir(DataPath):
            os.makedirs(DataPath)

        with open(self.path, mode='w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def load(self):
        """灌注清单 加载"""

        def _f(_data):
            for key, val in _data.items():
                yield key, {_key: {float(_k): _v for _k, _v in _val.items()} for _key, _val in val.items()}

        if os.path.isfile(self.path):
            # 加载用户配置
            with open(self.path, mode='r', encoding='utf-8') as f:
                self.data = dict(_f(json.load(f)))
        self.init()

    def update(self, goods_fy=False, goods_pg=False, goods_bg=False):
        """灌注清单 更新"""
        old_data = self.data.get(self.solve_user, {})
        if goods_fy is False:
            goods_fy = old_data.get('防具', [])
        if goods_fy is False:
            goods_pg = old_data.get('普攻', [])
        if goods_fy is False:
            goods_bg = old_data.get('暴攻', [])

        self.data[self.solve_user] = {
            '防具': goods_fy,
            '普攻': goods_pg,
            '暴攻': goods_bg,
        }

    def save(self):
        """灌注清单 保存"""
        return self.init()

    def get_config(self, uname):
        """获取用户配置"""
        return self.data.setdefault(uname, {})

    def print_config(self, uname=False, data=False):
        """输出用户配置"""
        if uname:
            data = {uname: self.get_config(uname)}
        elif data is False:
            data = self.data

        def _f():
            for _index, (_name, _dict) in enumerate(data.items()):
                if _index:
                    yield f'\n>>> 用户：{_name}',
                else:
                    yield f'>>> 用户：{_name}',
                for _type, _value in _dict.items():
                    yield f'> {_type}',
                    for _key, _val in _value.items():
                        yield _key, _val

        return Message('\n'.join(''.join('{: <10}'.format(_item) for _item in item) for item in _f()))

    def solve(self, name):
        """启动解析模式"""
        self.solve_page_sets = {''}
        self.solve_user = name
        self.solve_goods = defaultdict(list)

    def solve_finish(self):
        """完成解析模式"""
        self.solve__set_zb()
        self.solve_user = False

    def solve__get_zb(self, msg):
        """处理装备信息"""
        # 页码信息
        page_match = re.compile(r'当前最大页数(\d+), 目前(\d+)页').search(msg)
        if not page_match:
            return
        page_max, page_min = page_match.groups()

        # 首次执行，录入页码信息
        if not self.solve_page_sets:
            self.solve_page_sets.update(range(int(page_min) + 1, int(page_max) + 1))
        elif int(page_min) not in self.solve_page_sets:
            return

        pattern = re.compile(r'编号【(\d+)】(.*?)：.*?\n.*?(-?\d+)%(减伤率|攻击力)')
        for _num, _name, _value, _type in pattern.findall(msg):
            self.solve_goods[_type].append(self.Goods(_num, _name, float(_value) * 0.01, _type))

        return True

    def solve__set_zb(self):
        """设置物品信息"""
        solve_goods = self.solve_goods

        # 防具
        goods_fy = {float(rec.value): f'装备道具 {rec.id}' for rec in solve_goods['减伤率']}

        # 普攻
        goods_pg = {}
        # 暴攻
        goods_bg = {}

        for rec in self.solve_goods['攻击力']:
            if rec.name == '傻逼喇叭':
                if not goods_pg:
                    goods_pg[float(rec.value)] = f'装备道具 {rec.id}'
                continue
            goods_bg[float(rec.value)] = f'装备道具 {rec.id}'

        self.update(goods_fy, goods_pg, goods_bg)
        self.save()

    def solve__get_zb_msg(self, event, name):
        """处理装备信息 交互信息"""
        if name:
            return xxBot.msg__at(event.user_id) + f'装备库{self.solve_page_sets.pop()}'
        else:
            return xxBot.msg__at_xxbot + f'装备库{self.solve_page_sets.pop()}'


# 灌注配置
gz_config = GuanZhuConfig()

"""录入"""

# 注册监控器
timing = Monitor(name='灌注配置录入')
monitor = Monitor(name='灌注配置录入监控')

command = on_startswith(('装备录入', '功法录入'), rule=to_me(), priority=60, block=True)
exit_command = on_fullmatch(('关闭装备录入', '!装备录入', '!lr'), rule=to_me(), priority=60, block=True)


@command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    # 启动
    if not timing('start'):
        return

    cate, name = re.compile(r'(装备|功法|装备功法|功法装备)录入\s*(\S*)').match(str(event.message)).groups()
    if not name and not eventCheck.api_check__app_event(event):
        return

    timing('running', msg=name)

    if cate != '功法':
        await get_zb(command, event, name)
    elif cate != '装备':
        await get_gf(command, event)

    timing('init')
    await command_print.finish(xxBot.msg__at(event.user_id) + Message('录入完成！'))


"""录入装备"""


async def get_zb(cmd, event, name):
    """录入装备"""
    # 加载异步监听
    loop = LoopEvent(event)

    gz_config.solve(name)
    while gz_config.solve_page_sets:
        if timing.check('is_finish'):
            break

        monitor('init')
        went_await = loop.add(loop.loop_await_cmd('zb', monitor=monitor))
        went_send = loop.add(loop.loop_send_cmd('zb', cmd=cmd, count=3, msg=gz_config.solve__get_zb_msg(event, name)))
        await went_await
        await went_send
    gz_config.solve_finish()


get_zb_pattern = r'^.*?(\S+)的背包.*?\n'
command_get_zb_status = on_regex(get_zb_pattern, permission=GROUP, priority=1000, block=True)


@command_get_zb_status.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not monitor.check('is_normal'):
        return

    str_msg = str(event.message[-1])
    # todo 未知原因 此处name仅能做模糊查询
    user = re.compile(get_zb_pattern).match(str_msg).groups()[0]
    if gz_config.solve_user and not user.endswith(str(gz_config.solve_user)):
        return
    elif gz_config.solve_user == '':
        if not eventCheck.api_check__xxbot_event(event):
            return
        gz_config.solve_user = user

    if gz_config.solve__get_zb(str_msg):
        monitor('done')


"""录入功法"""


async def get_gf(cmd, event):
    """录入功法"""
    ...


"""查看录入"""

command_print = on_startswith(('查看录入', '录入查看'), rule=to_me(), priority=60, block=True)


@command_print.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    _, name = re.compile(r'(查看录入|录入查看)\s*(\S*)').match(str(event.message)).groups()

    if not name and eventCheck.api_check__xxbot_event(event):
        return

    await command_print.finish(gz_config.print_config(uname=name))
