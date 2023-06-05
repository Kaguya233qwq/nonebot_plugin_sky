import configparser
import os
from pathlib import Path

from nonebot import logger


def cfg_path() -> str:
    path = 'Sky/config.ini'
    return path


def reset_config() -> None:
    """
    恢复默认配置
    """
    cfg_path_ = cfg_path()
    os.remove(cfg_path_)
    load()
    logger.success('已恢复默认配置')


def load() -> dict:
    """
    载入配置项及初始化
    """
    if not Path('Sky').is_dir():
        os.mkdir('Sky')
    cfg_path_ = cfg_path()
    conf = configparser.ConfigParser()
    if not Path(cfg_path_).is_file():
        # 这里编写需要初始化的配置项
        conf.add_section('Message')
        conf.add_section('Helper')
        conf.add_section('Travelling')
        conf.set('Message', 'forward', 'True')
        conf.set('Helper', 'at_all', 'False')
        conf.set('Travelling', 'cache', 'True')

        setting = open(cfg_path_, 'a')
        conf.write(setting)
        setting.close()
        logger.success('配置文件初始化成功')

    conf.read(cfg_path_, encoding="utf-8")
    return conf


CONFIG = load()
logger.success('读取配置成功')


def get_config():
    return CONFIG


__all__ = (
    "cfg_path",
    "load",
    "get_config",
    "CONFIG"
)
