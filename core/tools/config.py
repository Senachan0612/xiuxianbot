"""xxbot配置"""

import re
import os
import sys

import nonebot

# from . import DataPath
DataPath = 'D:/__env__/bot/autoxx-bot/autoxx_bot/plugins/xiuxianbot/data'


class Config:
    # bot配置字典
    _config_dict = nonebot.get_driver().config.dict()
    # 配置前缀
    _prefix = 'XiuXian__'.lower()
    # 注释
    _pattern = r'<\*.*?\*>'
    # 路径
    _path = r'%s%s' % (DataPath, 'Config.json')

    def __int__(self):
        self.config_dict = self.load_config()

    def load_config(self):
        """加载xxbot配置"""
        if os.path.isfile(self._path):
            ...

        return dict(self._load_config())

    def _load_bot_config(self):
        """加载bot配置"""
        for key, val in self._config_dict.items():
            if not str(key).startswith(self._prefix):
                continue

            try:
                val = re.sub(self._pattern, '', val)
                val = eval(val)
            except Exception:
                val = None

            yield key, val

    def _load_user_config(self):
        """加载用户配置"""

    def __getitem__(self, item):
        if isinstance(item, str):
            item = item.lower()
        return self.config_dict.get(item, None)
