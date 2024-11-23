import os
import random

from nonebot import require, on_command, logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

from ..utils_.bot_loader import Config, get_the_bot
from ..config.command import get_cmd_alias
from ..config.helper_at_all import *

LunchScheduler = on_command("lunch_helper", aliases=get_cmd_alias('干饭小助手'))

@LunchScheduler.handle()
async def scheduler_handler(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    try:
        if plain_text in ["start","启动"]:
            if not scheduler.get_job("task_lunch"):
                # 设定提前五分钟提醒
                # 国服雨林干饭时间：整点的8,10,12,16,18,20
                scheduler.add_job(
                    _task_lunch,
                    "cron",
                    hour="7,9,11,15,17,19",
                    minute="55",
                    id="task_lunch"
                )
                await matcher.send('已启动雨林干饭小助手')
            else:
                await matcher.send('雨林干饭小助手已经在运行中啦！')
        elif plain_text in ["status","状态","运行状态"]:
            if scheduler.state == 1:
                await matcher.send('当前运行状态：干饭小助手服务运行中')
            if scheduler.state == 0:
                await matcher.send('当前运行状态：干饭小助手服务未启动')

        elif plain_text in ["stop","关闭","停止"]:
            if scheduler.get_job("task_lunch"):
                # 移除定时任务
                scheduler.remove_job("task_lunch")
                await matcher.send('已关闭雨林干饭小助手')
            else:
                await matcher.send('雨林干饭小助手未运行哦~')

        elif plain_text in ['test','测试']:
            results = await _have_a_lunch()
            await matcher.send("[testing mode]\n" + results)
        else:
            await matcher.send('指令参数错误，用法：lunch_helper [start|status|stop|test]')
    except Exception as error:
        await matcher.send('发生错误：%s' % error)
        
async def _task_lunch():
    """
    干饭任务
    """
    results = await _have_a_lunch()
    if isinstance(Config.RECV_GROUP_ID, list):
        # 向所有群组发送消息
        bot = await get_the_bot()
        for group_id in Config.RECV_GROUP_ID:
            await bot.send_group_msg(
                group_id=group_id,
                message=results
            )
    else:
        logger.error('群id配置错误，请检查您的配置')

async def _have_a_lunch():
    """
    干饭函数主体
    """
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
        results = text + MessageSegment.image('file:///' + path + file) + MessageSegment.at("all")
    else:
        results = text + MessageSegment.image('file:///' + path + file)
    return results