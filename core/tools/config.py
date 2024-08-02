"""xxbot配置"""

import re
import os
import json

import nonebot

from . import DataPath
# 配置前缀
ConfigPrefix = 'XiuXian'


class XiuXianConfig:
    # 配置前缀
    _prefix = ConfigPrefix.lower()
    # bot配置字典
    _xiuxian_config = nonebot.get_driver().config.dict().get(_prefix, {})
    # 注释
    _pattern = r'<\*.*?\*>'
    # 路径
    _path_dir = DataPath
    _path_file = r'%s\%s' % (DataPath, 'Config.json')

    def __init__(self):
        # 配置字典
        self.config_dict = {}

        # 加载配置
        self.load()

    def __getitem__(self, item, default=None):
        if isinstance(item, tuple):
            item, default, *_ = *item, None, None
        return self.config_dict.get(item.lower(), default)

    def load(self):
        """加载xxbot配置"""
        # 读取用户配置
        config_dict = self.get_user_config()

        if config_dict and isinstance(config_dict, dict):
            self.config_dict = config_dict
        else:
            # 读取bot配置
            config_dict = dict(self.get_bot_config())
            self.config_dict = config_dict
            # 生成用户配置
            self.set_user_config()
        return config_dict

    def update(self, configs: dict, write=True):
        """更新配置"""

        def _f():
            for k, v in configs.items():
                if isinstance(k, str):
                    k = k.lower()
                yield k, v

        self.config_dict.update(dict(_f()))

        if write:
            self.set_user_config()

    def get_bot_config(self):
        """加载bot配置"""
        for key, val in self._xiuxian_config.items():
            if isinstance(val, str):
                try:
                    val = re.sub(self._pattern, '', val)
                    val = eval(val)
                except Exception:
                    val = None
            yield key, val

    def get_user_config(self):
        """加载用户配置"""
        if os.path.isfile(self._path_file):
            # 加载用户配置
            try:
                with open(self._path_file, mode='r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

    def set_user_config(self):
        """更新用户配置"""
        try:
            if not os.path.isdir(self._path_dir):
                os.makedirs(self._path_dir)

            with open(self._path_file, mode='w', encoding='utf-8') as f:
                json.dump(self.config_dict, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


Config = XiuXianConfig()
