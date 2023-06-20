import os
import random

from nonebot import require, on_command, logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

from ..utils_.bot_loader import CONFIG, connect
from ..config.command import get_cmd_alias
from ..config.helper_at_all import *

Scheduler = on_command("-sc", aliases=get_cmd_alias('helper_name'))


@Scheduler.handle()
async def scheduler_handler(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    is_on = False
    bot = await connect()
    try:
        if '启动' in plain_text:
            is_on = True
            scheduler.start()
            await matcher.send(
                '已启动雨林干饭小助手'
            )
        elif '状态' in plain_text:
            if scheduler.state == 1:
                await matcher.send('当前运行状态：干饭提醒服务运行中')
            if scheduler.state == 0:
                await matcher.send('当前运行状态：干饭提醒服务未启动')

        elif '关闭' in plain_text:
            if scheduler.state:
                scheduler.shutdown()
                await matcher.send('已关闭雨林干饭小助手')

        elif '测试' in plain_text:
            results = await go()
            await matcher.send("【功能测试】\n" + results)
        else:
            await matcher.send('指令关键字错误请重新输入')
    except Exception as error:
        await matcher.send('发生错误：%s' % error)

    if is_on:
        # 设定提前五分钟提醒
        # 国服雨林干饭时间：整点的8,10,12,16,18,20
        @scheduler.scheduled_job("cron",
                                 hour="7,9,11,15,17,19",
                                 minute="55",
                                 id="job_0")
        async def auto_run():
            results_ = await go()

            if isinstance(CONFIG.RECV_GROUP_ID, list):
                for group_id in CONFIG.RECV_GROUP_ID:
                    await bot.send_group_msg(
                        group_id=group_id,
                        message=results_
                    )
            elif isinstance(CONFIG.RECV_GROUP_ID, str):
                await bot.send_group_msg(
                    group_id=CONFIG.RECV_GROUP_ID,
                    message=results_
                )
            else:
                logger.error('群id配置错误，请检查您的配置')

    else:
        pass


async def go():
    texts = [
        '干饭人干饭魂,冲鸭！',
        '还有五分钟就要开饭了哦~快叫上你的朋友一起去叭',
        '让我看看是哪个小可爱干饭不带盆~,'
        '上号！干饭人',
        '干饭不积极思想有问题~今天我要吃三碗饭！',
        '快到饭点了崽崽们，准备准备出发吧~',
        '我是要励志把小陈吃破产的人！'
    ]
    text = random.sample(texts, 1)[0]
    abspath_ = os.path.abspath(__file__).strip('scheduler.py')
    path = abspath_ + 'helper_image/'
    image_list = os.listdir(path)
    file = random.sample(image_list, 1)[0]
    if at_all():
        results = MessageSegment.at(
            "all") + text + MessageSegment.image('file:///' + path + file)
    else:
        results = text + MessageSegment.image('file:///' + path + file)
    return results
