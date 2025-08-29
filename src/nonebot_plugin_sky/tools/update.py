import re
from typing import Union

import pip
import httpx
from bs4 import BeautifulSoup
import logging
from importlib import metadata

from nonebot import logger
from nonebot.matcher import Matcher

logging.captureWarnings(True)  # 去掉建议使用SSL验证的显示

try:
    __version__ = metadata.version("nonebot-plugin-sky")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0-dev"


async def get_datapack_ver() -> str:
    """
    检查本地数据包版本
    """
    try:
        with open("SkyDataPack/version", "r", encoding="utf-8") as f:
            datapack_ver = f.read()
            f.close()
            return datapack_ver
    except Exception as e:
        logger.error("获取本地数据包版本失败，原因：%s" % str(e))
        return "1.0.0"


async def check_plugin_latest() -> str:
    """
    检查最新发布的插件版本
    """
    url = "https://github.com/Kaguya233qwq/nonebot_plugin_sky/"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome"
        "/62.0.3202.9 Safari/537.36"
    }
    async with httpx.AsyncClient(verify=False, timeout=10) as client:
        res = await client.get(url=url, headers=headers)
        bs = BeautifulSoup(res.text, "lxml")
        tag = bs.find(class_="package-header__name")
        if not tag:
            return ""
        results = tag.get_text()
        latest_ver = results.strip("\n").strip(" ").replace("\n", "")
        latest_ver = latest_ver.replace("nonebot-plugin-sky ", "")
        return latest_ver


async def check_datapack_latest() -> str:
    """
    检查最新发布的数据包版本
    """
    url = "https://gitee.com/Kaguyaaa/nonebot_plugin_sky/"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome"
        "/62.0.3202.9 Safari/537.36"
    }
    try:
        async with httpx.AsyncClient(verify=False, timeout=None) as client:
            res = await client.get(url=url, headers=headers)
            comp = re.compile("SkyDataPack-v(\\d+.\\d+.\\d+)")
            if not comp:
                return ""
            latest_ver = comp.findall(res.text)[0]
            return latest_ver
    except Exception:
        logger.error("获取数据包更新信息失败")
        return ""


async def upgrade_plugin() -> Union[bool, None]:
    latest = await check_plugin_latest()
    if latest:
        if latest == __version__:
            logger.info("已是最新版本，无需更新")
            return False
        else:
            logger.info("发现新版本，开始下载更新")
            return True
    else:
        return None


async def check_handle(matcher: Matcher):
    await matcher.send("正在检查更新，请稍候")
    results = ""
    plugin_latest = await check_plugin_latest()

    if plugin_latest:
        if plugin_latest == __version__:
            results += "-当前插件已是最新版本(v%s)\n" % __version__
            logger.info("当前插件已是最新版本(v%s)" % __version__)
        else:
            results += f"-[New]发现新版本插件：v{__version__} -> v{plugin_latest}\n"
            logger.warning("发现新版本插件：v%s" % plugin_latest)
    else:
        results += "-[Error]插件检查更新失败，请稍后重试"

    datapack_latest = await check_datapack_latest()
    datapack_current = await get_datapack_ver()
    if datapack_latest:
        if datapack_latest == datapack_current:
            results += "-本地数据包已是最新版本(v%s)" % datapack_current
            logger.info("本地数据包已是最新版本(v%s)" % datapack_current)
        else:
            results += (
                f"-[New]发现新版本数据包：v{datapack_current} -> v{datapack_latest}"
            )
            logger.warning("发现新版本数据包：v%s" % datapack_latest)
    else:
        results += "-[Error]数据包检查更新失败，请稍后重试"

    await matcher.send(results)


async def upgrade_handle(matcher: Matcher):
    await matcher.send("检查插件是否有更新..")
    upgrade = await upgrade_plugin()
    if upgrade is None:
        await matcher.send("检查更新失败")
        logger.error("检查更新失败")
    elif upgrade is True:
        await matcher.send("正在下载更新，请稍候..")
        pip.main(["install", "nonebot-plugin-sky", "--upgrade"])
        await matcher.send("插件更新完成，请重新启动Nonebot")
    else:
        await matcher.send("插件已是最新版，无需更新")


__all__ = ("check_handle", "upgrade_handle", "check_datapack_latest")
