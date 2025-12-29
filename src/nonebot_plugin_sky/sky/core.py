from datetime import datetime, timedelta
import json

import httpx
from ..spider import Spider
from .tools import Tools


class Sky:

    @staticmethod
    async def get_chinese_server_daily():
        """
        获取国服每日任务信息
        """

        # @今天游离翻车了吗 微博uid
        spider = Spider(7360748659)

        await spider.fetch()
        pattern = r"^#[^#]*光遇[^#]*超话]#\s*\d{1,2}\.\d{1,2}\s*"
        blog = spider.filter_by_time().filter_by_regex(pattern).one()
        if not blog:
            return ("【国服】今日任务还未更新", [])
        text = await blog.fetch_long_text()
        binary_images = await blog.fetch_images_binary_list()
        if not text:
            text = "【国服】今日任务还未更新"
        return (
            text + Sky._generate_copywright("今天游离翻车了吗", blog.url),
            binary_images,
        )

    @staticmethod
    async def get_international_server_daily():
        """获取国际服每日任务信息"""

        # @旧日与春 微博uid
        spider = Spider(6502272646)

        await spider.fetch()
        pattern = r"国际服.*(任务)?.*"
        blog = (
            # 这里应该是美国的时间而不是北京时间
            spider.filter_by_time(
                datetime.now().replace(hour=0, minute=0, second=0) - timedelta(hours=16)
            )
            .filter_by_regex(pattern)
            .one()
        )
        if not blog:
            return ("【国际服】今日任务还未更新", [])
        text = await blog.fetch_long_text()
        if not text:
            text = "【国际服】今日任务还未更新"
        binary_images = await blog.fetch_images_binary_list()
        return (text + Sky._generate_copywright("旧日与春", blog.url), binary_images)

    @staticmethod
    async def get_chinese_server_travelling_spirit():
        """获取国服旅行先祖信息"""

        # 陈陈努力不鸽的微博uid
        spider = Spider(5539106873)

        await spider.search("#光遇复刻#")
        pattern = r"复刻"
        # 根据复刻周期函数的时间进行筛选
        tss = Tools.get_chinese_server_travelling_spirit_cycle()
        tips = Tools.get_bot_tips(tss)
        if tss.status is True:
            # 在复刻期间内，判断是否有旅行先祖图片的缓存
            release_time = tss.current_release.replace(" 12:00:00", "")
            data = Tools.get_travelling_spirit_cache(release_time)
            if data:
                return ("", [data], tips)
            else:
                # 实时获取旅行先祖图片
                start_time = datetime.strptime(tss.current_release, "%Y-%m-%d %H:%M:%S")
                blogs = spider.filter_by_time(start_time).filter_by_regex(pattern).all()
                # 如果作者当天发了其他的东西，也会被匹配到
                # 但是通常的复刻先祖有且只有一到两张图片，所以再根据图片数量筛选
                for blog in blogs:
                    if len(blog.pic_list) <= 2:
                        path = await blog.pic_list[0].save(
                            rename_as=release_time, parent="Sky/Cache"
                        )
                        with open(path, "rb") as f:
                            return ("", [f.read()], tips)
                else:
                    return ("没有找到本期复刻先祖的信息", [], tips)
        # 没有在复刻周期内
        return (f"当前无复刻先祖信息，下次复刻公布时间：\n{tss.next_release}", [], tips)

    # @staticmethod
    # async def get_international_server_travelling_spirit():
    #     """获取国际服旅行先祖信息"""

    #     # 光遇Beta搬运工的微博uid
    #     spider = Spider(7555312647)

    @staticmethod
    async def get_sky_notice():
        """获取官方公告"""
        url = "https://ma75.update.netease.com/game_notice/announcement_live.json"
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome"
            "/62.0.3202.9 Safari/537.36",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=headers)
            content = json.loads(response.text)
            return content["OtherChannelMessage"]

    @staticmethod
    async def get_queue_state():
        """获取排队状态"""
        url = "https://live-queue-sky-merge.game.163.com/queue"
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome"
            "/62.0.3202.9 Safari/537.36",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=headers)
            if response.status_code != 200:
                return "服务器返回状态码异常"
            content = response.json()
            state = content["text"]
            if "enter" in state:
                return "当前服务器畅通，无需排队"
            elif "queue" in state:
                wait_time = content["wait_time"]
                players = content["pos"]
                return f"当前排队人数：{players}\n预计排队时间：{wait_time}"
            else:
                return "服务器又炸啦！"  # 破土豆服务器（

    @staticmethod
    def _generate_copywright(user: str, url: str):
        return "------------\n" f"【数据来源：微博@{user}】\n" f"原文链接：{url}"
