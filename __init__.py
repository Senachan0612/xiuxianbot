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
    xxBot,  # 加载xxbot
    eventCheck,  # 加载事件校验工具包
)

# 加载应用功能
from . import app

# 加载管理功能
from . import control
