import asyncio
from typing import List
from pydantic import BaseModel

import nonebot
from nonebot import logger


class Config(BaseModel):
    """Sky的.env配置项"""

    """bot的昵称"""
    nickname: List[str] | str

    """欲开启所有推送功能的群号列表"""
    recv_group_id: List[str] = []
    
    weibo_cookie: str = ""


try:
    config: Config = nonebot.get_plugin_config(Config)
    if isinstance(config.nickname, list):
        if len(config.nickname) == 0 or config.nickname[0] == "":
            config.nickname = "Sky"
        else:
            config.nickname = config.nickname[0]
    elif isinstance(config.nickname, str):
        if config.nickname == "":
            config.nickname = "Sky"
    else:
        config.nickname = "Sky"
    logger.success(f"Hi~ [Bot]{config.nickname} loaded successfully.")
    logger.success(f"[sky插件推送服务] 以下群组已启用：{config.recv_group_id}")
except Exception:
    logger.warning("您还未配置接收推送服务消息的群id，推送功能将无法正常工作")


async def get_the_bot():
    """
    连接bot实例

    :return: None
    """
    while True:
        try:
            bot = nonebot.get_bot()
            logger.success("bot实例获取成功")
            return bot
        except Exception:
            logger.error("bot实例获取失败，正在重试..")
        await asyncio.sleep(2)
