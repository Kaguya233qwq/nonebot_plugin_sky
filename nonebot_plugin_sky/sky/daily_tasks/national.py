import json

import httpx
from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageSegment

from ...utils_.date_util import get_today


class SkyDaily:
    """国服光遇类"""

    def __init__(self):
        self.url = 'https://weibo.com/ajax/statuses/mymblog?uid=7360748659&page=1&feature=0'
        self.longtext = 'https://weibo.com/ajax/statuses/longtext?id='
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                          '/62.0.3202.9 Safari/537.36',
            'cookie': 'SUB=_2AkMUd3SHf8NxqwFRmP8Ty2Pna4VwywzEieKiK4VcJRMxHRl'
                      '-yT9jqnAOtRB6P_daaLXfdvYkPfvZhXy3bTeuLdBjWXF9;'  # 未登录时的cookie直接写死
        }
        self.copyright_ = ('------------'
                           '\r【数据来源：微博@今天游离翻车了吗】\n'
                           '--本插件仅做数据展示之用，著作权归原文作者所有。'
                           '转载或转发请附文章作者微博--')

    async def get_mblog(self, today):
        """获取微博 @今天游离翻车了吗 今日攻略详情"""

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=self.url,
                headers=self.headers)
            content = json.loads(response.text)
            overhead = content['data']['list']
            for log in overhead:
                if today in log['text_raw']:
                    return log
            return None

    async def get_longtext(self, mblog_id: str):
        """获取微博 @今天游离翻车了吗 今日攻略长文本"""

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=self.longtext + mblog_id,
                headers=self.headers)
            content = json.loads(response.text)
            longtext = content['data']['longTextContent']
            return longtext

    async def get_data(self):
        """获取今日攻略数据"""
        results = MessageSegment.text('')
        today = await get_today()
        overhead = await self.get_mblog(today)
        if overhead:
            mblog_id = overhead['mblogid']
            longtext = await self.get_longtext(mblog_id)
            results += MessageSegment.text(longtext)
            pic_infos = overhead['pic_infos']
            for pic in pic_infos:
                large_url = pic_infos[pic]['large']['url']
                img = MessageSegment.image(large_url)
                results += img
            results += self.copyright_  # 附加版权信息
        else:
            notice = '今日数据还未更新，请耐心等候'
            logger.warning('今日数据还未更新，请耐心等候')
            results += MessageSegment.text(notice)
        return results
