# -*- coding: utf-8 -*-
# @Author  : 子龙君
# @Email   :  1435608435@qq.com
# @Github    : neet姬辉夜大人
# @Software: PyCharm

import httpx
import datetime
import json

import nonebot
from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import NetworkError as networkError

daily_yoli = on_command("daily_yoli", aliases={"光遇今日攻略"})

# 加载bot昵称
try:
    bot_name = nonebot.get_driver().config.nickname
    if not list(bot_name) or list(bot_name) == ['']:
        Nick = '未命名'
    else:
        Nick = list(bot_name)[0]
except Exception as e:
    Nick = '未命名'
    logger.error(e)
    logger.warning('您还没有配置bot的昵称，请先进入env文件配置')


class SkyDaily:
    """光遇类"""

    def __init__(self):
        self.url = 'https://weibo.com/ajax/statuses/mymblog?uid=7360748659&page=1&feature=0'
        self.longtext = 'https://weibo.com/ajax/statuses/longtext?id='
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                          '/62.0.3202.9 Safari/537.36',
            'cookie': 'SUB=_2AkMUd3SHf8NxqwFRmP8Ty2Pna4VwywzEieKiK4VcJRMxHRl'
                      '-yT9jqnAOtRB6P_daaLXfdvYkPfvZhXy3bTeuLdBjWXF9;'
        }
        self.copyright_ = ('------------'
                           '\r【数据来源：微博@今天游离翻车了吗】\n'
                           '--本插件仅做数据展示之用，著作权归原文作者所有。'
                           '转载或转发请附文章作者微博--')

    @staticmethod
    def get_today():
        """获取今日日期"""
        date = datetime.date.today().timetuple()
        today = str(date.tm_mon) + '月' + str(date.tm_mday) + '日'
        today_format = str(date.tm_mon) + '.' + str(date.tm_mday)
        logger.info('今天是：{}'.format(today))
        return today_format

    async def get_mblog_id(self, today):
        """获取微博 @今天游离翻车了吗 今日攻略详情"""

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=self.url,
                headers=self.headers)
            content = json.loads(response.text)
            overhead = content['data']['list']
            for log in overhead:
                if today in log['text_raw']:
                    return log
            return None

    async def get_longtext(self, mblog_id: str):
        """获取微博 @今天游离翻车了吗 今日攻略长文本"""

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=self.longtext + mblog_id,
                headers=self.headers)
            content = json.loads(response.text)
            longtext = content['data']['longTextContent']
            return longtext

    async def get_data(self):
        """获取今日攻略数据"""
        results = MessageSegment.text('')
        today = self.get_today()
        overhead = await self.get_mblog_id(today)
        if overhead:
            mblog_id = overhead['mblogid']
            longtext = await self.get_longtext(mblog_id)
            results += MessageSegment.text(longtext)
            pic_infos = overhead['pic_infos']
            for pic in pic_infos:
                large_url = pic_infos[pic]['large']['url']
                img = MessageSegment.image(large_url)
                results += img
            results += self.copyright_  # 附加版权信息
        else:
            notice = '今日数据还未更新，请耐心等候'
            logger.warning('今日数据还未更新，请耐心等候')
            results += MessageSegment.text(notice)
        return results


async def chain_reply(
        # 构造聊天记录转发消息，参照了塔罗牌插件
        bot: Bot,
        msg: MessageSegment
):
    chain = []
    global Nick

    data = {
        "type": "node",
        "data": {
            "name": Nick,
            "uin": f"{bot.self_id}",
            "content": msg
        },
    }
    chain.append(data)
    return chain


@daily_yoli.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    try:
        sky = SkyDaily()
        results = await sky.get_data()
        chain = await chain_reply(bot, results)
        await bot.send_group_forward_msg(
            group_id=event.group_id,
            messages=chain
        )

    except networkError:
        logger.error('NetworkError: 网络环境较差，调用发送信息接口超时')
        await daily_yoli.send(
            message='网络环境较差，调用发送信息接口超时'
        )
