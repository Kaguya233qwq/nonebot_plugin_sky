import nonebot
from nonebot import logger

#  加载bot昵称
try:
    bot_name = nonebot.get_driver().config.nickname
    if not list(bot_name) or list(bot_name) == ['']:
        Nick = '未命名'
    else:
        Nick = list(bot_name)[0]
except Exception as e:
    Nick = '未命名'
    logger.error(e)
    logger.warning('您还没有配置bot的昵称，请先进入env文件配置')
