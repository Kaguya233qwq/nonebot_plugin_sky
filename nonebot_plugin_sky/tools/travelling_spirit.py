import json
import re

import httpx
from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageSegment


class Travelling:
    """国服复刻类"""

    def __init__(self):
        self.url = 'https://weibo.com/ajax/statuses/mymblog?uid=5539106873&feature=0'
        self.longtext = 'https://weibo.com/ajax/statuses/longtext?id='
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                          '/62.0.3202.9 Safari/537.36',
            'cookie': 'SUB=_2AkMUd3SHf8NxqwFRmP8Ty2Pna4VwywzEieKiK4VcJRMxHRl'
                      '-yT9jqnAOtRB6P_daaLXfdvYkPfvZhXy3bTeuLdBjWXF9;'  # 未登录时的cookie直接写死
        }
        self.copyright_ = ('------------'
                           '\r【数据来源：微博@光遇陈陈】\n'
                           '--本插件仅做数据展示之用，著作权归原文作者所有。'
                           '转载或转发请附文章作者微博--')

    async def get_mblog(self, max_page):
        """获取微博 @光遇陈陈 复刻先祖详情"""

        for page in range(1, max_page + 1):
            param = {
                'page': str(page)
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url=self.url,
                    headers=self.headers,
                    params=param
                )
                content = json.loads(response.text)
                overhead = content['data']['list']
                for log in overhead:
                    if (
                            log.get('pic_infos') and
                            re.findall(
                                r'#(光遇)*([\u4e00-\u9fa5])*(先祖)*(复刻)+#',
                                log['text_raw']
                            ) and
                            '国服' in log['text_raw']
                            # 讲声多谢陈陈哥啦
                    ):
                        return log
        return None

    async def get_data(self):
        """获取复刻数据"""
        results = MessageSegment.text('')
        overhead = await self.get_mblog(40)
        if overhead:
            pic_infos = overhead['pic_infos']
            for pic in pic_infos:
                large_url = pic_infos[pic]['large']['url']
                img = MessageSegment.image(large_url)
                results += img
            results += self.copyright_
        else:
            notice = '没有找到国服复刻先祖的数据'
            logger.warning(notice)
            results += MessageSegment.text(notice)
        return results
