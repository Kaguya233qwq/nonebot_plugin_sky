from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot

from nonebot_plugin_sky.utils_.config_loader import Nick


async def chain_reply(
        # 构造聊天记录转发消息
        bot: Bot,
        msg: MessageSegment
):
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
