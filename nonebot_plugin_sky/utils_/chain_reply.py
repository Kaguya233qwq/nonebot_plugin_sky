from typing import Union

from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot

from ..utils_.bot_loader import Nick


async def chain_reply(
        bot: Bot,
        msg: Union[str, MessageSegment]
) -> list:
    """
    构造聊天记录转发消息

    :param bot:
    :param msg:
    :return:
    """
    chain = []

    data = {
        "type": "node",
        "data": {
            "name": Nick,
            "uin": f"{bot.self_id}",
            "content": msg
        },
    }
    chain.append(data)
    return chain
