from pathlib import Path

from ..config import Config
from ..config.helper_at_all import at_all
from ..utils.bot_loader import get_the_bot
from nonebot.config import Config as NBConfig
from nonebot.params import CommandArg
from nonebot.internal.matcher import Matcher
from nonebot.adapters.onebot.v11 import Message, MessageSegment
import random
from datetime import datetime, timedelta
from typing import List

from nonebot import require, logger, get_plugin_config

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler  # noqa: E402


class RockfallEvent:
    """
    落石事件返回结构
    """

    def __init__(self, rock_type: str, start_time: List[datetime] | None = None):
        self.rock_type = rock_type
        self.start_time = start_time


async def lunch_helper_handler(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    try:
        if plain_text in ["start", "启动"]:
            if not scheduler.get_job("task_lunch"):
                # 设定提前五分钟提醒
                # 国服雨林干饭时间：整点的8,10,12,16,18,20
                scheduler.add_job(
                    _task_lunch,
                    "cron",
                    hour="7,9,11,15,17,19",
                    minute="55",
                    id="task_lunch",
                )
                await matcher.send("已启动雨林干饭小助手")
            else:
                await matcher.send("雨林干饭小助手已经在运行中啦！")
        elif plain_text in ["status", "状态", "运行状态"]:
            if scheduler.get_job("task_lunch"):
                await matcher.send("干饭小助手服务状态：运行中")
            else:
                await matcher.send("干饭小助手服务状态：未启动")

        elif plain_text in ["stop", "关闭", "停止"]:
            if scheduler.get_job("task_lunch"):
                # 移除定时任务
                scheduler.remove_job("task_lunch")
                await matcher.send("已关闭雨林干饭小助手")
            else:
                await matcher.send("雨林干饭小助手未运行哦~")

        elif plain_text in ["test", "测试"]:
            results = await _have_a_lunch()
            await matcher.send("[testing mode]\n" + results)
        else:
            await matcher.send(
                "指令参数错误，用法：lunch_helper [start|status|stop|test]"
            )
    except Exception as error:
        await matcher.send("发生错误：%s" % error)


async def _task_lunch():
    """
    干饭任务
    """
    results = await _have_a_lunch()
    await _send_msg_to_groups(results)


async def _have_a_lunch() -> Message:
    """
    干饭函数主体
    """
    results = ""
    texts = [
        "干饭人干饭魂,冲鸭！",
        "还有五分钟就要开饭了哦~快叫上你的朋友一起去叭",
        "让我看看是哪个小可爱干饭不带盆~,上号！干饭人",
        "干饭不积极思想有问题~今天我要吃三碗饭！",
        "快到饭点了崽崽们，准备准备出发吧~",
        "我是要励志把小陈吃破产的人！",
    ]
    text = random.choice(texts)
    path = Config.IMAGES_PATH
    image_list: List[Path] = [i for i in path.glob("*")]
    image: Path = path / random.choice(image_list)
    if at_all():
        results = (
            text
            + MessageSegment.image(image.resolve().as_uri())
            + MessageSegment.at("all")
        )
    else:
        results = text + MessageSegment.image(image.resolve().as_uri())
    return results


async def get_rockfall_event_results():
    """
    获取落石事件描述
    """
    event = await _get_rockfall_event(datetime.now())
    rock_type = event.rock_type
    start_time = event.start_time
    if start_time is None:
        return "今日没有落石事件"
    if rock_type == "black":
        results = "今日伊甸落石：黑石\n开始时间：\n"
        for t in start_time:
            results += t.strftime("%H:%M:%S\n")
    elif rock_type == "red":
        results = "今日伊甸落石：红石\n开始时间：\n"
        for t in start_time:
            results += t.strftime("%H:%M:%S\n")
    else:
        results = "今日没有落石事件"
    return results


async def rockfall_handler(matcher: Matcher):
    """今日落石事件handler"""
    results = await get_rockfall_event_results()
    await matcher.send(results.strip("\n"))


async def rockfall_scheduler_handler(matcher: Matcher, args: Message = CommandArg()):
    """落石小助手handler"""
    plain_text = args.extract_plain_text()
    if plain_text in ["start", "启动"]:
        # 添加定时器任务 每晚0点0分1秒自动添加落石提醒的定时任务
        if not scheduler.get_job("rockfall_helper"):
            scheduler.add_job(
                _add_rockfall_task,
                "cron",
                hour="0",
                minute="0",
                second="10",
                id="rockfall_helper",
            )
            await matcher.send("已启动落石提醒小助手")
        else:
            await matcher.send("落石提醒小助手已经在运行中啦~")
    elif plain_text in ["status", "状态", "运行状态"]:
        if scheduler.get_job("rockfall_helper"):
            await matcher.send("落石小助手服务状态：运行中")
        else:
            await matcher.send("落石小助手服务状态：未启动")
    elif plain_text in ["stop", "关闭", "停止"]:
        if scheduler.get_job("rockfall_helper"):
            # 移除定时任务
            scheduler.remove_job("rockfall_helper")
            await matcher.send("已关闭落石提醒小助手")
        else:
            await matcher.send("落石提醒小助手未运行哦~")
    elif plain_text in ["test", "测试"]:
        check_time = datetime.now() + timedelta(seconds=10)
        if not scheduler.get_job("rockfall_helper"):
            scheduler.add_job(
                _add_rockfall_task_test,
                "cron",
                hour=f"{check_time.hour}",
                minute=f"{check_time.minute}",
                second=f"{check_time.second}",
                id="rockfall_helper",
            )
            logger.info("已启动落石提醒小助手[test mode]")
            await matcher.send("[testing mode]\n已启动落石提醒小助手")
        else:
            logger.info("落石提醒小助手已经在运行中啦~[test mode]")
            await matcher.send("落石提醒小助手已经在运行中啦~")
    else:
        await matcher.send(
            "指令参数错误，用法：rockfall_helper [start|status|stop|test]"
        )


async def _add_rockfall_task_test(matcher: Matcher) -> None:
    """test rockfall adding task"""
    # 如果已经注册了定时器任务则先移除
    if scheduler.get_job("task_rockfall"):
        scheduler.remove_job("task_rockfall")
    args = ["[testing mode]\nxx石已落地！伊甸黑暗能量正在影响着主世界，..."]
    check_time = datetime.now() + timedelta(seconds=10)
    scheduler.add_job(
        _send_msg_to_groups,
        "cron",
        hour=f"{check_time.hour}",
        minute=f"{check_time.minute}",
        second=f"{check_time.second}",
        args=args,
        id="task_rockfall",
    )
    # 如果已经注册了定时器任务则先移除
    await matcher.send("[testing mode]\n落石提醒的定时任务注册成功")


async def _add_rockfall_task() -> None:
    """
    添加落石的提醒定时任务 的定时任务
    """
    # 如果已经注册了定时器任务则先移除
    if scheduler.get_job("task_rockfall"):
        scheduler.remove_job("task_rockfall")
    event = await _get_rockfall_event(datetime.now())
    rock_type = event.rock_type
    start_time = event.start_time
    if start_time is None:
        return
    results = await get_rockfall_event_results()
    await _send_msg_to_groups(results.strip("\n"))
    if rock_type == "black":
        args = ["黑石已落地！伊甸黑暗能量正在影响着主世界，清理落石可得白色蜡烛"]
    elif rock_type == "red":
        args = ["红石已落地！伊甸黑暗能量正在影响着主世界，清理落石可得升华蜡烛"]
    else:
        return
    scheduler.add_job(
        _send_msg_to_groups,
        "cron",
        hour=",".join([str(t.hour) for t in start_time]),
        minute="8",
        args=args,
        id="task_rockfall",
    )
    logger.info("落石定时任务已更新")
    await _send_msg_to_groups("已添加各个落石时间点的定时任务")


async def _send_msg_to_groups(msg: Message | str) -> None:
    """
    向所有已配置群组发送消息
    """
    config = get_plugin_config(NBConfig)
    # 向所有群组发送消息
    bot = await get_the_bot()
    for group_id in config.recv_group_id:
        await bot.send_group_msg(group_id=group_id, message=msg)


async def _get_rockfall_event(input_date: datetime) -> RockfallEvent:
    """
    落石事件判定逻辑
    """

    def create_start_times(hours):
        return [
            datetime(
                year=input_date.year,
                month=input_date.month,
                day=input_date.day,
                hour=h,
                minute=8,
                second=0,
            )
            for h in hours
        ]

    if 1 <= input_date.day <= 15:
        if input_date.weekday() == 1:  # 星期二
            return RockfallEvent(
                rock_type="black",
                start_time=create_start_times([8, 14, 19]),
            )
        elif input_date.weekday() == 5:  # 星期六
            return RockfallEvent(
                rock_type="red",
                start_time=create_start_times([10, 14, 22]),
            )
        elif input_date.weekday() == 6:  # 星期日
            return RockfallEvent(
                rock_type="red",
                start_time=create_start_times([7, 13, 19]),
            )
        else:  # 其他时候没有事件
            return RockfallEvent(rock_type="")
    if 16 <= input_date.day <= 31:
        if input_date.weekday() == 2:  # 星期三
            return RockfallEvent(
                rock_type="black",
                start_time=create_start_times([9, 15, 21]),
            )
        elif input_date.weekday() == 4:  # 星期五
            return RockfallEvent(
                rock_type="red",
                start_time=create_start_times([11, 17, 23]),
            )
        elif input_date.weekday() == 6:  # 星期日
            return RockfallEvent(
                rock_type="red",
                start_time=create_start_times([7, 13, 19]),
            )
        else:  # 其他时候没有事件
            return RockfallEvent(rock_type="")
    return RockfallEvent(rock_type="")
