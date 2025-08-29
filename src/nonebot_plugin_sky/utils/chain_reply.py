from typing import Sequence

from nonebot import get_plugin_config
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot

from .bot_loader import Config


async def chain_reply(bot: Bot, msg_list: Sequence[str | MessageSegment]) -> list:
    """
    构造聊天记录转发消息

    :param bot:
    :param msg:
    :return:
    """
    nick = get_plugin_config(Config).nickname
    chain = []
    for msg in msg_list:
        data = {
            "type": "node",
            "data": {"name": nick[0], "uin": f"{bot.self_id}", "content": msg},
        }
        chain.append(data)
    return chain
