"""工具包"""

__all__ = [
    'Config',  # xxbot配置
    'xxBot',  # xxbot
    'eventCheck',  # event校验
]

from .. import DataPath

from .config import Config

from .bot import xxBot

from . import eventCheck
