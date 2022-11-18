import datetime

from nonebot import logger


async def get_today():
    """获取今日日期"""
    date = datetime.date.today().timetuple()
    today = str(date.tm_mon) + '月' + str(date.tm_mday) + '日'
    today_format = str(date.tm_mon) + '.' + str(date.tm_mday)
    logger.info('今天是：{}'.format(today))
    return today_format
