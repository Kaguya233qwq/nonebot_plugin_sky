import json
import os
import re
import time
from typing import Union

import httpx
from nonebot import on_command
from nonebot.adapters.onebot.v11 import PRIVATE_FRIEND, Message, PrivateMessageEvent, Bot, GroupMessageEvent, MessageSegment, \
    MessageEvent
from nonebot.internal.matcher import Matcher
from nonebot.internal.params import ArgPlainText
from nonebot.params import CommandArg

from ..utils_.chain_reply import chain_reply
from ..config.msg_forward import is_forward


async def save_sky_id(qq: str, sky_id: str) -> None:
    """
    保存qq号与对应的sky_id
    """
    if not os.path.isfile('Sky/origin_id'):
        with open("Sky/origin_id", "a") as f:
            f.write(json.dumps({qq: sky_id}))
    else:
        with open("Sky/origin_id", 'r') as f:
            content = f.read()
            if content == "":
                tmp = json.dumps({qq: sky_id})
            else:
                tmp = json.loads(content)
                tmp.update({qq: sky_id})
                tmp = json.dumps(tmp)
        with open("Sky/origin_id", 'w') as f:
            f.write(tmp)


async def load_sky_id(qq: str) -> Union[None, str]:
    """
    根据qq读取绑定的光遇id
    """
    if not os.path.isfile('Sky/origin_id'):
        return None
    with open("Sky/origin_id", 'r') as f:
        content = f.read()
        if content != '' and content is not None:
            tmp = json.loads(content)
        else:
            return None
        return tmp.get(qq, None)


To_Get_Uid = (
        '如何获取uid？见下图：' +
        MessageSegment.image(
            'https://gitee.com/Kaguya233qwq/'
            'nonebot_plugin_sky/raw/main/'
            '.README_images/get_uid.jpg')
)


class Sprite:

    def __init__(self):
        self.api_get_token = 'https://live-gms-sky-merge.game.163.com:9005/gms_cmd'
        self.answer = 'https://ma75.gmsdk.gameyw.netease.com/sprite/answer'
        self.sprite_answer = 'https://ma75.gmsdk.gameyw.netease.com/interface/sprite/answerKms'
        self.message_get = 'https://ma75.gmsdk.gameyw.netease.com/interface/message/get'

    async def __get_token(
            self,
            sky_id: str
    ) -> str:
        """
        根据uid获取登录的token
        """
        body = {
            "cmd": "kefu_get_token",
            "uid": "@ad.bilibili_sdk.win.163.com",
            "game_uid": sky_id,
            "os": "android",
            "game_server": "8000",
            "login_from": "0",
            "map": "CandleSpace",
            "return_buff": "false"
        }
        async with httpx.AsyncClient() as client:
            res = await client.post(self.api_get_token, json=body)
            result = res.json().get('result')
            return json.loads(result).get('token')

    async def get_answer(
            self,
            sky_id: str,
            key_words: str
    ) -> str:
        """
        获取回答的接口
        """
        token = await self.__get_token(sky_id)
        params = {
            'ismanual': '0',
            'q': key_words,
            'token': token
        }
        async with httpx.AsyncClient() as client:
            res = await client.get(
                self.answer,
                params=params
            )
            answer = res.json()['answer']
            return answer

    async def get_activities(self, sky_id: str) -> str:
        """
        获取活动日历
        """
        answer = await self.get_answer(sky_id, 'T一c四_热点精灵日历')
        img = re.findall('src="(.*?)"', answer)[0]
        return img

    async def get_weather(self, sky_id: str) -> str:
        """
        获取今日天气预报
        """
        answer = await self.get_answer(sky_id, 'T一d一_热点天气预报')
        img = re.findall('src="(.*?)"', answer)[2]
        return img

    async def request_to_sprite(
            self,
            token: str,
            key_words: str
    ) -> dict:
        """
        向精灵接口发送请求
        """
        params = {
            'ismanual': '0',
            'answerType': '0',
            'askFrom': 'click',
            'from': 'webapp',
            'system': 'crmpro',
            'showQ': key_words,
            'q': key_words,
            'token': token
        }
        async with httpx.AsyncClient() as client:
            res = await client.get(
                self.answer,
                params=params
            )
            return res.json()

    async def get_message(self, token: str) -> str:
        """
        获取与精灵对话后的最后一条消息
        这个基本没用
        """
        params = {
            'version': '2.1',
            'token': token
        }
        async with httpx.AsyncClient() as client:
            res = await client.get(
                self.sprite_answer,
                params=params
            )
            return res.json().get('best').get('answer')

    async def get_candles(self, sky_id: str) -> str:
        """
        查询普通蜡烛的记录
        """
        token = await self.__get_token(sky_id)
        results = await self.request_to_sprite(token, '蜡烛查询')
        if results.get('code') == 200:
            answer = results.get('answer')
            changes: str = answer.strip(
                '<默认回复>小易帮您查到'
                '最近蜡烛变化记录：#r请留意：'
                '#R维护补偿#n所获得道具记录本功能不显示'
            )
            log = changes.replace('#r', '\n').replace('#R', '【').replace('#n', '】').strip(
                '若您想要查询更多蜡烛变化请点击<ask>【更多蜡烛查询】</ask'
            )
            return f'---最近的普通蜡烛变化记录---\n{log}'
        else:
            return '查询失败，未知错误'

    async def get_season_candles(self, sky_id: str) -> str:
        """
        查询季节蜡烛的记录
        """
        token = await self.__get_token(sky_id)
        results: dict = await self.request_to_sprite(token, '季节蜡烛查询')
        if results.get('code') == 200:
            answer = results.get('answer')
            changes: str = answer.strip(
                '<默认回复>小易帮您查到'
                '最近季节蜡烛变化记录：#r请留意：'
                '#R维护补偿#n所获得道具记录本功能不显示'
            )
            log = changes.replace('#r', '\n').replace('#R', '【').replace('#n', '】').strip(
                '若您想要查询更多蜡烛变化请点击<ask>【更多蜡烛查询】</ask'
            )
            return f'---最近的季节蜡烛变化记录---\n{log}'
        else:
            return '查询失败，未知错误'


SaveId = on_command("id -s", aliases={"光遇绑定"}, permission=PRIVATE_FRIEND)
QueryWhiteCandles = on_command("q -w", aliases={"查询白蜡"})
QuerySeasonCandles = on_command("q -s", aliases={"查询季蜡"})
CandlesView = on_command("q -all", aliases={"蜡烛", "我的蜡烛"})  # 啊蜡烛~我的蜡烛~（无端联想）

Weather = on_command("sky weather", aliases={"光遇天气预报", "sky天气", "光遇天气"})
Activities = on_command("sky act", aliases={"活动日历", "精灵日历"})


@SaveId.handle()
async def save_id_handler(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    if plain_text:
        matcher.set_arg("sky_id", args)


@SaveId.got("sky_id", prompt="请输入您的光遇原id，注意不是纯数字的id,可在精灵-查询-查询id查到")
async def sky_id_handler(event: MessageEvent, sky_id: str = ArgPlainText("sky_id")):
    if not re.match('[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12}', sky_id):
        await SaveId.reject("您输入的光遇原id格式有误，请重新输入")
    tmp = await load_sky_id(str(event.sender.user_id))
    if not tmp:
        await save_sky_id(str(event.sender.user_id), sky_id)
        await SaveId.finish("绑定成功")
    else:
        await SaveId.finish("你已经绑定过了，无需重复绑定")


@QueryWhiteCandles.handle()
async def white_candles_handler(bot: Bot, event: MessageEvent):
    sky_id = await load_sky_id(str(event.sender.user_id))
    if not sky_id:
        await QueryWhiteCandles.send(
            '没有相应缓存数据，请先私聊bot进行id绑定操作。\n'
            + To_Get_Uid
        )
    else:
        if sky_id == '':
            await QueryWhiteCandles.send(
                '您还没有绑定您的光遇id，'
                '请私聊bot发送“光遇绑定”来进行绑定\n' +
                To_Get_Uid
            )
        query = Sprite()
        results = await query.get_candles(sky_id)
        if '这边查询一下' not in results:
            pass
        else:
            time.sleep(1)
            results = await query.get_candles(sky_id)
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
            await QueryWhiteCandles.send(results)


@QuerySeasonCandles.handle()
async def season_candles_handler(bot: Bot, event: MessageEvent):
    sky_id = await load_sky_id(str(event.sender.user_id))
    if not sky_id:
        await QuerySeasonCandles.send(
            '没有相应缓存数据，请先私聊bot进行id绑定操作。\n' +
            To_Get_Uid
        )
    else:
        if sky_id == '':
            await QuerySeasonCandles.send(
                '您还没有绑定您的光遇id，'
                '请私聊bot发送“光遇绑定”来进行绑定\n' +
                To_Get_Uid
            )
        query = Sprite()
        results = await query.get_season_candles(sky_id)
        if '这边查询一下' not in results:
            pass
        else:
            time.sleep(1)
            results = await query.get_season_candles(sky_id)
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
            await QuerySeasonCandles.send(results)


@CandlesView.handle()
async def candle_view(event: MessageEvent):
    sky_id = await load_sky_id(str(event.sender.user_id))
    if not sky_id:
        await CandlesView.send(
            '没有相应缓存数据，请先私聊bot进行id绑定操作。\n' +
            To_Get_Uid
        )
    else:
        if sky_id == '':
            await CandlesView.send(
                '您还没有绑定您的光遇id，'
                '请私聊bot发送“光遇绑定”来进行绑定\n' +
                To_Get_Uid
            )
        query = Sprite()
        season = await query.get_season_candles(sky_id)
        white = await query.get_candles(sky_id)

        if '这边查询一下' not in season and '这边查询一下' not in white:
            pass
        else:
            time.sleep(1)
            season = await query.get_season_candles(sky_id)
            white = await query.get_candles(sky_id)
        season_left = re.findall('剩余：(\d+)+?', season)[0]
        white_left = re.findall('剩余：(\d+)+?', white)[0]
        await CandlesView.send(
            f'蜡烛总览：\n●普通蜡烛：{white_left}\n●季节蜡烛：{season_left}'
        )


@Weather.handle()
async def weather_handle(event: MessageEvent):
    query = Sprite()
    sky_id = await load_sky_id(str(event.sender.user_id))
    if not sky_id:
        await Weather.send(
            '没有相应缓存数据，请先私聊bot进行id绑定操作。\n' +
            To_Get_Uid
        )
    else:
        if sky_id == '':
            await Weather.send(
                '您还没有绑定您的光遇id，'
                '请私聊bot发送“光遇绑定”来进行绑定\n' +
                To_Get_Uid
            )
        results = await query.get_weather(sky_id)
        await Weather.send(MessageSegment.image(results))


@Activities.handle()
async def act_handle(event: MessageEvent):
    query = Sprite()
    sky_id = await load_sky_id(str(event.sender.user_id))
    if not sky_id:
        await Activities.send(
            '没有相应缓存数据，请先私聊bot进行id绑定操作。\n' +
            To_Get_Uid
        )
    else:
        if sky_id == '':
            await Activities.send(
                '您还没有绑定您的光遇id，'
                '请私聊bot发送“光遇绑定”来进行绑定\n' +
                To_Get_Uid
            )
        results = await query.get_activities(sky_id)
        await Activities.send(MessageSegment.image(results))


__all__ = (
    "save_id_handler",
    "sky_id_handler",
    "white_candles_handler",
    "season_candles_handler",
    "weather_handle"
)
