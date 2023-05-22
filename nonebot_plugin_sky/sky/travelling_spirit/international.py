import re
from typing import Union

import httpx
from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageSegment
from ...utils_ import time_no_more, weibo_image


class Travelling:
    """国际服复刻类"""

    def __init__(self):
        self.url = 'https://weibo.com/ajax/statuses/mymblog?uid=5685423899&feature=0'
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

    async def get_mblog(self, max_page) -> Union[str, dict, None]:
        """获取微博 @光遇陈陈 国际服复刻先祖详情"""

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
                overhead = response.json().get('data')
                if overhead:
                    overhead = overhead.get('list')
                    for log in overhead:
                        if (
                                log.get('pic_infos') and
                                re.findall(
                                    r'#(光遇)*([\u4e00-\u9fa5])*(先祖)*(复刻)+#',
                                    log['text_raw']
                                ) and
                                time_no_more(log.get('created_at'), 9, 50) and
                                re.findall('【*?国.*?际.*?服】*?', log['text_raw'])
                                # 错了再改
                        ):
                            return log
                else:
                    return 'invalid'
        return None


async def get_data():
    """获取复刻数据"""
    travel = Travelling()
    results = MessageSegment.text('')
    overhead = await travel.get_mblog(100)
    if overhead == 'invalid':
        return '超过未登录能获取页数的最大值：2'
    if overhead:
        pic_infos = overhead.get('pic_infos')
        if pic_infos:
            for pic in pic_infos:
                large_url = pic_infos[pic]['largest']['url']
                path = await weibo_image(large_url, pic)
                img = MessageSegment.image(path)
                results += img
        else:
            results += overhead['text_raw']
    else:
        notice = '没有找到国际服复刻先祖的数据'
        logger.warning(notice)
        results += MessageSegment.text(notice)
    return results
