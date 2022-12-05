from nonebot_plugin_sky.config.load_config import load, get_path
from nonebot import on_command, logger
from nonebot.internal.matcher import Matcher

cfg_path = get_path()


def conf():
    config = load()
    value = config.getboolean('Message', 'forward')
    logger.success('读取配置成功')
    return value


def on():
    global cfg_path
    config = load()
    config.set('Message', 'forward', 'True')

    config.write(open(cfg_path, 'w+'))
    logger.success('消息转发：开启')


def off():
    global cfg_path
    config = load()
    config.set('Message', 'forward', 'False')

    config.write(open(cfg_path, 'w+'))
    logger.success('消息转发：关闭')


forward = conf()

On = on_command("f -on", aliases={"开启消息转发"})
Off = on_command("关闭消息转发", aliases={"关闭消息转发"})


@On.handle()
async def on_handle(matcher: Matcher):
    try:
        global forward
        on()
        await matcher.send('消息转发开启成功')
        forward = conf()

    except Exception as e:
        logger.error('消息转发开启失败')
        await matcher.send('开启失败！原因：%s' % str(e))


@Off.handle()
async def off_handle(matcher: Matcher):
    try:
        global forward
        off()
        await matcher.send('消息转发关闭成功')
        forward = conf()

    except Exception as e:
        logger.error('消息转发关闭失败')
        await matcher.send('关闭失败！原因：%s' % str(e))


def is_forward():
    return forward
