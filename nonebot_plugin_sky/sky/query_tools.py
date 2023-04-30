import json
import os
import re
import time
from typing import Union

import httpx
from nonebot import on_command
from nonebot.adapters.onebot.v11 import PRIVATE_FRIEND, Message, Bot, MessageSegment, MessageEvent
from nonebot.internal.matcher import Matcher
from nonebot.internal.params import ArgPlainText
from nonebot.params import CommandArg

from ..utils_ import send_forward_msg
from ..config.msg_forward import is_forward
from ..config.command import *

NO_CACHE_ID_MSG = '没有相应缓存数据，请先私聊bot进行id绑定操作。\n'
NO_BIND_MSG = '您还没有绑定您的光遇id，请私聊bot发送“光遇绑定”来进行绑定\n'


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


def get_id_img():
    abspath_ = os.path.abspath(__file__).strip('query_tools.py')
    path = 'file:///' + abspath_ + 'get_id.png'
    return MessageSegment.image(path)


To_Get_Uid = (
        '如何获取uid？见下图：' +
        get_id_img()
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

    async def get_activities(
            self,
            sky_id: str
    ) -> Union[str, MessageSegment]:
        """
        获取活动日历
        """
        answer = await self.get_answer(sky_id, 'T一c四_热点精灵日历')
        if '光遇的世界很美好' in answer:
            return '暂无活动日历哦~'
        else:
            results = re.findall('src="(.*?)"', answer)[0]
            return MessageSegment.image(results)

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
        try:
            if results.get('answer'):
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
                return '服务器异常，返回结果时出现错误'
        except Exception as e:
            str(e)
            return '查询失败，未知错误'

    async def get_season_candles(self, sky_id: str) -> str:
        """
        查询季节蜡烛的记录
        """
        token = await self.__get_token(sky_id)
        results: dict = await self.request_to_sprite(token, '季节蜡烛查询')
        try:
            if results.get('answer'):
                answer = results.get('answer')
                if '小易帮您查到' in answer:
                    changes: str = answer.strip(
                        '<默认回复>小易帮您查到'
                        '最近季节蜡烛变化记录：#r请留意：'
                        '#R维护补偿#n所获得道具记录本功能不显示'
                    )
                    log = changes.replace('#r', '\n').replace('#R', '【').replace('#n', '】').strip(
                        '若您想要查询更多蜡烛变化请点击<ask>【更多蜡烛查询】</ask'
                    )
                    return f'---最近的季节蜡烛变化记录---\n{log}'
                elif '请稍候再查看' in answer:
                    return '季节真空期，季蜡数默认为零'
            else:
                return '服务器异常，返回结果时出现错误'
        except Exception as e:
            str(e)
            return '查询失败，未知错误'


SaveId = on_command("id -s", aliases=get_cmd_alias('save_sky_id'), permission=PRIVATE_FRIEND)
QueryWhiteCandles = on_command("q -w", aliases=get_cmd_alias('qw'))
QuerySeasonCandles = on_command("q -s", aliases=get_cmd_alias('qs'))
CandlesView = on_command("q -all", aliases=get_cmd_alias('qa'))  # 啊蜡烛~我的蜡烛~（无端联想）

Weather = on_command("sky weather", aliases=get_cmd_alias('sky_weather'))
Activities = on_command("sky act", aliases=get_cmd_alias('sky_activities'))


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
            NO_CACHE_ID_MSG
            + To_Get_Uid
        )
    else:
        if sky_id == '':
            await QueryWhiteCandles.send(
                NO_BIND_MSG +
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
            await send_forward_msg(bot, event, results)
        else:
            await QueryWhiteCandles.send(results)


@QuerySeasonCandles.handle()
async def season_candles_handler(bot: Bot, event: MessageEvent):
    sky_id = await load_sky_id(str(event.sender.user_id))
    if not sky_id:
        await QuerySeasonCandles.send(
            NO_CACHE_ID_MSG +
            To_Get_Uid
        )
    else:
        if sky_id == '':
            await QuerySeasonCandles.send(
                NO_BIND_MSG +
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
            await send_forward_msg(bot, event, results)
        else:
            await QuerySeasonCandles.send(results)


@CandlesView.handle()
async def candle_view(event: MessageEvent):
    sky_id = await load_sky_id(str(event.sender.user_id))
    if not sky_id:
        await CandlesView.send(
            NO_CACHE_ID_MSG +
            To_Get_Uid
        )
    else:
        if sky_id == '':
            await CandlesView.send(
                NO_BIND_MSG +
                To_Get_Uid
            )
        query = Sprite()

        try:
            season = await query.get_season_candles(sky_id)
            white = await query.get_candles(sky_id)
            season_left = ''
            if '这边查询一下' not in season and '这边查询一下' not in white:
                pass
            else:
                time.sleep(1)
                season = await query.get_season_candles(sky_id)
                white = await query.get_candles(sky_id)
            if '真空期' in season:
                season_left = 0
            white_left = re.findall('剩余：(\d+)+?', white)[0]
            await CandlesView.send(
                f'蜡烛总览：\n●普通蜡烛：{white_left}\n●季节蜡烛：{season_left}'
            )
        except Exception as e:
            str(e)
            await CandlesView.send('查询失败，返回结果异常')


@Weather.handle()
async def weather_handle(event: MessageEvent):
    query = Sprite()
    sky_id = await load_sky_id(str(event.sender.user_id))
    if not sky_id:
        await Weather.send(
            NO_CACHE_ID_MSG +
            To_Get_Uid
        )
    else:
        if sky_id == '':
            await Weather.send(
                NO_BIND_MSG +
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
            NO_CACHE_ID_MSG +
            To_Get_Uid
        )
    else:
        if sky_id == '':
            await Activities.send(
                NO_BIND_MSG +
                To_Get_Uid
            )
        results = await query.get_activities(sky_id)
        await Activities.send(results)


# __all__ = (
#     "save_id_handler",
#     "sky_id_handler",
#     "white_candles_handler",
#     "season_candles_handler",
#     "weather_handle"
# )
