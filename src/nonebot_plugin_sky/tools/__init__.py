import asyncio
import os
from nonebot import logger, on_command

from ..config.command import get_cmd_alias


def register_all_handlers():
    """
    注册所有消息处理器
    """
    from .scheduler import (
        lunch_helper_handler,
        rockfall_handler,
        rockfall_scheduler_handler,
    )

    on_command(
        "lunch_helper",
        aliases=get_cmd_alias("lunch_helper"),
        handlers=[lunch_helper_handler],
    )
    on_command(
        "rockfall", aliases=get_cmd_alias("rockfall"), handlers=[rockfall_handler]
    )
    on_command(
        "rockfall_helper",
        aliases=get_cmd_alias("rockfall_helper"),
        handlers=[rockfall_scheduler_handler],
    )

    from .update import check_handle, upgrade_handle

    on_command("check", aliases=get_cmd_alias("check"), handlers=[check_handle])
    on_command("upgrade", aliases=get_cmd_alias("upgrade"), handlers=[upgrade_handle])
    
    async def restart_handle(matcher):
        """
        重启bot框架 需配合外部的守护脚本使用
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
                os._exit()
                return
            loop.call_later(0, _do_exit, 0)

        
        await matcher.send("正在重启插件...")
        await trigger_restart()
    
    on_command("restart",aliases={"重启"},handlers=[restart_handle])
