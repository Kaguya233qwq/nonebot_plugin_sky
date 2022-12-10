from pathlib import Path
import os
import configparser

from nonebot import logger


def get_path():
    cur_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(cur_path, "config.ini")
    return path


def load():
    cfg_path = get_path()
    conf = configparser.ConfigParser()
    if not Path(cfg_path).is_file():

        # 这里编写需要初始化的配置项
        conf.add_section('Message')
        conf.add_section('Helper')
        conf.set('Message', 'forward', 'True')
        conf.set('Helper', 'at_all', 'True')

        conf.write(open(cfg_path, 'a'))
        logger.success('配置文件初始化成功')
    else:
        conf.read(cfg_path, encoding="utf-8")
        return conf


CONFIG = load()
logger.success('读取配置成功')


def get_config():
    return CONFIG
