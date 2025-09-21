import asyncio
from enum import Enum
import json
import os
from pathlib import Path
import aiofiles
from nonebot import logger
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent


async def restart_handle(matcher: Matcher, event: MessageEvent):
    """
    重启bot框架
    前提是需要通过sky脚手架命令运行框架
    """

    def _do_exit(exit_code: int):
        """
        一个同步的退出函数，用于被事件循环调度。
        """
        logger.info(f"事件循环已调度退出，将以代码 {exit_code} 退出进程。")
        os._exit(exit_code)

    async def trigger_restart():
        """
        通过在事件循环的下一个 tick 中调度 os._exit() 来请求重启
        """
        logger.info("插件更新成功，正在调度重启...")

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            logger.error("无法获取事件循环，将强制退出。")
            os._exit(0)
            return
        loop.call_later(0, _do_exit, 0)

    await matcher.send("正在重启Bot...")
    tips = "Bot重启完成"
    if isinstance(event, GroupMessageEvent):
        action = Action.SEND_GROUP_MSG
        signal = Signal(
            name="Send message when connected",
            action=action,
            group_id=event.group_id,
            message=tips,
        )
    else:
        action = Action.SEND_PRIVATE_MSG
        signal = Signal(
            name="Send message when connected",
            action=action,
            user_id=event.user_id,
            message=tips,
        )
    await register_signal(signal)
    await trigger_restart()


SIGNAL_PATH = Path("signal.json")


class Action(Enum):
    SEND_GROUP_MSG = "send_group_msg"
    SEND_PRIVATE_MSG = "send_private_msg"


class Signal:
    def __init__(
        self,
        name: str,
        action: Action,
        *,
        user_id: int | None = None,
        group_id: int | None = None,
        message: str | None = None,
    ):
        self.name = name
        self.action = action
        self.user_id = user_id
        self.group_id = group_id
        self.message = message

        if self.action == Action.SEND_GROUP_MSG and self.group_id is None:
            raise ValueError("Action 'SEND_GROUP_MESSAGE' requires a 'group_id'.")
        if self.action == Action.SEND_PRIVATE_MSG and self.user_id is None:
            raise ValueError("Action 'SEND_PRIVATE_MESSAGE' requires a 'user_id'.")

    def to_dict(self):
        data = {
            "name": self.name,
            "action": self.action.value,
            "message": self.message,
        }
        if self.action == Action.SEND_GROUP_MSG:
            data["group_id"] = self.group_id
        elif self.action == Action.SEND_PRIVATE_MSG:
            data["user_id"] = self.user_id

        return {k: v for k, v in data.items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict) -> "Signal":
        """
        从字典安全地创建一个 Signal 实例
        """
        try:
            data_copy = data.copy()

            name = data_copy.pop("name")
            action_value = data_copy.pop("action")
            action = Action(action_value)
            return cls(name=name, action=action, **data_copy)

        except KeyError as e:
            raise ValueError(f"字典中缺少必要的键: {e}") from e
        except ValueError as e:
            raise ValueError(f"字典中的 'action' 值无效: {e}") from e
        except TypeError as e:
            raise TypeError(f"创建 Signal 失败，参数类型错误: {e}") from e


async def register_signal(signal: Signal):
    """注册一个信号"""
    async with aiofiles.open(SIGNAL_PATH, "w", encoding="utf-8") as f:
        await f.write(json.dumps(signal.to_dict(), ensure_ascii=False))


from nonebot import get_driver

driver = get_driver()


@driver.on_bot_connect
async def trigger_signal(bot: Bot):
    """触发信号文件"""
    if not SIGNAL_PATH.is_file():
        return
    async with aiofiles.open(SIGNAL_PATH, "r", encoding="utf-8") as f:
        data = json.loads(await f.read())
    signal = Signal.from_dict(data)
    if signal.action == Action.SEND_PRIVATE_MSG:
        await bot.send_private_msg(user_id=signal.user_id, message=signal.message)
    elif signal.action == Action.SEND_GROUP_MSG:
        await bot.send_group_msg(group_id=signal.group_id, message=signal.message)
    # 触发后删除
    SIGNAL_PATH.unlink()
