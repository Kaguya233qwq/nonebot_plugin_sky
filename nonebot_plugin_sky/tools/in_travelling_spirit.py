from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageSegment

from .travelling_spirit import Travelling


async def get_data():
    """获取今日攻略数据"""
    copyright_ = ('------------'
                  '\r【数据来源：微博@光遇陈陈】\n'
                  '--本插件仅做数据展示之用，著作权归原文作者所有。'
                  '转载或转发请附文章作者微博--')
    travel = Travelling()
    results = MessageSegment.text('')
    overhead = await travel.get_mblog('【国际服】', 100)
    if overhead:
        pic_infos = overhead['pic_infos']
        for pic in pic_infos:
            large_url = pic_infos[pic]['large']['url']
            img = MessageSegment.image(large_url)
            results += img
        results += copyright_
    else:
        notice = '没有找到国际服复刻先祖的数据'
        logger.warning(notice)
        results += MessageSegment.text(notice)
    return results
