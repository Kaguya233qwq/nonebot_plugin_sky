import asyncio
from pathlib import Path
import sys
from typing import Union

import httpx
import logging
from importlib import metadata

from nonebot import logger
from nonebot.matcher import Matcher

logging.captureWarnings(True)  # 去掉建议使用SSL验证的显示

try:
    __version__ = metadata.version("nonebot-plugin-sky")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0-dev"


async def get_datapack_ver() -> str | None:
    """
    检查本地数据包版本
    """

    ver = Path("SkyDataPack/version")
    if not ver.exists():
        return
    with open(ver, "r", encoding="utf-8") as f:
        return f.read()


async def check_plugin_latest() -> str:
    """
    通过 PyPI API 检查插件的最新版本
    """

    pypi_url = "https://pypi.org/pypi/nonebot-plugin-sky/json"

    headers = {"User-Agent": "nonebot_plugin_sky_update_checker/1.0"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # 优先尝试官方源，如果失败则尝试镜像源
            try:
                res = await client.get(url=pypi_url, headers=headers)
                res.raise_for_status()
            except httpx.RequestError:
                logger.warning("访问 PyPI 官方源失败，正在尝试镜像源...")
                pypi_mirror_url = (
                    "https://pypi.tuna.tsinghua.edu.cn/pypi/nonebot-plugin-sky/json"
                )
                res = await client.get(url=pypi_mirror_url, headers=headers)
                res.raise_for_status()
                return "网络错误"
            data = res.json()
            latest_version = data.get("info", {}).get("version")

            if latest_version:
                return str(latest_version)
            else:
                return ""

    except httpx.HTTPStatusError:
        return ""
    except Exception:
        return ""


async def check_datapack_latest() -> str:
    """
    通过 Gitee API 检查最新发布的数据包版本，稳定且快速。
    """

    gitee_api_url = (
        "https://gitee.com/api/v5/repos/Kaguyaaa/nonebot_plugin_sky/releases/latest"
    )

    headers = {"User-Agent": "nonebot_plugin_sky_datapack_checker/1.0"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(url=gitee_api_url, headers=headers)
            res.raise_for_status()
            data = res.json()
            tag_name = data.get("tag_name")
            if not tag_name:
                return ""
            version_prefix = "SkyDataPack-v"
            if tag_name.startswith(version_prefix):
                version = tag_name.replace(version_prefix, "", 1)
                return version
            else:
                logger.warning(f"Gitee 最新 Release 的 tag 格式不符合预期: {tag_name}")
                return ""

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logger.info("Gitee 仓库中没有找到任何 Release。")
        else:
            logger.error(f"访问 Gitee API 时发生HTTP错误: {e}")
        return ""
    except Exception as e:
        logger.error(f"获取数据包更新信息失败: {e}")
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
            logger.info("发现新版本插件：v%s" % plugin_latest)
    else:
        results += "-[Error]插件检查更新失败，请稍后重试"

    datapack_latest = await check_datapack_latest()
    datapack_current = await get_datapack_ver()
    datapack_current = "1.0.0"
    if not datapack_current:
        results += "-数据包未安装"
        logger.info("数据包未安装")
    else:
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
    await matcher.send("正在检查插件更新...")

    has_update = await upgrade_plugin()

    if has_update is None:
        await matcher.send("检查更新失败，请检查网络或稍后再试。")
        logger.error("检查更新失败")
        return

    if not has_update:
        await matcher.send("插件已是最新版本，无需更新。")
        return

    await matcher.send("发现新版本，正在尝试更新，请稍候...")

    python_executable = sys.executable

    command = [
        python_executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        "nonebot-plugin-sky",
    ]
    process = await asyncio.create_subprocess_exec(
        *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        logger.info("插件更新成功。")
        log_output = stdout.decode("utf-8", errors="ignore")
        logger.debug(f"Pip output:\n{log_output}")
        await matcher.send("插件更新成功！\n请手动重启 NoneBot 以使新版本生效。")
    else:
        error_message = stderr.decode("utf-8", errors="ignore")
        logger.error(f"插件更新失败，返回码: {process.returncode}")
        logger.error(f"Pip 错误信息:\n{error_message}")

        # 将关键错误信息发送给用户
        await matcher.send(
            f"插件更新失败！\n错误信息: `{error_message[-200:]}`\n请检查日志获取详细信息。"
        )


__all__ = ("check_handle", "upgrade_handle", "check_datapack_latest")
