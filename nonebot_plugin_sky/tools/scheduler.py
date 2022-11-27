from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg
from nonebot import require, on_command, logger, get_bot, get_driver

import random
import os

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

Scheduler = on_command("-t", aliases={'小助手'})

try:
    recv_group_id = get_driver().config.recv_group_id
except Exception as e:
    str(e)
    logger.warning('您还未配置接收小助手消息的群id')


@Scheduler.handle()
async def scheduler_handler(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    is_on = False
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
    except Exception as e:
        await matcher.send('发生错误：%s' % e)

    if is_on:
        # 设定提前五分钟提醒
        @scheduler.scheduled_job("cron", hour="7,9,11,15,16,17,19", minute="32,55", id="job_0")
        async def auto_run():
            try:
                bot = get_bot()
            except Exception as p:
                logger.error('您还未启动go-cqhttp | %s' % p)

            group_id = recv_group_id
            results_ = await go()
            await bot.send_group_msg(
                group_id=group_id,
                message=results_
            )

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
    path = abspath_ + 'image\\'
    image_list = os.listdir(path)
    file = random.sample(image_list, 1)[0]
    results = text + MessageSegment.image('file:///' + path + file)
    return results
