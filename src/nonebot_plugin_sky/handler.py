import asyncio
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    NetworkError,
    ActionFailed,
    MessageSegment,
)
from nonebot import logger
from nonebot.matcher import Matcher

from .config.msg_forward import is_forward
from .config import Config
from .utils import send_forward_msg
from .sky import Sky


class Handler:
    @staticmethod
    async def chinese_server_daily_handler(event: MessageEvent, bot: Bot):
        """国服每日任务的handler"""
        try:
            text, images = await Sky.get_chinese_server_daily()
            messages = [MessageSegment.text(text)]
            for image in images:
                messages.append(MessageSegment.image(image))
            if is_forward():
                await send_forward_msg(bot, event, messages)
            else:
                message = MessageSegment.text(text)
                for image in images:
                    message += MessageSegment.image(image)
                await bot.send(event, message)

        except (NetworkError, ActionFailed):
            logger.error("网络环境较差，调用发送信息接口超时")
            await bot.send(event, message="网络环境较差，调用发送信息接口超时")

    @staticmethod
    async def international_server_daily_handler(event: MessageEvent, bot: Bot):
        """国际服每日任务的handler"""
        try:
            text, images = await Sky.get_international_server_daily()
            messages = [MessageSegment.text(text)]
            for image in images:
                messages.append(MessageSegment.image(image))
            if is_forward():
                await send_forward_msg(bot, event, messages)
            else:
                message = MessageSegment.text(text)
                for image in images:
                    message += MessageSegment.image(image)
                await bot.send(event, message)

        except (NetworkError, ActionFailed):
            logger.error("网络环境较差，调用发送信息接口超时")
            await bot.send(event, message="网络环境较差，调用发送信息接口超时")

    @staticmethod
    async def chinese_server_travelling_spirit_handler(matcher: Matcher):
        """获取国服旅行先祖的Handler"""
        try:
            text, images, tips = await Sky.get_chinese_server_travelling_spirit()
            if images:
                await matcher.send(message=MessageSegment.image(images[0]))
            else:
                # 只发提示语
                await matcher.send(message=MessageSegment.text(text))
            await asyncio.sleep(2)
            if tips is not None:
                await matcher.send(message=tips)
        except (NetworkError, ActionFailed):
            logger.error("网络环境较差，调用发送信息接口超时")
            await matcher.send(message="网络环境较差，调用发送信息接口超时")

    @staticmethod
    async def get_public_notice_handler(bot: Bot, event: MessageEvent):
        """获取官方公告的handler"""
        try:
            notice = await Sky.get_sky_notice()
            if is_forward():
                await send_forward_msg(bot, event, [notice])
            else:
                await bot.send(event, notice)

        except NetworkError:
            logger.error("NetworkError: 网络环境较差，调用发送信息接口超时")
            await bot.send(event, message="网络环境较差，调用发送信息接口超时")

    @staticmethod
    async def get_queue_state_handler(matcher: Matcher):
        """服务器排队状态的handler"""
        try:
            state = await Sky.get_queue_state()
            await matcher.send(message=state)

        except NetworkError:
            logger.error("NetworkError: 网络环境较差，调用发送信息接口超时")
            await matcher.send(message="网络环境较差，调用发送信息接口超时")

    @staticmethod
    async def menu_handler(matcher: Matcher):
        """获取菜单的Handler"""

        def get_menu_image_path() -> str:
            path = Config.RESOURCE_PATH / "menu.png"
            return path.absolute().as_uri()

        try:
            menu = get_menu_image_path()
            await matcher.send(message=MessageSegment.image(menu))

        except NetworkError:
            logger.error("NetworkError: 网络环境较差，调用发送信息接口超时")
            await matcher.send(message="网络环境较差，调用发送信息接口超时")
