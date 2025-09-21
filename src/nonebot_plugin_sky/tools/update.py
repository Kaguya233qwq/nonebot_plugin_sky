import asyncio
import sys
from pathlib import Path

import httpx
import logging
from importlib import metadata

from nonebot import logger
from nonebot.matcher import Matcher

from packaging.version import parse as parse_version, Version

logging.captureWarnings(True)

try:
    __version__ = metadata.version("nonebot-plugin-sky")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0-dev"

CURRENT_PLUGIN_VERSION: Version = parse_version(__version__)


async def get_datapack_ver() -> str | None:
    """检查本地数据包版本"""
    ver_path = Path("SkyDataPack/version")
    if not ver_path.exists():
        return None
    try:
        import aiofiles

        async with aiofiles.open(ver_path, "r", encoding="utf-8") as f:
            return (await f.read()).strip()
    except (ImportError, IOError):
        with open(ver_path, "r", encoding="utf-8") as f:
            return f.read().strip()


async def check_plugin_latest() -> Version | None:
    """通过 PyPI API 检查插件的最新版本，返回 Version 对象"""
    pypi_url = "https://pypi.org/pypi/nonebot-plugin-sky/json"
    pypi_mirror_url = "https://pypi.tuna.tsinghua.edu.cn/pypi/nonebot-plugin-sky/json"
    headers = {"User-Agent": "nonebot_plugin_sky_update_checker/1.0"}

    async with httpx.AsyncClient(timeout=10) as client:
        for url in [pypi_url, pypi_mirror_url]:
            try:
                res = await client.get(url=url, headers=headers)
                res.raise_for_status()
                data = res.json()
                latest_version_str = data.get("info", {}).get("version")
                if latest_version_str:
                    return parse_version(latest_version_str)
                return None
            except httpx.RequestError as e:
                logger.warning(f"访问 PyPI 源 {url} 失败: {e}")
            except (KeyError, TypeError, Exception) as e:
                logger.error(f"解析 PyPI 响应失败: {e}")
                return None
    return None


async def check_datapack_latest() -> Version | None:
    """通过 Gitee API 检查最新数据包版本，返回 Version 对象"""
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
                return None

            version_prefix = "SkyDataPack-v"
            if tag_name.startswith(version_prefix):
                version_str = tag_name.replace(version_prefix, "", 1)
                return parse_version(version_str)

            logger.warning(f"Gitee 最新 Release 的 tag 格式不符合预期: {tag_name}")
            return None
    except Exception as e:
        logger.error(f"获取数据包更新信息失败: {e}")
        return None


async def upgrade_plugin() -> bool:
    """检查插件是否有新版本可供升级"""
    latest_version = await check_plugin_latest()
    if latest_version:
        if latest_version > CURRENT_PLUGIN_VERSION:
            logger.info(f"发现新版本: {CURRENT_PLUGIN_VERSION} -> {latest_version}")
            return True
    return False


async def check_handle(matcher: Matcher):
    await matcher.send("正在检查更新，请稍候...")
    results = ""

    # 检查插件更新
    plugin_latest = await check_plugin_latest()
    if plugin_latest:
        if plugin_latest > CURRENT_PLUGIN_VERSION:
            results += f"-[New] 发现新版本插件：v{CURRENT_PLUGIN_VERSION} -> v{plugin_latest}\n"
        elif plugin_latest < CURRENT_PLUGIN_VERSION:
            results += f"-[Info] 当前插件版本 v{CURRENT_PLUGIN_VERSION} 高于 PyPI 最新版 v{plugin_latest}\n"
        else:
            results += f"- 当前插件已是最新版本 (v{CURRENT_PLUGIN_VERSION})\n"
    else:
        results += "-[Error] 插件检查更新失败，请稍后重试\n"

    # 检查数据包更新
    datapack_latest = await check_datapack_latest()
    datapack_current_str = await get_datapack_ver()

    if not datapack_current_str:
        results += "- 数据包未安装"
    else:
        datapack_current = parse_version(datapack_current_str)
        if datapack_latest:
            if datapack_latest > datapack_current:
                results += f"-[New] 发现新版本数据包：v{datapack_current} -> v{datapack_latest}"
            elif datapack_latest < datapack_current:
                results += f"-[Info] 当前数据包版本 v{datapack_current} 高于 Gitee 最新版 v{datapack_latest}"
            else:
                results += f"- 本地数据包已是最新版本 (v{datapack_current})"
        else:
            results += "-[Error] 数据包检查更新失败，请稍后重试"

    await matcher.send(results.strip())


async def upgrade_handle(matcher: Matcher):
    await matcher.send("正在检查插件更新...")

    has_update = await upgrade_plugin()

    if not has_update:
        await matcher.send("插件已是最新版本或检查更新失败，无需更新。")
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
        await matcher.send("✅ 插件更新成功！\n请手动重启 NoneBot 以使新版本生效。")
    else:
        error_message = stderr.decode("utf-8", errors="ignore")
        logger.error(f"插件更新失败，返回码: {process.returncode}")
        logger.error(f"Pip 错误信息:\n{error_message}")
        await matcher.send(
            f"❌ 插件更新失败！\n错误信息: `{error_message[-200:]}`\n请检查日志获取详细信息。"
        )
