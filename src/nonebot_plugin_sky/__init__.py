# -*- coding: utf-8 -*-
# @Author  : 辉夜sama
# @Email   :  marisa_qwq@qq.com
# @Github  : https://github.com/Kaguya233qwq
import datetime

from nonebot import logger, on_command
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Message,
)
from nonebot.permission import SUPERUSER

from .config.command import get_cmd_alias

from .utils.bot_loader import Config
from .utils import clear_cache
from .tools.update import __version__
from .handler import Handler
from .tools import register_all_handlers

RemainCN = on_command("remain -cn", aliases=get_cmd_alias("remain_cn"))
RemainIN = on_command("remain -in", aliases=get_cmd_alias("remain_in"))
Clear = on_command(
    "sky_clear_cache", aliases=get_cmd_alias("sky_clear_cache"), permission=SUPERUSER
)


# 注册tools中的所有消息处理器
register_all_handlers()

# 国服每日任务
on_command(
    "sky -cn",
    aliases=get_cmd_alias("sky_cn"),
    handlers=[Handler.chinese_server_daily_handler],
)

# 国际服每日任务
on_command(
    "sky -in",
    aliases=get_cmd_alias("sky_in"),
    handlers=[Handler.international_server_daily_handler],
)

# 国服旅行先祖
on_command(
    "tss -cn",
    aliases=get_cmd_alias("travel_cn"),
    handlers=[Handler.chinese_server_travelling_spirit_handler],
)

# 游戏公告
on_command(
    "notice",
    aliases=get_cmd_alias("sky_notice"),
    handlers=[Handler.get_public_notice_handler],
)

# 排队
on_command(
    "queue",
    aliases=get_cmd_alias("sky_queue"),
    handlers=[Handler.get_queue_state_handler],
)

# 菜单
on_command("Sky", aliases=get_cmd_alias("sky_menu"), handlers=[Handler.menu_handler])


def remain(
    season_name: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
) -> str:
    """
    通用季节倒计时
    """

    # @Author  : ZQDesigned
    # @Email   :  2990918167@qq.com
    # @Github  : ZQDesigned
    # @Software: IDEA Ultimate 2022.3.1

    # 定义剩余时间
    deadline = datetime.datetime(year, month, day, hour, minute, second)
    # 获取当前时间
    now = datetime.datetime.now()
    # 判断当前时间是否大于截止时间
    if now > deadline:
        return "季节已经过去了，下一个季节还有一段时间呢"
    else:
        # 计算剩余时间
        remain_time = deadline - now
        # 获取天数
        days = remain_time.days
        # 获取小时
        hours = remain_time.seconds // 3600
        # 获取分钟
        minutes = remain_time.seconds % 3600 // 60
        # 获取秒
        seconds = remain_time.seconds % 3600 % 60
        # 发送剩余时间
        return f"距离{season_name}结束还有{days}天{hours}小时{minutes}分钟{seconds}秒"


@RemainCN.handle()
async def remain_cn():
    results = remain("夜行季国服", 2023, 7, 19, 00, 00, 00)
    await RemainIN.send(results)


@RemainIN.handle()
async def remain_in():
    results = remain("夜行季国际服", 2023, 6, 25, 15, 00, 00)
    await RemainIN.send(results)


@Clear.handle()
async def _(args: Message = CommandArg()):
    """
    清理缓存

    - 指令名: 清理缓存
    - 可用参数:
        - day: 指定清理缓存时间段x天前，默认为30
        - f: 忽略上次清理时间间隔，强制执行清理
    - 传参方式：http params形式
        - 示例：day=30&force
    """
    plain_text = args.extract_plain_text().strip()
    day = 30
    f = False
    if plain_text:
        try:
            plain_text = plain_text.lower()
            arg_list = plain_text.split("&")
            for arg in arg_list:
                if arg.startswith("day="):
                    day = int(arg.strip()[4:])
                elif arg == "f" or arg == "force":
                    f = True
        except Exception as exp:
            logger.error(plain_text, Exception=exp)
            await Clear.finish("参数解析错误")
            return
    if f:
        msg = f"开始强制清理{day}天前的数据"
    else:
        msg = f"开始清理{day}天前的数据"
    await Clear.send(msg)
    num = clear_cache(day, f)
    await Clear.finish(f"清理{day}天前的缓存数据,共{num}条完成")


# nonebot的插件元数据标准
__plugin_meta__ = PluginMetadata(
    name="Sky光遇",
    description="光遇的每日任务及活动相关查询插件",
    usage="""
基本命令：
光遇菜单 -> 查看插件菜单图
今日国服 -> 查看今日国服任务
今日国际服 -> 查看今日国际服任务
国服复刻 -> 查询国服复刻先祖信息
国际服复刻 -> 查询国际服复刻先祖信息
    
数据包命令：
安装数据包 -> 从gitee拉取可用的静态攻略资源包
菜单v2 -> 查看所有数据包命令
[命令起始符]-[命令] -> 执行数据包命令
    """,
    config=Config,
    type="application",
    extra={"author": "Kaguya姬辉夜", "version": __version__},
    homepage="https://github.com/Kaguya233qwq/nonebot_plugin_sky",
    supported_adapters={"~onebot.v11"},
)
