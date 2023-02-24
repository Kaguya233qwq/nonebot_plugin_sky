# -*- coding: utf-8 -*-
# @Author  : 子龙君
# @Email   :  1435608435@qq.com
# @Github  : neet姬辉夜大人
# @Software: PyCharm

from nonebot.adapters.onebot.v11 import NetworkError, ActionFailed, Bot, GroupMessageEvent
import datetime

from .sky.international import SkyDaily as IN
from .sky.national import SkyDaily as CN
from .tools.in_travelling_spirit import get_data
from .tools.menu import get_menu
from .tools.public_notice import get_notice
from .tools.queue import get_state
from .tools.travelling_spirit import Travelling as travel_CN
from .utils_.chain_reply import chain_reply
from .utils_.data_pack import *
from .config.msg_forward import *
from .tools.scheduler import *
from .utils_.notice_board import *
from .utils_.check_update import *
from .sky.query_tools import *

Menu = on_command("sky", aliases={"光遇菜单"})
DailyYori = on_command("sky -cn", aliases={"今日国服", "国服今日任务", "今日任务"})
DailyHaru = on_command("sky -in", aliases={"今日国际服", "今日国际服任务"})
Queue = on_command("queue", aliases={"排队"})
Notice = on_command("notice", aliases={"公告"})
TravellingCN = on_command("travel -cn", aliases={"国服复刻"})
TravellingIN = on_command("travel -in", aliases={"国际服复刻"})
RemainCN = on_command("remain -cn", aliases={"国服季节剩余"})


@DailyYori.handle()
async def daily_yori(bot: Bot, event: GroupMessageEvent):
    try:
        sky = CN()
        results = await sky.get_data()
        if is_forward():
            chain = await chain_reply(bot, results)
            await bot.send_group_forward_msg(
                group_id=event.group_id,
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
async def daily_haru(bot: Bot, event: GroupMessageEvent):
    try:
        sky = IN()
        results = await sky.get_data()
        if is_forward():
            chain = await chain_reply(bot, results)
            await bot.send_group_forward_msg(
                group_id=event.group_id,
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
async def notice(bot: Bot, event: GroupMessageEvent):
    try:
        notice_ = await get_notice()
        if is_forward():
            chain = await chain_reply(bot, notice_)
            await bot.send_group_forward_msg(
                group_id=event.group_id,
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
async def travel_cn(bot: Bot, event: GroupMessageEvent):
    try:
        travelling = travel_CN()
        results = await travelling.get_data()
        if is_forward():
            chain = await chain_reply(bot, results)
            await bot.send_group_forward_msg(
                group_id=event.group_id,
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
async def travel_in(bot: Bot, event: GroupMessageEvent):
    try:
        results = await get_data()
        if is_forward():
            chain = await chain_reply(bot, results)
            await bot.send_group_forward_msg(
                group_id=event.group_id,
                messages=chain
            )
        else:
            await TravellingIN.send(results)
    except (NetworkError, ActionFailed):
        logger.error('网络环境较差，调用发送信息接口超时')
        await TravellingIN.send(
            message='网络环境较差，调用发送信息接口超时'
        )


# @Author  : ZQDesigned
# @Email   :  2990918167@qq.com
# @Github  : ZQDesigned
# @Software: IDEA Ultimate 2022.3.1
@RemainCN.handle()
async def remain_cn():
    # 定义剩余时间
    deadline = datetime.datetime(2023, 4, 3, 15, 00, 00)
    # 获取当前时间
    now = datetime.datetime.now()
    # 判断当前时间是否大于截止时间
    if now > deadline:
        await RemainCN.send(
            message='季节已经过去了，下一个季节还有一段时间呢'
        )
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
        await RemainCN.send(
            message=f'距离追忆季结束还有{days}天{hours}小时{minutes}分钟{seconds}秒'
        )
