import os
import re
from typing import Union

import httpx
import json

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, Message, PRIVATE, Bot, MessageSegment
from nonebot.internal.matcher import Matcher
from nonebot.internal.params import ArgPlainText
from nonebot.params import CommandArg

from ..utils_.chain_reply import chain_reply
from ..utils_.json_cards import card_group_bot
from ..config.msg_forward import is_forward


async def __get_data(sky_id, types):
    """
    根据光遇原id
    获取蜡烛变动数据
    """
    # 这是光萌提供的蜡烛查询api，拿来吧你。
    api = 'http://plugin.skybay.cn:443/api/cx_w'
    params = {
        'id': sky_id,
        'cmd': types
    }
    async with httpx.AsyncClient() as client:
        res = await client.get(api, params=params)
        data = json.loads(res.text)
        if data != {}:
            return data
        else:
            return None


async def __parse_data(data_):
    """
    解析返回的json信息
    """
    if data_ is None:
        return "查询失败：id不存在"
    else:
        results = ''
        for item in data_['data']:
            time = item['time']
            cause = item['cause']
            change = item['change']
            if '-' not in change:
                change = f'+{change}'
            residual = item['residual']
            results += f'●{time}\n{cause}【{change}】\n剩余：{residual}\n'
        return results


async def save_sky_id(qq: str, sky_id: str) -> None:
    """
    保存qq号与对应的sky_id
    """
    if not os.path.exists('Sky'):
        os.makedirs('Sky')
        with open("Sky/origin_id", "a") as f:
            f.write(json.dumps({qq: sky_id}))
    else:
        with open("Sky/origin_id", 'r') as f:
            tmp = json.loads(f.read()).update({qq: sky_id})
        with open("Sky/origin_id", 'w') as f:
            f.write(tmp)


async def load_sky_id(qq: str) -> Union[None, str]:
    """
    根据qq读取绑定的光遇id
    """
    if not os.path.exists('Sky'):
        return None
    with open("Sky/origin_id", 'r') as f:
        tmp = json.loads(f.read())
        return tmp.get(qq, '')


SaveId = on_command("id -s", aliases={"光遇绑定"}, permission=PRIVATE)
QueryWhiteCandles = on_command("q -w", aliases={"查询白蜡"})
QuerySeasonCandles = on_command("q -s", aliases={"查询季蜡"})
CandlesView = on_command("q -all", aliases={"蜡烛", "我的蜡烛"})  # 啊蜡烛~我的蜡烛~（无端联想）


@SaveId.handle()
async def save_id_handler(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    if plain_text:
        matcher.set_arg("sky_id", args)


@SaveId.got("sky_id", prompt="请输入您的光遇原id，注意不是纯数字的id,可在精灵-查询-查询id查到")
async def sky_id_handler(event: PrivateMessageEvent, sky_id: str = ArgPlainText("sky_id")):
    if not re.match('[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12}', sky_id):
        await SaveId.reject("您输入的光遇原id格式有误，请重新输入")
    await save_sky_id(str(event.sender.user_id), sky_id)
    await SaveId.finish("绑定成功")


@QueryWhiteCandles.handle()
async def white_candles_handler(bot: Bot, event: GroupMessageEvent):
    sky_id = await load_sky_id(str(event.sender.user_id))
    if not sky_id:
        await QueryWhiteCandles.send(
            '没有相应缓存数据，请先私聊bot进行id绑定操作。'
        )
    else:
        if sky_id == '':
            await QueryWhiteCandles.send(
                '您还没有绑定您的光遇id，'
                '请私聊bot发送“光遇绑定”来进行绑定'
            )
        results = await __parse_data(await __get_data(sky_id, 'bl'))
        if is_forward():
            chain = await chain_reply(bot, results)
            await bot.send_group_forward_msg(
                group_id=event.group_id,
                messages=chain
            )
        else:
            await QueryWhiteCandles.send(results)


@QuerySeasonCandles.handle()
async def season_candles_handler(bot: Bot, event: GroupMessageEvent):
    sky_id = await load_sky_id(str(event.sender.user_id))
    if not sky_id:
        await QuerySeasonCandles.send(
            '没有相应缓存数据，请先私聊bot进行id绑定操作。'
        )
    else:
        if sky_id == '':
            await QuerySeasonCandles.send(
                '您还没有绑定您的光遇id，'
                '请私聊bot发送“光遇绑定”来进行绑定'
            )
        results = await __parse_data(await __get_data(sky_id, 'jl'))
        if is_forward():
            chain = await chain_reply(bot, results)
            await bot.send_group_forward_msg(
                group_id=event.group_id,
                messages=chain
            )
        else:
            await QuerySeasonCandles.send(results)


@CandlesView.handle()
async def candle_view(event: GroupMessageEvent):
    sky_id = await load_sky_id(str(event.sender.user_id))
    white_candles = await __get_data(sky_id, 'bl')
    white = f"● 普通蜡烛总数：{white_candles['data'][0]['residual']}"
    season_candles = await __get_data(sky_id, 'jl')
    season = f"● 季节蜡烛总数：{season_candles['data'][0]['residual']}"
    results = card_group_bot(
        white, season,
        title="蜡烛总览",
        prompt="蜡烛总览"
    )
    await CandlesView.send(results)
