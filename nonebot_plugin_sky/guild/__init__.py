from nonebot import get_bot, logger, on_command
from nonebot.exception import ActionFailed


async def check():
    """
    检查 gocq版本、是否加入光萌与光媛频道
    """
    try:
        bot = None
        try:
            bot = get_bot()
        except Exception as e:
            logger.error("go-cqhttp还未启动:%s" % e)
        guild_list = await bot.call_api('get_guild_list')
        id_list = []
        for guild in guild_list:
            id_list.append(guild['guild_id'])
        if '53342781636642213' in id_list and \
                '83098461664034475' in id_list:
            return 'both'
        elif '53342781636642213' in id_list:
            logger.warning("bot已加入光萌频道,但未加入光媛频道")
            return 'cute'
        elif '83098461664034475' in id_list:
            logger.warning("bot已加入光媛频道,但未加入光萌频道")
            return "beauty"
        else:
            logger.error("bot未加入光萌或光媛频道")
            return 'none'
    except ActionFailed:
        logger.error(
            '调用api失败'
        )
        return False