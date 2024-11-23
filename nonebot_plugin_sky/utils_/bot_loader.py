import asyncio
from typing import List

import nonebot
from nonebot import logger, Bot


class Config:
    """Sky的.env配置项"""
    """bot的昵称"""
    NICKNAME: str = "unnamed"

    """欲开启所有推送功能的群号列表"""
    RECV_GROUP_ID: List[str] = []

try:
    config = nonebot.get_driver().config
    if config.nickname:
        Config.NICKNAME = list(config.nickname)[0]
    if config.recv_group_id:
        Config.RECV_GROUP_ID = config.recv_group_id
    logger.success(f'Hi~ [Bot]{Config.NICKNAME} loaded successfully.')
    logger.success(f'[sky插件推送服务] 以下群组已启用：{Config.RECV_GROUP_ID}')
except Exception:
    logger.warning('您还未配置接收推送服务消息的群id，推送功能将无法正常工作')

async def get_the_bot() -> Bot:
    """
    连接bot实例

    :return: None
    """
    while True:
        try:
            bot = nonebot.get_bot()
            logger.success('bot连接成功')
            return bot
        except Exception:
            logger.error(f'bot实例获取失败，正在重试..')
        await asyncio.sleep(2)
