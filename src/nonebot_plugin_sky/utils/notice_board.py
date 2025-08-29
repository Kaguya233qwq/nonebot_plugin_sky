import httpx
from bs4 import BeautifulSoup
import logging
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment
from ..config.command import get_cmd_alias

logging.captureWarnings(True)  # 去掉建议使用SSL验证的显示


async def get_plugin_notice():
    url = "https://gitee.com/Kaguyaaa/notice_manager/blob/main/public_sky/notice.txt"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome"
        "/62.0.3202.9 Safari/537.36"
    }
    async with httpx.AsyncClient(verify=False, timeout=None) as client:
        res = await client.get(url=url, headers=headers)
        bs = BeautifulSoup(res.text, "lxml")
        results_ = ""
        notice_list = bs.find_all(class_="line")
        for notice in notice_list:
            results_ += notice.text
        return results_


Notice = on_command("noticeboard", aliases=get_cmd_alias("noticeboard"))


@Notice.handle()
async def notice_handle():
    results_ = await get_plugin_notice()
    await Notice.send(MessageSegment.text(results_))


__all__ = ("notice_handle", "Notice")
