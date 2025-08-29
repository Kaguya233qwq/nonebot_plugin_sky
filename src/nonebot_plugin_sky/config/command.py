import os
import re
from pathlib import Path
from typing import List

from nonebot import on_command, logger
from nonebot.params import EventPlainText

from . import Config

# 若添加了新的命令，请在这里为新命令注册变量名称
CMD_LIST = [
    # 主命令
    "sky_menu=光遇菜单,sky菜单",
    "sky_cn=今日国服",
    "rockfall=今日落石",
    "sky_in=今日国际服",
    "travel_cn=国服复刻",
    "travel_in=国际服复刻",
    "remain_cn=国服季节剩余",
    "remain_in=国际服季节剩余",
    "sky_queue=排队",
    "sky_notice=公告",
    "sky_clear_cache=清理缓存",
    # 更新相关命令
    "check=检查更新",
    "upgrade=更新插件",
    # 数据包相关命令
    "data_pack_install=安装数据包",
    "menu_v2=菜单v2,数据包菜单",
    # 配置命令
    "at_all_on=开启艾特全体",
    "at_all_off=关闭艾特全体",
    "forward_on=开启转发模式",
    "forward_off=关闭转发模式",
    "cmd_add=添加命令",
    # 雨林干饭小助手
    "lunch_helper=干饭小助手",
    # 落石小助手
    "rockfall_helper=落石小助手",
    # 其他
    "noticeboard=插件公告,插件公告板",
]


def parse_cmd_list(cmd_list: List[str]) -> dict:
    """
    将命令列表解析为命令字典
    """
    cmd_dict = {}
    for cmd in cmd_list:
        cmd = cmd.replace("\n", "")
        key, value = cmd.split("=", 1)
        if "," in value:
            value = value.split(",")
        else:
            value = [value]
        cmd_dict[key] = value
    return cmd_dict


def parse_cmd_dict(cmd_dict: dict) -> list:
    """
    将命令字典解析为命令列表
    """
    cmd_list = []
    for key, value in cmd_dict.items():
        if isinstance(value, list):
            value_str = ",".join(value)
        else:
            value_str = str(value)
        cmd_list.append(f"{key}={value_str}")
    return cmd_list


def check_template() -> None:
    """
    命令模板校验函数：
    若不存在命令模板则自动新建，
    若存在则检测本地模板中的命令是否符合标准

    """
    global CMD_LIST

    if not Path(Config.TEMPLATE_FILE).exists():
        with open(Config.TEMPLATE_FILE, "w", encoding="utf-8") as f:
            CMD_LIST = [cmd + "\n" for cmd in CMD_LIST]
            f.writelines(CMD_LIST)
        logger.info("命令模板初始化成功")
        return

    old_cmds = []
    new_cmds = []

    # 读取用户本地的命令模板
    with open(Config.TEMPLATE_FILE, "r", encoding="utf-8") as f:
        data = f.readlines()
        # 将其转为命令字典并只取其key的列表
        old_cmds = list(parse_cmd_list(data).keys())

    # 读取当前版本程序定义的命令模板
    # 将其转为命令字典并只取其key的列表
    new_cmds = list(parse_cmd_list(CMD_LIST).keys())

    new = set(new_cmds) - set(old_cmds)  # 新增的命令
    discard = set(old_cmds) - set(new_cmds)  # 废弃的命令
    # 若有新增的命令则把新增命令添加进去
    for cmd in list(new):
        for i in CMD_LIST:
            if i.startswith(cmd):
                data.append(i)
                logger.info(f"当前版本新增命令:{cmd}")

    # 若有废弃的命令则
    for cmd in list(discard):
        for i in data:
            if i.startswith(cmd):
                data.remove(i)
                logger.info(f"已移除过时的命令:{cmd}")
    if new or discard:
        # 将调整后的数据写入文件
        with open(Config.TEMPLATE_FILE, "w", encoding="utf-8") as f:
            f.writelines(data)


def initialize() -> dict:
    """
    初始化全局配置
    """
    if not Path("Sky").is_dir():
        os.mkdir("Sky")
    check_template()  # 校验是否含有废弃命令或新增命令,或是否需要新建模板
    with open(Config.TEMPLATE_FILE, "r", encoding="utf-8") as f:
        data = f.readlines()
    logger.success(f"全局命令配置读取成功，{len(data)} 个命令已加载")
    return parse_cmd_list(data)


CmdConfig = initialize()  # 加载全局配置


def get_cmd_alias(cmd: str) -> set:
    """
    根据命令获取命令别名
    """
    global CmdConfig
    alias_list = CmdConfig.get(cmd, [])
    alias = set(alias_list)
    return alias


async def add_cmd_aliases(cmd: str, alias: str) -> bool:
    """
    添加命令别名
    """

    with open(Config.TEMPLATE_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        if cmd in line:
            index = lines.index(line)
            lines[index] = line.strip("\n") + f",{alias}\n"
            with open(Config.TEMPLATE_FILE, "w", encoding="utf-8") as f:
                f.writelines(lines)
            logger.success("命令别名添加成功，将在下次重启后生效")
            break
    else:
        logger.error("找不到命令")
        return False
    return True


AddCmdAliases = on_command("cmd -add", aliases=get_cmd_alias("cmd_add"))


@AddCmdAliases.handle()
async def add_cmd_aliases_handle(msg: str = EventPlainText()):
    if not re.findall("cmd -add (.+) (.+)", msg):
        await AddCmdAliases.send("您输入的命令格式有误。用法：\ncmd -add [cmd] [alias]")
    else:
        cmd = re.findall("cmd -add (.+) (.+)", msg)[0][0]
        alias = re.findall("cmd -add (.+) (.+)", msg)[0][1]
        results = await add_cmd_aliases(cmd, alias)
        if results:
            await AddCmdAliases.send(
                f"命令 {cmd} 添加别名 {alias} 成功,将在下次重启后生效"
            )
        else:
            await AddCmdAliases.send("Command not found：找不到命令")


__all__ = ("add_cmd_aliases_handle", "get_cmd_alias", "initialize", "CmdConfig")
