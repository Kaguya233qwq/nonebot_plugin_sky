from nonebot import on_command

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
    from .restart import restart_handle
    from . import data_pack as data_pack

    on_command("check", aliases=get_cmd_alias("check"), handlers=[check_handle])
    on_command("upgrade", aliases=get_cmd_alias("upgrade"), handlers=[upgrade_handle])
    on_command("restart", aliases={"重启"}, handlers=[restart_handle])
