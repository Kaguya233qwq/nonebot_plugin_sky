from nonebot import on_command, logger
from nonebot.internal.matcher import Matcher

from .command import get_cmd_alias
from .loader import loaded_config,save_to_config


def get_is_forward() -> bool:
    try:
        value = loaded_config().getboolean("Message", "forward")
        return value
    except Exception:
        return False


def on() -> None:
    save_to_config("Message", "forward", "True")
    logger.success("消息转发：开启")


def off() -> None:
    save_to_config("Message", "forward", "False")
    logger.success("消息转发：关闭")


Forward = get_is_forward()

On = on_command("forward -on", aliases=get_cmd_alias("forward_on"))
Off = on_command("forward -off", aliases=get_cmd_alias("forward_off"))


@On.handle()
async def on_handle(matcher: Matcher):
    try:
        global Forward
        on()
        await matcher.send("消息转发开启成功")
        Forward = get_is_forward()

    except Exception as e:
        logger.error("消息转发开启失败")
        await matcher.send("开启失败！原因：%s" % str(e))


@Off.handle()
async def off_handle(matcher: Matcher):
    try:
        global Forward
        off()
        await matcher.send("消息转发关闭成功")
        Forward = get_is_forward()

    except Exception as e:
        logger.error("消息转发关闭失败")
        await matcher.send("关闭失败！原因：%s" % str(e))


def is_forward() -> bool:
    return Forward


__all__ = ("on_handle", "off_handle", "is_forward")
