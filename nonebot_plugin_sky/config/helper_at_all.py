from nonebot import on_command, logger
from nonebot.internal.matcher import Matcher

from ..config.load_config import get_config as config
from ..config.load_config import cfg_path
from .command import get_cmd_alias

cfg_path_ = cfg_path()


def get_at_all() -> bool:
    try:
        value = config().getboolean('Helper', 'at_all')
        return value
    except Exception as e:
        str(e)


def at_all_on() -> None:
    global cfg_path_
    config().set('Helper', 'at_all', 'True')

    config().write(open(cfg_path_, 'w+'))
    logger.success('小助手艾特全体：开启')


def at_all_off() -> None:
    global cfg_path_
    config().set('Helper', 'at_all', 'False')

    config().write(open(cfg_path_, 'w+'))
    logger.success('小助手艾特全体：关闭')


At_all = get_at_all()

AtAllOn = on_command("at all -on", aliases=get_cmd_alias('at_all_on'))
AtAllOff = on_command("at all -off", aliases=get_cmd_alias('at_all_off'))


@AtAllOn.handle()
async def on_handle(matcher: Matcher):
    try:
        global At_all
        at_all_on()
        await matcher.send('小助手艾特全体开启成功')
        At_all = get_at_all()

    except Exception as e:
        logger.error('小助手艾特全体开启失败')
        await matcher.send('开启失败！原因：%s' % str(e))


@AtAllOff.handle()
async def off_handle(matcher: Matcher):
    try:
        global At_all
        at_all_off()
        await matcher.send('小助手艾特全体关闭成功')
        At_all = get_at_all()

    except Exception as e:
        logger.error('小助手艾特全体关闭失败')
        await matcher.send('关闭失败！原因：%s' % str(e))


def at_all() -> bool:
    return At_all


__all__ = (
    "on_handle",
    "off_handle",
    "at_all"
)
