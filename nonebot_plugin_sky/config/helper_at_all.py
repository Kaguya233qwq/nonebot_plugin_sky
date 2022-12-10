from nonebot_plugin_sky.config.load_config import load, get_path
from nonebot import on_command, logger
from nonebot.internal.matcher import Matcher

from nonebot_plugin_sky.config.load_config import get_config as config

cfg_path = get_path()


def get_at_all():
    try:
        value = config().getboolean('Helper', 'at_all')
        return value
    except Exception as e:
        str(e)

def at_all_on():
    global cfg_path
    config().set('Helper', 'at_all', 'True')

    config().write(open(cfg_path, 'w+'))
    logger.success('小助手艾特全体：开启')


def at_all_off():
    global cfg_path
    config().set('Helper', 'at_all', 'False')

    config().write(open(cfg_path, 'w+'))
    logger.success('小助手艾特全体：关闭')


At_all = get_at_all()

AtAllOn = on_command("f -on", aliases={"开启艾特全体"})
AtAllOff = on_command("f -off", aliases={"关闭艾特全体"})


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


def at_all():
    return At_all
