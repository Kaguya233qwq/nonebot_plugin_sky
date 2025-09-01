import asyncio
import os
from nonebot import logger


async def restart_handle(matcher):
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

        # 1. 获取当前正在运行的事件循环
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            logger.error("无法获取事件循环，将强制退出。")
            os._exit(0)
            return
        loop.call_later(0, _do_exit, 0)

    await matcher.send("正在重启插件...")
    await trigger_restart()
