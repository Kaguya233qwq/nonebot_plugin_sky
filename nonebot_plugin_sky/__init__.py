# -*- coding: utf-8 -*-
# @Author  : 子龙君
# @Email   :  1435608435@qq.com
# @Github  : neet姬辉夜大人
# @Software: PyCharm
from nonebot.adapters.onebot.v11 import NetworkError, ActionFailed, Bot, MessageEvent

from .sky.international import SkyDaily as Task_in
from .sky.national import SkyDaily as Task_cn
from .tools.in_travelling_spirit import get_data
from .tools.menu import get_menu
from .tools.public_notice import get_notice
from .tools.queue import get_state
from .tools.travelling_spirit import Travelling as Travelling_cn
from .utils_.chain_reply import chain_reply
from .utils_.data_pack import *
from .config.msg_forward import *
from .tools.scheduler import *
from .utils_.notice_board import *
from .utils_.check_update import *
from .sky.query_tools import *
from .config.command import *
import re
import datetime

initialize()  # 初始化全局命令

Menu = on_command("Sky", aliases=get_cmd_alias("menu"))
DailyYori = on_command("sky -cn", aliases=get_cmd_alias("sky_cn"))
DailyHaru = on_command("sky -in", aliases=get_cmd_alias("sky_in"))
Queue = on_command("queue", aliases=get_cmd_alias("queue"))
Notice = on_command("notice", aliases=get_cmd_alias("notice"))
TravellingCN = on_command("travel -cn", aliases=get_cmd_alias("travel_cn"))
TravellingIN = on_command("travel -in", aliases=get_cmd_alias("travel_in"))
RemainCN = on_command("remain -cn", aliases=get_cmd_alias("remain_cn"))
RemainIN = on_command("remain -in", aliases=get_cmd_alias("remain_in"))


@DailyYori.handle()
async def daily_yori(bot: Bot, event: MessageEvent):
    try:
        sky = Task_cn()
        results = await sky.get_data()
        if is_forward():
            chain = await chain_reply(bot, results)
            msg_type = event.message_type
            if msg_type == 'group':
                group_id = re.findall('_(\d{5,})_', event.get_session_id())[0]
                await bot.send_group_forward_msg(
                    group_id=group_id,
                    messages=chain
                )
            elif msg_type == 'private':
                await bot.send_private_forward_msg(
                    user_id=event.get_session_id(),
                    messages=chain
                )
        else:
            await DailyYori.send(results)

    except (NetworkError, ActionFailed):
        logger.error('网络环境较差，调用发送信息接口超时')
        await DailyYori.send(
            message='网络环境较差，调用发送信息接口超时'
        )


@DailyHaru.handle()
async def daily_haru(bot: Bot, event: MessageEvent):
    try:
        sky = Task_in()
        results = await sky.get_data()
        if is_forward():
            chain = await chain_reply(bot, results)
            msg_type = event.message_type
            if msg_type == 'group':
                group_id = re.findall('_(\d{5,})_', event.get_session_id())[0]
                await bot.send_group_forward_msg(
                    group_id=group_id,
                    messages=chain
                )
            elif msg_type == 'private':
                await bot.send_private_forward_msg(
                    user_id=event.get_session_id(),
                    messages=chain
                )
        else:
            await DailyHaru.send(results)

    except (NetworkError, ActionFailed):
        logger.error('网络环境较差，调用发送信息接口超时')
        await DailyHaru.send(
            message='网络环境较差，调用发送信息接口超时'
        )


@Queue.handle()
async def queue():
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
async def menu():
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
async def notice(bot: Bot, event: MessageEvent):
    try:
        notice_ = await get_notice()
        if is_forward():
            chain = await chain_reply(bot, notice_)
            msg_type = event.message_type
            if msg_type == 'group':
                group_id = re.findall('_(\d{5,})_', event.get_session_id())[0]
                await bot.send_group_forward_msg(
                    group_id=group_id,
                    messages=chain
                )
            elif msg_type == 'private':
                await bot.send_private_forward_msg(
                    user_id=event.get_session_id(),
                    messages=chain
                )
        else:
            await Notice.send(notice_)

    except NetworkError:
        logger.error('NetworkError: 网络环境较差，调用发送信息接口超时')
        await Notice.send(
            message='网络环境较差，调用发送信息接口超时'
        )


@TravellingCN.handle()
async def travel_cn(bot: Bot, event: MessageEvent):
    try:
        travelling = Travelling_cn()
        results = await travelling.get_data()
        if is_forward():
            chain = await chain_reply(bot, results)
            msg_type = event.message_type
            if msg_type == 'group':
                group_id = re.findall('_(\d{5,})_', event.get_session_id())[0]
                await bot.send_group_forward_msg(
                    group_id=group_id,
                    messages=chain
                )
            elif msg_type == 'private':
                await bot.send_private_forward_msg(
                    user_id=event.get_session_id(),
                    messages=chain
                )
        else:
            await TravellingCN.send(results)
    except (NetworkError, ActionFailed):
        logger.error('网络环境较差，调用发送信息接口超时')
        await TravellingCN.send(
            message='网络环境较差，调用发送信息接口超时'
        )


@TravellingIN.handle()
async def travel_in(bot: Bot, event: MessageEvent):
    try:
        results = await get_data()
        if is_forward():
            chain = await chain_reply(bot, results)
            msg_type = event.message_type
            if msg_type == 'group':
                group_id = re.findall('_(\d{5,})_', event.get_session_id())[0]
                await bot.send_group_forward_msg(
                    group_id=group_id,
                    messages=chain
                )
            elif msg_type == 'private':
                await bot.send_private_forward_msg(
                    user_id=event.get_session_id(),
                    messages=chain
                )
        else:
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


# @Author  : ZQDesigned
# @Email   :  2990918167@qq.com
# @Github  : ZQDesigned
# @Software: IDEA Ultimate 2022.3.1
@RemainCN.handle()
async def remain_cn():
    results = remain("追忆季", 2023, 4, 20, 00, 00, 00)
    await RemainIN.send(results)


@RemainIN.handle()
async def remain_in():
    results = remain("缅怀季", 2023, 4, 3, 15, 00, 00)
    await RemainIN.send(results)
