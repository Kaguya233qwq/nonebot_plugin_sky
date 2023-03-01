import re
from datetime import datetime
from typing import Union
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from .chain_reply import chain_reply


def time_no_more(date, hour, minute):
    """
    UTC时间判断工具
    """
    time_obj = datetime.strptime(date, '%a %b %d %H:%M:%S +0800 %Y')
    if time_obj.hour == hour and time_obj.minute <= minute:
        return True
    else:
        return False


async def send_forward_msg(
        bot: Bot,
        event: MessageEvent,
        results: Union[str, MessageSegment]
):
    """
    自动判断消息类型发送对应转发消息

    :param bot:
    :param event:
    :param results:
    :return:
    """
    chain = await chain_reply(bot, results)
    msg_type = event.message_type
    if msg_type == 'group':
        group_id = re.findall('_(\d{5,})_', event.get_session_id())[0]
        await bot.send_group_forward_msg(
            group_id=group_id,
            messages=chain
        )
    elif msg_type == 'private':
        await bot.send_private_forward_msg(
            user_id=event.get_session_id(),
            messages=chain
        )


if __name__ == '__main__':
    date_ = 'Tue Feb 21 12:02:10 +0800 2023'
    print(time_no_more(date_, 12, 10))
