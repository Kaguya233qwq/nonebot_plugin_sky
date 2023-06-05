# -*- coding: utf-8 -*-
# @Author  : 子龙君
# @Email   :  1435608435@qq.com
# @Github  : neet姬辉夜大人
# @Software: PyCharm
import asyncio
import datetime

from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import NetworkError, ActionFailed, Bot, MessageEvent
from nonebot.permission import SUPERUSER

from .config.command import *
from .config.msg_forward import *
from .sky.daily_tasks.international import SkyDaily as Task_in
from .sky.daily_tasks.national import SkyDaily as Task_cn
from .sky.public_notice import get_sky_notice
from .sky.queue import get_state
from .sky.travelling_spirit.international import get_data
from .sky.travelling_spirit.national import Travelling as Travelling_cn
from .tools.menu import get_menu
from .tools.scheduler import *
from .utils_.bot_loader import Config
from .utils_ import send_forward_msg, clear_cache
from .utils_.chain_reply import chain_reply
from .utils_.check_update import *
from .utils_.data_pack import *
from .utils_.notice_board import *
from .config.travelling_cache import *
from .utils_.travel_cycle import is_exist, NormalTravel, bot_tips

Menu = on_command("Sky", aliases=get_cmd_alias("sky_menu"))
DailyCN = on_command("sky -cn", aliases=get_cmd_alias("sky_cn"))
DailyIN = on_command("sky -in", aliases=get_cmd_alias("sky_in"))
TravellingCN = on_command("travel -cn", aliases=get_cmd_alias("travel_cn"))
TravellingIN = on_command("travel -in", aliases=get_cmd_alias("travel_in"))
RemainCN = on_command("remain -cn", aliases=get_cmd_alias("remain_cn"))
RemainIN = on_command("remain -in", aliases=get_cmd_alias("remain_in"))
Queue = on_command("queue", aliases=get_cmd_alias("sky_queue"))
Notice = on_command("notice", aliases=get_cmd_alias("sky_notice"))
Clear = on_command("sky_clear_cache", aliases=get_cmd_alias("sky_clear_cache"), permission=SUPERUSER)


@DailyCN.handle()
async def daily_cn(bot: Bot, event: MessageEvent):
    try:
        sky = Task_cn()
        results = await sky.get_data()
        if is_forward():
            await send_forward_msg(bot, event, results)
        else:
            await DailyCN.send(results)

    except (NetworkError, ActionFailed):
        logger.error('网络环境较差，调用发送信息接口超时')
        await DailyCN.send(
            message='网络环境较差，调用发送信息接口超时'
        )


@DailyIN.handle()
async def daily_in(bot: Bot, event: MessageEvent):
    try:
        sky = Task_in()
        results = await sky.get_data()
        if is_forward():
            await send_forward_msg(bot, event, results)
        else:
            await DailyIN.send(results)

    except (NetworkError, ActionFailed):
        logger.error('网络环境较差，调用发送信息接口超时')
        await DailyIN.send(
            message='网络环境较差，调用发送信息接口超时'
        )


@Queue.handle()
async def queue_handle():
    try:
        state = await get_state()
        await Queue.send(
            message=state
        )

    except NetworkError:
        logger.error('NetworkError: 网络环境较差，调用发送信息接口超时')
        await Queue.send(
            message='网络环境较差，调用发送信息接口超时'
        )


@Menu.handle()
async def menu_handle():
    try:
        menu_ = await get_menu()
        await Menu.send(
            message=menu_
        )

    except NetworkError:
        logger.error('NetworkError: 网络环境较差，调用发送信息接口超时')
        await Menu.send(
            message='网络环境较差，调用发送信息接口超时'
        )


@Notice.handle()
async def notice_handle(bot: Bot, event: MessageEvent):
    try:
        notice_ = await get_sky_notice()
        if is_forward():
            await send_forward_msg(bot, event, notice_)
        else:
            await Notice.send(notice_)

    except NetworkError:
        logger.error('NetworkError: 网络环境较差，调用发送信息接口超时')
        await Notice.send(
            message='网络环境较差，调用发送信息接口超时'
        )


@TravellingCN.handle()
async def travel_cn():
    travel = NormalTravel()
    try:

        status = travel.national()
        tips = bot_tips(status)
        if status.get('status') is True:
            # 如果在复刻期间内就判断有无缓存
            release_time = status.get('current_release').replace(' 12:00:00', '')
            cache = is_exist(release_time)
            if cache:
                # 如果有复刻缓存则发送缓存
                await TravellingCN.send(MessageSegment.image(cache))
            else:
                # 没有就执行实时调用
                travelling = Travelling_cn()
                img_url = await travelling.get_data()
                if img_url:
                    cache = is_exist(release_time)
                    if cache:
                        await TravellingCN.send(MessageSegment.image(cache))
                    else:
                        await TravellingCN.send('发送图片缓存失败！请联系开发者解决')
                else:
                    await TravellingCN.send('没有找到国服复刻先祖的数据')
        else:
            # 如果不在复刻期间，则发送提示信息
            await TravellingCN.send(
                f'当前无复刻先祖信息，下次复刻公布时间：\n{status.get("next_release")}'
            )
        await asyncio.sleep(2)
        await TravellingCN.send(tips)
    except (NetworkError, ActionFailed):
        logger.error('网络环境较差，调用发送信息接口超时')
        await TravellingCN.send(
            message='网络环境较差，调用发送信息接口超时'
        )


@TravellingIN.handle()
async def travel_in():
    try:
        # 实时调用
        results = await get_data()
        if results:
            await TravellingIN.send(results)
        else:
            await TravellingIN.send('未获取到国际服复刻先祖信息（维护中）')
    except (NetworkError, ActionFailed):
        logger.error('网络环境较差，调用发送信息接口超时')
        await TravellingIN.send(
            message='网络环境较差，调用发送信息接口超时'
        )


def remain(
        season_name: str,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        second: int
) -> str:
    """
    通用季节倒计时
    """

    # @Author  : ZQDesigned
    # @Email   :  2990918167@qq.com
    # @Github  : ZQDesigned
    # @Software: IDEA Ultimate 2022.3.1

    # 定义剩余时间
    deadline = datetime.datetime(
        year, month, day, hour, minute, second
    )
    # 获取当前时间
    now = datetime.datetime.now()
    # 判断当前时间是否大于截止时间
    if now > deadline:
        return '季节已经过去了，下一个季节还有一段时间呢'
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
        return f'距离{season_name}结束还有{days}天{hours}小时{minutes}分钟{seconds}秒'


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
    # 包含f或者force则忽略上次清理时间间隔，直接清除
    # 传入http方式参数 day=30&force
    plain_text = args.extract_plain_text().strip()
    day = 30
    f = False
    if plain_text:
        try:
            plain_text = plain_text.lower()
            arg_list = plain_text.split('&')
            for arg in arg_list:
                if arg.startswith('day='):
                    day = int(arg.strip()[4:])
                elif arg == 'f' or arg == 'force':
                    f = True
        except Exception as exp:
            logger.error(plain_text, Exception=exp)
            await Clear.finish("参数解析错误")
            return
    if f:
        msg = f'开始强制清理前{day}天数据'
    else:
        msg = f'开始清理前{day}天数据'
    await Clear.send(msg)
    num = clear_cache(day, f)
    await Clear.finish(f"清理前{day}天缓存数据,共{num}条完成")


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
    type='application',
    extra={
        "author": "Kaguya姬辉夜",
        "qq": "1435608435",
        "version": "2.2.10"
    }
)
