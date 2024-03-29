import os
import json
import re
from pathlib import Path
from typing import List

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import EventPlainText

CONFIG_PATH = 'Sky/cmd_setting.cfg'
TEMPLATE_PATH = 'Sky/cmd_template.txt'

# 若添加了新的命令，请在这里为新命令注册变量名称
CMD_LIST = [
    # 主命令
    'sky_menu=光遇菜单,sky菜单\n',
    'sky_cn=今日国服\n',
    'sky_in=今日国际服\n',
    'travel_cn=国服复刻\n',
    'travel_in=国际服复刻\n',
    'remain_cn=国服季节剩余\n',
    'remain_in=国际服季节剩余\n',
    'sky_queue=排队\n',
    'sky_notice=公告\n',
    'sky_clear_cache=清理缓存\n',

    # 更新相关命令
    'check=检查更新\n',
    'upgrade=更新插件\n',

    # 数据包相关命令
    'data_pack_install=安装数据包\n',
    'menu_v2=菜单v2,数据包菜单\n',

    # 配置命令
    'at_all_on=开启艾特全体\n',
    'at_all_off=关闭艾特全体\n',
    'forward_on=开启转发模式\n',
    'forward_off=关闭转发模式\n',
    'cmd_add=添加命令\n',

    # 雨林干饭小助手
    'helper_name=小助手\n',

    # 其他
    'noticeboard=插件公告,插件公告板'
]


def create_template() -> None:
    """
    生成命令模板文件
    """
    if not Path(TEMPLATE_PATH).is_file():
        with open(TEMPLATE_PATH, 'a') as f:
            f.writelines(CMD_LIST)


def check_template() -> None:
    """
    命令模板校验函数,用于检测现有的模板命令是否符合标准

    """
    current_cmd = []
    original_cmd = []
    with open(TEMPLATE_PATH, 'r') as f:
        data = f.readlines()
    for i in data:
        current_cmd.append(i[0:i.rfind('=')])
    for i in CMD_LIST:
        original_cmd.append(i[0:i.rfind('=')])
    # 新增的命令
    new = set(original_cmd) - set(current_cmd)
    # 废弃的命令
    discard = set(current_cmd) - set(original_cmd)
    if new:
        # 若有新增的命令则：
        for cmd in list(new):
            for i in CMD_LIST:
                if cmd in i:
                    data.append(i)
                    logger.info(f'当前版本新增命令:{cmd}')
    if discard:
        # 若有废弃的命令则
        for cmd in list(discard):
            for i in data:
                if cmd in i:
                    data.remove(i)
                    logger.info(f'已移除过时的命令:{cmd}')
    if new or discard:
        # 将调整后的数据写入文件
        with open(TEMPLATE_PATH, 'w') as f:
            f.writelines(data)


def from_template_import() -> None:
    """
    从模板导入命令
    """
    with open(TEMPLATE_PATH, 'r') as f:
        lines = f.readlines()
    f = open(CONFIG_PATH, 'w')
    f.close()
    for line in lines:
        cmd = re.findall('^(.+)=', line)[0]
        aliases: str = re.findall('=(.+)', line)[0]
        aliases_list: list = aliases.split(',')
        content = json.dumps({cmd: aliases_list}) + "\n"
        with open(CONFIG_PATH, 'a') as cfg:
            cfg.write(content)
    logger.success('从模板导入命令成功')


def initialize() -> List[str]:
    """
    初始化全局命令
    """
    if not Path('Sky').is_dir():
        os.mkdir('Sky')
    if not Path(CONFIG_PATH).is_file():
        create_template()  # 初始化命令模板
        logger.success("命令配置初始化成功")
    check_template()  # 校验是否含有废弃命令或新增命令
    from_template_import()
    with open(CONFIG_PATH, 'r') as f:
        lines = f.readlines()
    logger.success(f'全局命令配置读取成功，{len(lines)} 个命令已加载')
    return lines


CmdList = initialize()  # 加载全局配置


def get_cmd_alias(cmd: str) -> set:
    """
    根据命令获取命令别名
    """
    for line in CmdList:
        cmd_json: dict = json.loads(line)
        if cmd_json.get(cmd):
            return set(cmd_json.get(cmd))
    else:
        return set()


async def add_cmd_aliases(
        cmd: str,
        alias: str
) -> bool:
    """
    添加命令别名
    """

    # with open(ConfigPath, 'r') as f:
    #     lines = f.readlines()
    # for line in lines:
    #     cmd_line: dict = json.loads(line)
    #     if cmd_line.get(cmd):
    #         index = lines.index(line)
    #         aliases: list = cmd_line.get(cmd)
    #         aliases.append(alias)
    #         line = json.dumps({cmd: aliases})
    #         lines[index] = line + '\n'
    #         with open(ConfigPath, 'w') as f:
    #             f.writelines(lines)
    #         logger.success(
    #             "命令别名添加成功，将在下次重启后生效"
    #         )
    #         break
    # else:
    #     logger.error("找不到命令")
    #     return False
    # return True
    with open(TEMPLATE_PATH, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if cmd in line:
            index = lines.index(line)
            lines[index] = line.strip('\n') + f',{alias}\n'
            with open(TEMPLATE_PATH, 'w') as f:
                f.writelines(lines)
            logger.success(
                "命令别名添加成功，将在下次重启后生效"
            )
            break
    else:
        logger.error('找不到命令')
        return False
    return True


AddCmdAliases = on_command('cmd -add', aliases=get_cmd_alias('cmd_add'))


@AddCmdAliases.handle()
async def add_cmd_aliases_handle(args: Message = EventPlainText()):
    msg = str(args)
    if not re.findall('cmd -add (.+) (.+)', msg):
        await AddCmdAliases.send(
            '您输入的命令格式有误。用法：\n'
            'cmd -add [cmd] [alias]'
        )
    else:
        cmd = re.findall('cmd -add (.+) (.+)', msg)[0][0]
        alias = re.findall('cmd -add (.+) (.+)', msg)[0][1]
        results = await add_cmd_aliases(cmd, alias)
        if results:
            await AddCmdAliases.send(
                f'命令 {cmd} 添加别名 {alias} 成功,将在下次重启后生效'
            )
        else:
            await AddCmdAliases.send(
                'Command not found：找不到命令'
            )


__all__ = (
    "add_cmd_aliases_handle",
    "get_cmd_alias",
    "initialize",
    "CmdList"
)
