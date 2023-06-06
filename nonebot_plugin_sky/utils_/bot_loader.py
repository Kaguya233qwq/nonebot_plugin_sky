import asyncio
from typing import Union, List

import nonebot
from nonebot import logger, Bot
from pydantic import BaseModel


class Config(BaseModel):
    """Sky的.env配置项"""
    """bot的昵称"""
    NICKNAME: Union[List[str], str]

    """欲开启雨林干饭小助手功能的群号，支持字符串和列表"""
    RECV_GROUP_ID: Union[List[str], str]


CONFIG: Config

try:
    nickname = 'Unnamed'
    recv_group_id = []
    __config = nonebot.get_driver().config
    if __config.nickname:
        nickname = __config.nickname
    if __config.recv_group_id:
        recv_group_id = __config.recv_group_id
    CONFIG = Config(
        NICKNAME=nickname,
        RECV_GROUP_ID=recv_group_id
    )
    nick = CONFIG.NICKNAME
    recv_id = CONFIG.RECV_GROUP_ID
    logger.success(f'Hi~ [Bot]{nick} loaded successfully.')
    logger.success('[雨林干饭小助手] 以下群组已启用：%s' % recv_id)
except Exception as e:
    e.__str__()
    CONFIG = Config(
        NICKNAME='未命名',
        RECV_GROUP_ID=[]
    )
    logger.warning('您还未配置接收小助手消息的群id，这个功能无法正常工作')


async def connect() -> Bot:
    """
    连接bot实例

    :return: None
    """
    while True:
        try:
            bot = nonebot.get_bot()
            logger.success('bot连接成功')
            return bot
        except Exception as p:
            logger.error('您还未启动go-cqhttp | %s' % p)
        await asyncio.sleep(2)
