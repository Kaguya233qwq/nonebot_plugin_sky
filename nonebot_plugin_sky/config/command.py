import os
import json
import re
from pathlib import Path

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import EventPlainText

ConfigPath = 'Sky/cmd_setting.cfg'
TemplatePath = 'Sky/cmd_template.txt'
CmdList = []


def initialize():
    """
    初始化全局命令
    """
    global CmdList
    if not Path('Sky').is_dir():
        os.mkdir('Sky')
    if not Path(ConfigPath).is_file():
        create_template()
        from_template_import()
        logger.success("命令配置初始化成功")
    else:
        from_template_import()
        with open(ConfigPath, 'r') as f:
            lines = f.readlines()
        CmdList = lines
        logger.success('全局命令配置读取成功')


def create_template():
    """
    生成命令模板文件
    """
    if not Path(TemplatePath).is_file():
        with open(TemplatePath, 'a') as f:
            f.write(
                # 主要命令
                'menu=光遇菜单,sky菜单\n'
                'sky_cn=今日国服\n'
                'sky_in=今日国际服\n'
                'travel_cn=国服复刻\n'
                'travel_in=国际服复刻\n'
                'remain_cn=国服季节剩余\n'
                'remain_in=国际服季节剩余\n'
                'queue=排队\n'
                'notice=公告\n'

                # 蜡烛查询命令
                'save_id=光遇绑定\n'
                'qw=查询白蜡\n'
                'qs=查询季蜡\n'
                'qa=蜡烛,我的蜡烛\n'
                'sky_weather=光遇天气预报,sky天气,光遇天气\n'
                'sky_activities=活动日历,精灵日历\n'

                # 配置命令
                'cmd_add=添加命令\n'
                'cmd_import=导入命令\n'
            )
        logger.success('命令模板生成成功')


def from_template_import():
    """
    从模板导入命令
    """
    with open(TemplatePath, 'r') as f:
        lines = f.readlines()
    f = open(ConfigPath, 'w')
    f.close()
    for line in lines:
        cmd = re.findall('^(.+)=', line)[0]
        aliases: str = re.findall('=(.+)', line)[0]
        aliases_list: list = aliases.split(',')
        content = json.dumps({cmd: aliases_list}) + "\n"
        with open(ConfigPath, 'a') as cfg:
            cfg.write(content)
    logger.success('导入成功')


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
):
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
    with open(TemplatePath, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if cmd in line:
            index = lines.index(line)
            lines[index] = line.strip('\n') + f',{alias}\n'
            with open(TemplatePath, 'w') as f:
                f.writelines(lines)
            logger.success(
                "命令别名添加成功，将在下次重启后生效"
            )
            break
    else:
        logger.error('找不到命令')
        return False
    return True


AddCmdAliases = on_command('cmd -add', aliases={'添加命令'})


@AddCmdAliases.handle()
async def add_cmd_aliases_handle(args: Message = EventPlainText()):
    msg = str(args)
    if not re.findall('cmd -add (.+) (.+)', msg):
        await AddCmdAliases.reject(
            '您输入的命令格式有误。用法：\n'
            'cmd -add [cmd] [alias]'
        )
    else:
        print(re.findall('cmd -add (.+) (.+)', msg))
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
    "initialize"
)
