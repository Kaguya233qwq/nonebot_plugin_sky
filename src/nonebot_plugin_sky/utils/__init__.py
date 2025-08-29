import os
from pathlib import Path
import re
from datetime import datetime
from typing import Sequence

import httpx
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from .chain_reply import chain_reply
import threading
import time

# 确保配置项被加载
from . import bot_loader as bot_loader

clear_cache_time = 0
lock = threading.Lock()
CACHE_PATH = "Sky/Cache"
day_second = 60 * 60 * 24


def clear_cache(before_day=30, force=False):
    # 加锁
    if not lock.acquire(False):
        return 0
    global clear_cache_time
    try:
        now = time.time()
        if not force:
            # 1天内清理过的暂时不清理
            if now - clear_cache_time < day_second:
                return 0
        file_name_list = os.listdir(CACHE_PATH)
        cleared = 0
        if file_name_list:
            for file_name in file_name_list:
                file_path = CACHE_PATH + "/" + file_name
                ctime = os.path.getctime(file_path)
                if (now - ctime) / day_second > before_day:
                    Path(file_path).unlink()
                    cleared = cleared + 1
        clear_cache_time = now
        lock.release()
        return cleared
    except Exception as e:
        lock.release()
        raise e


def time_no_more(date, hour, minute):
    """
    UTC时间判断工具
    """
    time_obj = datetime.strptime(date, "%a %b %d %H:%M:%S +0800 %Y")
    if time_obj.hour == hour and time_obj.minute <= minute:
        return True
    else:
        return False


async def send_forward_msg(
    bot: Bot, event: MessageEvent, messages: Sequence[str | MessageSegment]
):
    """
    自动判断消息类型发送对应转发消息

    :param bot:
    :param event:
    :param results:
    :return:
    """
    chain = await chain_reply(bot, messages)
    msg_type = event.message_type
    if msg_type == "group":
        group_id = re.findall(r"_(\d{5,})_", event.get_session_id())[0]
        await bot.send_group_forward_msg(group_id=group_id, messages=chain)
    elif msg_type == "private":
        await bot.send_private_forward_msg(
            user_id=event.get_session_id(), messages=chain
        )


async def parse_img_url(url: str, file_name):
    """
    将微博图片缓存到本地，返回绝对路径的file URI
    :param url: 图片链接
    :param file_name:文件名
    :return: file URI
    """
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        " AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/74.0.3729.169 Safari/537.36",
        "cookie": "SUB=_2AkMUd3SHf8NxqwFRmP8Ty2Pna4VwywzEieKiK4VcJRMxHRl"
        "-yT9jqnAOtRB6P_daaLXfdvYkPfvZhXy3bTeuLdBjWXF9;",
        "referer": "https://weibo.com/",
    }
    file_path: Path = Path(CACHE_PATH) / f"{file_name}.jpg"
    if url.endswith("gif"):
        # gif文件过大无法发送，故排除
        return ""
    if not file_path.exists():
        async with httpx.AsyncClient(timeout=10000) as client:
            res = await client.get(url=url, headers=headers)
            data = res.content
        if not Path(CACHE_PATH).exists():
            Path(CACHE_PATH).mkdir()
        with open(file_path, "wb") as f:
            f.write(data)
    # 创建清理线程异步执行
    threading.Thread(target=clear_cache).start()
    return file_path.resolve().as_uri()
