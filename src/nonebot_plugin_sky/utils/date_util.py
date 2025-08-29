import datetime

from nonebot import logger


async def get_today():
    """获取今日日期"""
    date = datetime.date.today()
    today = str(date.month) + '月' + str(date.day) + '日'
    today_format = {
        'month': str(date.month),
        'day': str(date.day)
    }
    logger.info(f'今天是：{today}')
    return today_format


__all__ = [
    "get_today"
]
