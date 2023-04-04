# -*- coding: utf-8 -*-
# @Author  : 子龙君
# @Email   :  1435608435@qq.com
# @Github  : neet姬辉夜大人
# @Software: PyCharm
from nonebot.adapters.onebot.v11 import NetworkError, ActionFailed, Bot, MessageEvent

from .sky.daily_tasks.international import SkyDaily as Task_in
from .sky.daily_tasks.national import SkyDaily as Task_cn
from .sky.travelling_spirit.international import get_data
from .tools.menu import get_menu
from .sky.public_notice import get_sky_notice
from .sky.queue import get_state
from .sky.travelling_spirit.national import Travelling as Travelling_cn
from .utils_.chain_reply import chain_reply
from .utils_.data_pack import *
from .config.msg_forward import *
from .tools.scheduler import *
from .utils_.notice_board import *
from .utils_.check_update import *
from .sky.query_tools import *
from .config.command import *
from .utils_ import send_forward_msg
import datetime

Menu = on_command("Sky", aliases=get_cmd_alias("sky_menu"))
DailyCN = on_command("sky -cn", aliases=get_cmd_alias("sky_cn"))
DailyIN = on_command("sky -in", aliases=get_cmd_alias("sky_in"))
TravellingCN = on_command("travel -cn", aliases=get_cmd_alias("travel_cn"))
TravellingIN = on_command("travel -in", aliases=get_cmd_alias("travel_in"))
RemainCN = on_command("remain -cn", aliases=get_cmd_alias("remain_cn"))
RemainIN = on_command("remain -in", aliases=get_cmd_alias("remain_in"))
Queue = on_command("queue", aliases=get_cmd_alias("sky_queue"))
Notice = on_command("notice", aliases=get_cmd_alias("sky_notice"))


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
    try:
        travelling = Travelling_cn()
        results = await travelling.get_data()
        await TravellingCN.send(results)
    except (NetworkError, ActionFailed):
        logger.error('网络环境较差，调用发送信息接口超时')
        await TravellingCN.send(
            message='网络环境较差，调用发送信息接口超时'
        )


@TravellingIN.handle()
async def travel_in():
    try:
        results = await get_data()
        await TravellingIN.send(results)
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
    results = remain("追忆季", 2023, 4, 20, 00, 00, 00)
    await RemainIN.send(results)


@RemainIN.handle()
async def remain_in():
    results = remain("缅怀季", 2023, 4, 3, 15, 00, 00)
    await RemainIN.send(results)
