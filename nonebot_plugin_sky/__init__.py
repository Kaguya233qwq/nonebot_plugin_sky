# -*- coding: utf-8 -*-
# @Author  : 子龙君
# @Email   :  1435608435@qq.com
# @Github    : neet姬辉夜大人
# @Software: PyCharm

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import NetworkError, ActionFailed

from nonebot_plugin_sky.sky.national import SkyDaily as CN
from nonebot_plugin_sky.sky.international import SkyDaily as IN
from nonebot_plugin_sky.utils_.chain_reply import chain_reply
from nonebot_plugin_sky.tools.queue import get_state
from nonebot_plugin_sky.tools.menu import get_menu
from nonebot_plugin_sky.tools.public_notice import get_notice

from nonebot_plugin_sky.tools.scheduler import *

Menu = on_command("sky", aliases={"光遇"})
DailyYoli = on_command("sky -cn", aliases={"今日国服"})
DailyHaru = on_command("sky -in", aliases={"今日国际服"})
Queue = on_command("queue", aliases={"排队"})
Notice = on_command("notice", aliases={"公告"})


@DailyYoli.handle()
async def yoli(bot: Bot, event: GroupMessageEvent):
    try:
        sky = CN()
        results = await sky.get_data()
        # chain = await chain_reply(bot, results)
        # await bot.send_group_forward_msg(
        #     group_id=event.group_id,
        #     messages=chain
        # )
        await DailyYoli.send(results)

    except (NetworkError, ActionFailed):
        logger.error('网络环境较差，调用发送信息接口超时')
        await DailyYoli.send(
            message='网络环境较差，调用发送信息接口超时'
        )


@DailyHaru.handle()
async def haru(bot: Bot, event: GroupMessageEvent):
    try:
        sky = IN()
        results = await sky.get_data()
        # chain = await chain_reply(bot, results)
        # await bot.send_group_forward_msg(
        #     group_id=event.group_id,
        #     messages=chain
        # )
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
        chain = await chain_reply(bot, notice_)
        # await bot.send_group_forward_msg(
        #     group_id=event.group_id,
        #     messages=chain
        # )
        await Notice.send(notice_)

    except NetworkError:
        logger.error('NetworkError: 网络环境较差，调用发送信息接口超时')
        await Notice.send(
            message='网络环境较差，调用发送信息接口超时'
        )
