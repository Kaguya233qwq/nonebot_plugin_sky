# -*- coding: utf-8 -*-
# @Author  : 子龙君
# @Email   :  1435608435@qq.com
# @Github    : neet姬辉夜大人
# @Software: PyCharm

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import NetworkError as networkError

from nonebot_plugin_sky.sky.national import SkyDaily as CN
from nonebot_plugin_sky.sky.international import SkyDaily as IN
from nonebot_plugin_sky.utils_.chain_reply import chain_reply
from nonebot_plugin_sky.tools.queue import get_state
from nonebot_plugin_sky.tools.menu import get_menu

Menu = on_command("sky", aliases={"光遇"})
DailyYoli = on_command("sky -cn", aliases={"今日国服"})
DailyHaru = on_command("sky -in", aliases={"今日国际服"})
Queue = on_command("queue",aliases={"排队"})


@DailyYoli.handle()
async def yoli(bot: Bot, event: GroupMessageEvent):
    try:
        sky = CN()
        results = await sky.get_data()
        chain = await chain_reply(bot, results)
        await bot.send_group_forward_msg(
            group_id=event.group_id,
            messages=chain
        )

    except networkError:
        logger.error('NetworkError: 网络环境较差，调用发送信息接口超时')
        await DailyYoli.send(
            message='网络环境较差，调用发送信息接口超时'
        )

@DailyHaru.handle()
async def haru(bot: Bot, event: GroupMessageEvent):
    try:
        sky = IN()
        results = await sky.get_data()
        chain = await chain_reply(bot, results)
        await bot.send_group_forward_msg(
            group_id=event.group_id,
            messages=chain
        )

    except networkError:
        logger.error('NetworkError: 网络环境较差，调用发送信息接口超时')
        await DailyHaru.send(
            message='网络环境较差，调用发送信息接口超时'
        )

@Queue.handle()
async def queue(bot: Bot, event: GroupMessageEvent):
    try:
        state = await get_state()
        await bot.send(
            event = event,
            message=state
        )

    except networkError:
        logger.error('NetworkError: 网络环境较差，调用发送信息接口超时')
        await DailyHaru.send(
            message='网络环境较差，调用发送信息接口超时'
        )

@Menu.handle()
async def queue(bot: Bot, event: GroupMessageEvent):
    try:
        menu = await get_menu()
        await bot.send(
            event = event,
            message=menu
        )

    except networkError:
        logger.error('NetworkError: 网络环境较差，调用发送信息接口超时')
        await DailyHaru.send(
            message='网络环境较差，调用发送信息接口超时'
        )