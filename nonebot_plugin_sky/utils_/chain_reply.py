from typing import Union

from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot

from .bot_loader import CONFIG


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
            "name": CONFIG.NICKNAME,
            "uin": f"{bot.self_id}",
            "content": msg
        },
    }
    chain.append(data)
    return chain
