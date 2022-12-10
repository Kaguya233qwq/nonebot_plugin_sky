from nonebot_plugin_sky.config.load_config import load, get_path
from nonebot import on_command, logger
from nonebot.internal.matcher import Matcher

from nonebot_plugin_sky.config.load_config import get_config as config

cfg_path = get_path()


def get_is_forward():
    try:
        value = config().getboolean('Message', 'forward')
        return value
    except Exception as e:
        str(e)


def on():
    global cfg_path
    config().set('Message', 'forward', 'True')

    config().write(open(cfg_path, 'w+'))
    logger.success('消息转发：开启')


def off():
    global cfg_path
    config().set('Message', 'forward', 'False')

    config().write(open(cfg_path, 'w+'))
    logger.success('消息转发：关闭')


Forward = get_is_forward()

On = on_command("f -on", aliases={"开启转发模式"})
Off = on_command("f -off", aliases={"关闭转发模式"})


@On.handle()
async def on_handle(matcher: Matcher):
    try:
        global Forward
        on()
        await matcher.send('消息转发开启成功')
        Forward = get_is_forward()

    except Exception as e:
        logger.error('消息转发开启失败')
        await matcher.send('开启失败！原因：%s' % str(e))


@Off.handle()
async def off_handle(matcher: Matcher):
    try:
        global Forward
        off()
        await matcher.send('消息转发关闭成功')
        Forward = get_is_forward()

    except Exception as e:
        logger.error('消息转发关闭失败')
        await matcher.send('关闭失败！原因：%s' % str(e))


def is_forward():
    return Forward
