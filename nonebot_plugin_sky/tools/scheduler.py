from nonebot.adapters.onebot.v11 import Message
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg
from nonebot import require, on_command, logger

import random

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

Scheduler = on_command("-t", aliases={'小助手'})


@Scheduler.handle()
async def scheduler_handler(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    is_on = False
    try:
        if '启动' in plain_text:
            is_on = True
            scheduler.start()
            await matcher.send(
                '已开启雨林干饭小助手'
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
        else:
            await matcher.send('指令关键字错误请重新输入')
    except Exception as e:
        await matcher.send('发生错误：%s' % e)

    if is_on:
        # 设定提前五分钟提醒
        @scheduler.scheduled_job("cron", hour="7,9,11,15,17,19", minute="55", id="job_0")
        async def auto_run():
            texts = [
                '干饭人干饭魂,冲鸭！',
                '还有五分钟就要开饭了哦~快叫上你的朋友一起去叭',
                '让我看看是哪个小可爱干饭不带盆~,'
                '上号！干饭人',
                '干饭不积极思想有问题~今天我要吃三碗饭！',
                '快到饭点了崽崽们，准备准备出发吧~',
                '我是要励志把小陈吃破产的人！'
            ]
            url = 'https://raw.githubusercontent.com/Kaguya233qwq/nonebot_plugin_sky/main/image/'
            images = [
                url+'eating.jpg',
                url+'go.jpg',
                url+'face_braid.gif',
                url+'face_bun.gif',
                url+'face_cat.gif',
                url+'face_fox.gif',
                url+'face_white_cat.gif'
            ]
            image = random.sample(images,1)[0]
            text = random.sample(texts, 1)[0]
            await matcher.send(text+image)

    else:
        pass
