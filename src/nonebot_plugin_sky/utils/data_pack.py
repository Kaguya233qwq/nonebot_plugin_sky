import os
from pathlib import Path
import zipfile
import shutil
import httpx

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.params import CommandArg, ArgPlainText

from ..tools.update import check_datapack_latest
from ..config.command import get_cmd_alias


class SkyDataPack:
    """光遇数据包类"""

    def __init__(self):

        self.url = 'https://gitee.com/Kaguyaaa/nonebot_plugin_sky/releases/download/SkyDataPack-v'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
            '/62.0.3202.9 Safari/537.36',
        }

    async def download(self):
        logger.info('开始下载安装光遇攻略数据包')
        try:
            version = await check_datapack_latest()
            ver_url = f'{version}/SkyDataPack.zip'
            async with httpx.AsyncClient(
                    headers=self.headers
            ) as client:
                async with client.stream(
                        "GET",
                        url=self.url + ver_url,
                        follow_redirects=True
                ) as stream:
                    size = 0
                    chunk = 1024 * 1024 * 1  # 下载速度1Mb/s
                    total = int(stream.headers['content-length']) / 1024 / 1024
                    with open('SkyDataPack.zip', 'wb') as f:
                        async for data in stream.aiter_bytes(chunk_size=chunk):
                            f.write(data)
                            size += len(data) / 1024 / 1024
                            print(
                                '\r[下载进度]: %0.2f MB/%0.2f MB' %
                                (size, total), end='')
                    logger.success('文件下载完成！')
        except (httpx.HTTPError, httpx.NetworkError):
            logger.error('数据包下载失败，请检查网络后重试')


async def install(path) -> None:
    """解压缩并移动到指定位置"""

    async def support_gbk(file: zipfile.ZipFile):
        """gbk编码防止中文乱码"""
        name_to_info = file.NameToInfo
        # copy map first
        for name, info in name_to_info.copy().items():
            real_name = name.encode('cp437').decode('gbk')
            if real_name != name:
                info.filename = real_name
                del name_to_info[name]
                name_to_info[real_name] = info
        return file

    logger.info('开始解压缩文件')
    zip_file = zipfile.ZipFile(path)
    zip_ = await support_gbk(zip_file)
    file_name = path.strip('.zip')
    for names in zip_.namelist():
        zip_.extract(names, file_name)
    zip_.close()
    logger.info('解压缩完成')
    Path('SkyDataPack.zip').unlink()
    logger.success('文件安装完成')


async def check() -> bool:
    """
    检查数据包
    存在返回True，不存在返回False
    """
    return Path('SkyDataPack').exists()


async def load_image(cmd_path: str) -> Message:
    """
    扫描指定命令路径下所有图片
    返回一个图片组的MessageSegment
    """
    love = MessageSegment.face(66)
    results = love + MessageSegment.text(cmd_path) + love
    path = Path('SkyDataPack') / cmd_path
    image_list = path.glob("**/*")
    for image in image_list:
        results += MessageSegment.image(image.resolve().as_uri())
    return results


Install = on_command(
    "data_pack -install",
    aliases=get_cmd_alias('data_pack_install'))
MenuV2 = on_command("menu v2", aliases=get_cmd_alias('menu_v2'))
Cmd = on_command("-")


@Install.handle()
async def install_handle():
    """
    下载数据包的流程逻辑
    """
    try:
        is_existed = await check()
        if not is_existed:
            await Install.send('正在下载安装数据包，请稍候...')
            data = SkyDataPack()
            await data.download()
            await install('SkyDataPack.zip')
            await Install.finish('安装完成')
        else:
            pass
    except (httpx.HTTPError, httpx.NetworkError):
        await Install.send('安装失败。请稍后重试')


@Install.got("existed", prompt="数据包已存在，是否删除已有资源并重新下载？")
async def selecting(existed: str = ArgPlainText("existed")):
    try:
        if '是' in existed:
            shutil.rmtree('SkyDataPack')
            await Install.send('正在下载安装数据包，请稍候...')
            data = SkyDataPack()
            await data.download()
            await install('SkyDataPack.zip')
            await Install.finish('安装完成')
        elif '否' in existed:
            await Install.finish('安装已取消')
        else:
            await Install.reject('命令不正确，请输入“是”或“否”')
    except (httpx.HTTPError, httpx.NetworkError):
        await Install.send('安装失败。请稍后重试')


@MenuV2.handle()
async def menu_v2():
    """
    扫描目录下的文件夹，生成命令列表
    """
    menu_list = '---数据包命令---\n'
    if os.path.isdir('SkyDataPack'):
        cmd_list = os.listdir('SkyDataPack')
        for param in cmd_list:
            if os.path.isdir('SkyDataPack/%s' % param):
                menu_list += "-" + param + '\n'
        menu_list += '-----------------'
        await Cmd.send(menu_list)


@Cmd.handle()
async def cmd(args: Message = CommandArg()):
    """
    扫描文件夹，按照文件夹名注入命令
    """
    plain_text = args.extract_plain_text()
    if os.path.isdir('SkyDataPack'):
        cmd_list = os.listdir('SkyDataPack')
        for cmd_ in cmd_list:
            if cmd_ == plain_text:
                results_ = await load_image(cmd_)
                await Cmd.send(results_)
    else:
        pass


__all__ = (
    "install_handle",
    "selecting",
    "menu_v2",
    "cmd"
)
