"""bot"""

__all__ = [
    'xxBot',
]

import datetime
from collections import namedtuple
from dateutil.relativedelta import relativedelta

import nonebot
from nonebot.adapters.onebot.v11 import Message

from . import Config

App = namedtuple('App', 'timing matcher auto msg at_bot')


class XiuXianBot:
    # bot配置
    _config = Config
    # 应用清单
    apps = {}
    # 自启动
    auto_apps = {}
    # 配置信息
    config_dict = {}
    # 日志信息
    infos = {}

    def __init__(self):
        self.load_configs()

        # 允许群组
        self.GroupIds = self['Group_Ids', []]
        # 超级管理员
        self.SuperManagerIds = self['Super_Manager_Ids', []]
        # 管理员
        self.ManagerIds = list(set(self.SuperManagerIds + self['Manager_Ids', []]))
        # 修仙botID
        self.xxBotId = self['Bot_Id']

        # 加载应用日志
        self.load_info('app', self.app_config_info())

    def __call__(self, item):
        """获取应用"""
        return self.apps[item]

    def __getitem__(self, item):
        """获取配置"""
        return self._config[item]

    """配置 应用相关"""

    def load_apps(self, data: dict):
        """初始化应用"""

        def _f():
            for k, v in data.items():
                yield k, App(
                    v['timing'],
                    v['cmd'],
                    v.get('auto'),
                    Message(v.get('msg', k)),
                    v.get('at_bot', True)
                )

        self.apps.update(dict(_f()))
        self.load_auto_apps()

    def load_auto_apps(self):
        """加载初始化应用"""
        for name, info in self.apps.items():
            if name not in self.auto_apps:
                self.update_auto_apps(name, valid=info.auto)

    def update_auto_apps(self, name, valid=True):
        """修改初始化应用"""
        self.auto_apps[name] = bool(valid)
        self.update_configs({
            # 自启动应用
            'xxbot_config_auto_apps': self.auto_apps,
        })

    """配置 设置相关"""

    def load_configs(self):
        """初始化配置"""
        if not self['xxbot_config_is_up_to_date']:
            self.update_configs({
                # 自启动应用
                'xxbot_config_auto_apps': self.auto_apps,
                # 配置信息
                'xxbot_config_configs': self.config_dict,
            })
        else:
            self.auto_apps = self['xxbot_config_auto_apps']
            self.config_dict = self['xxbot_config_configs']

    def update_configs(self, configs):
        """更新配置"""
        self._config.update(configs, write=configs.get('xxbot_config_is_up_to_date'))

    def save_configs(self):
        """保存配置"""
        self.update_configs({
            'xxbot_config_is_up_to_date': True,
        })

    def set_security(self, operate, tag, nums):
        """设置授权"""
        if tag == '超管':
            name, security = 'Super_Manager_Ids', self.SuperManagerIds
        elif tag == '用户':
            name, security = 'Manager_Ids', self.ManagerIds
        elif tag == '群组':
            name, security = 'Group_Ids', self.GroupIds
        else:
            return

        if operate == '设置授权':
            security.extend(set(nums) - set(security))
        elif operate == '取消授权':
            nums_index = (security.index(num) for num in (set(security) & set(nums)))
            for index in sorted(nums_index, reverse=True):
                security.pop(index)
        else:
            return

        self.update_configs({
            # 自启动应用
            name: security,
        })
        return security

    """配置 读取相关"""

    @property
    def bot(self):
        """Bot"""
        return nonebot.get_bot()

    @property
    def BotId(self):
        """Bot ID"""
        return self.bot.self_id

    def get_timing(self, name):
        """获取应用监控器"""
        app = self(name)
        return app.timing

    def get_regular_time(self, name, default, days=0):
        """获取定时"""
        hour, minute = self[name, default]
        now_dt = datetime.datetime.now()

        next_dt = now_dt.replace(hour=hour, minute=minute, second=0, microsecond=0) + relativedelta(days=days)
        time = (next_dt - now_dt).total_seconds()
        return now_dt, next_dt, time

    """配置信息 相关"""

    def set_config(self, name, default=False, delete=False):
        """设置配置信息"""
        if delete:
            self['xxbot_config_configs'].pop(name, default)
        else:
            self['xxbot_config_configs'][name] = default

    def get_config(self, name, default=False):
        """获取配置信息"""
        return self['xxbot_config_configs'].setdefault(name, default)

    """日志相关"""

    def load_info(self, name, func):
        """加载日志"""
        self.infos[name] = func

    def get_info(self, name):
        """读取日志"""
        func = self.infos.get(name)
        return func() if callable(func) else ('', '')

    def print_info(self, name, func=False):
        """输出日志"""
        title, infos = func() if callable(func) else self.get_info(name)
        return (
                Message(f'>>>{title}\n')
                + Message('\n'.join(''.join(self.set_format(m) for m in info) for info in infos))
        )

    def status(self):
        """打印状态"""
        msg = Message()
        for name, func in self.infos.items():
            if msg:
                msg += Message('\n\n')
            msg += self.print_info(name, func)
        return msg

    def app_config_info(self):
        """应用相关信息"""

        def _func():
            return '功能清单', [
                ['指令', '状态', '', ],
                *[app.timing.log() for _, app in self.apps.items()]
            ]

        return _func

    @staticmethod
    def set_format(text):
        return '{: <10}'.format(text)

    """通用回复模板"""

    @staticmethod
    def msg__at(_id):
        """at 命令"""
        return Message(f"[CQ:at,qq={_id}] ")

    @property
    def msg__at_xxbot(self):
        """at xxbot 命令"""
        return self.msg__at(self.xxBotId)

    @property
    def msg__at_bot(self):
        """at bot 命令"""
        return self.msg__at(self.BotId)

    """通用校验"""

    def check_is_gid(self, _id):
        """检查 是否拥有群组权限"""
        return _id in self.GroupIds

    def check_is_uid(self, _id):
        """检查 是否拥有用户权限"""
        return _id in self.SuperManagerIds or _id in self.ManagerIds

    def check_is_suid(self, _id):
        """检查 是否拥有超级用户权限"""
        return _id in self.SuperManagerIds

    def check_is_xxbot(self, _id):
        """检查 是否为bot"""
        return _id == self.xxBotId


xxBot = XiuXianBot()
