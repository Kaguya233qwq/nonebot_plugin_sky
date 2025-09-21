import asyncio
import os
import shutil
import zipfile
from pathlib import Path
import httpx
import aiofiles

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.params import ArgPlainText, CommandArg
from nonebot.matcher import Matcher

from ..config.command import get_cmd_alias

ASSET_NAME = "SkyDataPack.zip"
DATA_DIR = Path("SkyDataPack")
ZIP_FILENAME = DATA_DIR.with_suffix(".zip")


async def get_latest_datapack_url_from_api() -> str | None:
    """
    通过 Gitee v5 API 获取最新发行版中数据包的下载链接
    """
    api_url = (
        f"https://gitee.com/api/v5/repos/Kaguyaaa/nonebot_plugin_sky/releases/latest"
    )
    headers = {
        "User-Agent": "NoneBot-Plugin-Sky-Updater",
    }

    logger.info("正在通过 Gitee API 查询最新数据包版本...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers, timeout=20.0)
            response.raise_for_status()
            data = response.json()

        for asset in data.get("assets", []):
            if asset.get("name") == ASSET_NAME:
                download_url = asset.get("browser_download_url")
                logger.info(f"成功获取下载链接，最新版本 Tag: {data.get('tag_name')}")
                return download_url

        logger.error("在最新的发行版中未找到名为 'SkyDataPack.zip' 的资源文件。")
        return None

    except httpx.HTTPStatusError as e:
        logger.error(
            f"访问 Gitee API 失败，状态码: {e.response.status_code}，请检查仓库路径是否正确。"
        )
        return None
    except Exception as e:
        logger.error(f"查询最新版本时发生未知错误: {e}")
        return None


async def download_datapack():
    """下载最新的数据包文件"""
    download_url = await get_latest_datapack_url_from_api()

    if not download_url:
        return False

    logger.info("开始下载光遇攻略数据包...")
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    try:
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            async with client.stream("GET", download_url, timeout=300.0) as response:
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))
                downloaded_size = 0

                async with aiofiles.open(ZIP_FILENAME, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        await f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(
                                f"下载进度: {downloaded_size / 1024 / 1024:.2f}MB / {total_size / 1024 / 1024:.2f}MB ({progress:.2f}%)",
                                end="\r",
                            )

        logger.success("数据包下载完成！")
        return True
    except (httpx.HTTPError, httpx.NetworkError) as e:
        logger.error(f"数据包下载失败: {e}")
        return False


def _unzip_blocking(zip_path: Path, extract_dir: Path):
    """
    解压文件 
    """
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            try:
                is_utf8 = member.flag_bits & 0x800
                if not is_utf8:
                    member.filename = member.filename.encode("cp437").decode("gbk")
            except Exception:
                logger.warning(f"解码文件名失败: {member.filename}, 尝试使用默认编码。")

            target_path = extract_dir / member.filename
            if member.is_dir():
                target_path.mkdir(parents=True, exist_ok=True)
            else:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as source, open(target_path, "wb") as target:
                    shutil.copyfileobj(source, target)


async def install_datapack():
    """异步解压文件并进行清理"""
    logger.info("开始解压缩文件...")
    await asyncio.to_thread(_unzip_blocking, ZIP_FILENAME, DATA_DIR)
    logger.info("解压缩完成")

    if await asyncio.to_thread(ZIP_FILENAME.exists):
        await asyncio.to_thread(os.remove, ZIP_FILENAME)
    logger.success("数据包安装完成！")


async def check_datapack_exists() -> bool:
    """异步检查数据包目录是否存在"""
    return await asyncio.to_thread(DATA_DIR.exists)


async def remove_datapack():
    """异步移除旧的数据包目录"""
    if await check_datapack_exists():
        logger.info("正在删除旧的数据包...")
        await asyncio.to_thread(shutil.rmtree, DATA_DIR)
        logger.info("旧数据包已删除。")


async def load_images_from_path(cmd_path: str) -> Message:
    """异步扫描指定路径下的所有图片并返回 Message"""
    love = MessageSegment.face(66)
    results = love + MessageSegment.text(cmd_path) + love

    full_path = DATA_DIR / cmd_path

    if not await asyncio.to_thread(full_path.is_dir):
        return Message()

    image_paths = await asyncio.to_thread(lambda: list(full_path.rglob("*.*")))

    for image_path in image_paths:
        if await asyncio.to_thread(image_path.is_file):
            async with aiofiles.open(image_path, "rb") as f:
                image_bytes = await f.read()
                results += MessageSegment.image(image_bytes)

    return results


Install = on_command(
    "data_pack -install", aliases=get_cmd_alias("data_pack_install"), block=True
)
MenuV2 = on_command("menu v2", aliases=get_cmd_alias("menu_v2"))
Cmd = on_command("-")


async def _perform_download_and_install(matcher: Matcher):
    """下载并安装"""
    await matcher.send("正在下载安装数据包，这可能需要一些时间，请稍候...")
    if await download_datapack():
        await install_datapack()
        await matcher.finish("安装完成！")
    else:
        await matcher.finish("下载失败，请检查Nonebot后台日志。")


@Install.handle()
async def install_handle(matcher: Matcher):
    if await check_datapack_exists():
        return
    await _perform_download_and_install(matcher)


@Install.got("confirm", prompt="数据包已存在，是否删除并重新下载？(是/否)")
async def install_confirm(matcher: Matcher, confirm: str = ArgPlainText("confirm")):
    if "是" in confirm:
        await remove_datapack()
        await _perform_download_and_install(matcher)
    elif "否" in confirm:
        await matcher.finish("安装已取消。")
    else:
        await matcher.reject("输入不正确，请重新输入“是”或“否”。")


@MenuV2.handle()
async def menu_v2():
    if not await check_datapack_exists():
        await MenuV2.finish("数据包未安装，请发送“data_pack -install”进行安装。")
        return

    menu_list = "---数据包命令---\n"
    dir_items = await asyncio.to_thread(os.listdir, DATA_DIR)

    for item_name in dir_items:
        if await asyncio.to_thread((DATA_DIR / item_name).is_dir):
            menu_list += f"-{item_name}\n"

    menu_list += "-----------------"
    await MenuV2.send(menu_list)


@Cmd.handle()
async def cmd_handler(args: Message = CommandArg()):
    cmd_text = args.extract_plain_text().strip()
    if not cmd_text:
        return

    if not await check_datapack_exists():
        await Cmd.finish("数据包未安装，请发送“data_pack -install”进行安装。")
        return

    results = await load_images_from_path(cmd_text)
    if len(results) > 2:
        await Cmd.send(results)
    else:
        logger.warning(f"未找到与命令 '{cmd_text}' 匹配的数据包目录或图片。")
