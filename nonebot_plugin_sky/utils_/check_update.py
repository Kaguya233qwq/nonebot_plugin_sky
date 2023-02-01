import httpx
from bs4 import BeautifulSoup
import logging

from nonebot import on_command, logger

logging.captureWarnings(True)  # 去掉建议使用SSL验证的显示

Version = '2.0.8.post1'  # 全局插件版本信息


async def get_datapack_ver():
    """
    检查本地数据包版本
    """
    try:
        with open('SkyDataPack/version', 'r', encoding="utf-8") as f:
            datapack_ver = f.read()
            f.close()
            return datapack_ver
    except Exception as e:
        str(e)
        return '1.0.0'


async def check_plugin_latest():
    """
    检查最新发布的插件版本
    """
    url = 'https://pypi.org/project/nonebot-plugin-sky/'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                      '/62.0.3202.9 Safari/537.36'
    }
    try:
        async with httpx.AsyncClient(
                verify=False,
                timeout=None
        ) as client:
            res = await client.get(
                url=url,
                headers=headers
            )
            bs = BeautifulSoup(res.text)
            results = bs.find(class_='package-header__name').text
            latest_ver = results.strip('\n').strip(' ').replace('\n', '')
            latest_ver = latest_ver.replace('nonebot-plugin-sky ', '')
            return latest_ver
    except Exception as e:
        str(e)
        logger.error('获取插件更新信息失败')


async def check_datapack_latest():
    """
    检查最新发布的数据包版本
    """
    url = 'https://github.com/Kaguya233qwq/nonebot_plugin_sky'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                      '/62.0.3202.9 Safari/537.36'
    }
    try:
        async with httpx.AsyncClient(
                verify=False,
                timeout=None
        ) as client:
            res = await client.get(
                url=url,
                headers=headers
            )
            bs = BeautifulSoup(res.text)
            latest_ver = bs.find(
                class_='css-truncate css-truncate-target text-bold mr-2'
            ).text.strip('SkyDataPack-')
            return latest_ver
    except Exception as e:
        str(e)
        logger.error('获取数据包更新信息失败')


Check = on_command("check", aliases={"检查更新"})


@Check.handle()
async def check_handle():
    await Check.send('正在检查更新，请稍候')
    results = ''
    plugin_latest = await check_plugin_latest()

    if plugin_latest:
        if plugin_latest == Version:
            results += '-当前插件已是最新版本(v%s)\n' % Version
            logger.info('当前插件已是最新版本(v%s)' % Version)
        else:
            results += '-[New]发现新版本插件：v%s\n' % plugin_latest
            logger.warning('发现新版本插件：v%s' % plugin_latest)
    else:
        results += '-[Error]插件检查更新失败，请稍后重试'

    datapack_latest = await check_datapack_latest()
    datapack_current = await get_datapack_ver()
    if datapack_latest:
        if datapack_latest == datapack_current:
            results += '-本地数据包已是最新版本(v%s)' % datapack_current
            logger.info('本地数据包已是最新版本(v%s)' % datapack_current)
        else:
            results += '-[New]发现新版本数据包：v%s' % datapack_latest
            logger.warning('发现新版本数据包：v%s' % datapack_latest)
    else:
        results += '-[Error]数据包检查更新失败，请稍后重试'

    await Check.send(results)
