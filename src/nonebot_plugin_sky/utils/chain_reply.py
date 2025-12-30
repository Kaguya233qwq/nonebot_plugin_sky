from typing import Sequence

from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot

from .bot_loader import config


async def chain_reply(bot: Bot, msg_list: Sequence[str | MessageSegment]):
    """
    构造聊天记录转发消息

    :param bot:
    :param msg:
    :return:
    """
    nick = config.nickname
    chain = []
    for msg in msg_list:
        data = {
            "type": "node",
            "data": {"name": nick, "uin": bot.self_id, "content": msg},
        }
        chain.append(data)
    return chain
