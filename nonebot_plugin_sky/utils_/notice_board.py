import httpx
from bs4 import BeautifulSoup
import logging
from nonebot import logger, on_command

logging.captureWarnings(True)  # 去掉建议使用SSL验证的显示


async def get_notice():
    url = 'https://github.com/Kaguya233qwq/notice_manager/blob/main/public_sky/notice.txt'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                      '/62.0.3202.9 Safari/537.36'
    }
    async with httpx.AsyncClient(verify=False, timeout=None) as client:
        res = await client.get(
            url=url,
            headers=headers
        )
        bs = BeautifulSoup(res.text)
        results_ = ''
        notice_list = bs.find_all(class_='blob-code blob-code-inner js-file-line')
        for notice in notice_list:
            results_ += notice.text+'\n'
        print(notice_list)
        return results_


Notice = on_command("插件公告")


@Notice.handle()
async def _():
    results_ = await get_notice()
    await Notice.send(results_)
