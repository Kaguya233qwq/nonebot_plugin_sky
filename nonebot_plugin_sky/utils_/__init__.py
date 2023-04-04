import os
import re
from datetime import datetime
from typing import Union

import httpx
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


async def weibo_image(url, file_name):
    """
    将微博图片缓存到本地，返回绝对路径的file URI
    :param url: 图片链接
    :param file_name:文件名
    :return: file URI
    """
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/74.0.3729.169 Safari/537.36',
        'cookie': 'SUB=_2AkMUd3SHf8NxqwFRmP8Ty2Pna4VwywzEieKiK4VcJRMxHRl'
                  '-yT9jqnAOtRB6P_daaLXfdvYkPfvZhXy3bTeuLdBjWXF9;',
        'referer': 'https://weibo.com/'
    }
    async with httpx.AsyncClient(timeout=10000) as client:
        res = await client.get(
            url=url,
            headers=headers
        )
        data = res.content
    if not os.path.exists('Sky/Cache'):
        os.mkdir('Sky/Cache')
    with open(f'Sky/Cache/{file_name}.jpg', 'wb') as f:
        f.write(data)
        f.close()
    abspath = os.path.abspath(f'Sky/Cache/{file_name}.jpg')
    return 'file:///' + abspath
