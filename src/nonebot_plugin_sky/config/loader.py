import configparser
import os
from pathlib import Path
from . import Config

from nonebot import logger


def reset_config() -> None:
    """
    恢复默认配置
    """
    Config.CONFIG_FILE.unlink()
    load_config()
    logger.success("已恢复默认配置")


def load_config() -> configparser.ConfigParser:
    """
    载入配置项及初始化
    """
    if not Path(Config.SKY_ROOT_PATH).is_dir():
        os.mkdir(Config.SKY_ROOT_PATH)
    path = Config.CONFIG_FILE
    conf = configparser.ConfigParser()
    if not path.is_file():
        # 这里编写需要初始化的配置项
        conf.add_section("Message")
        conf.add_section("Helper")
        conf.add_section("Travelling")
        conf.set("Message", "forward", "True")
        conf.set("Helper", "at_all", "False")
        conf.set("Travelling", "cache", "True")

        setting = open(path, "a")
        conf.write(setting)
        setting.close()
        logger.success("配置文件初始化成功")

    conf.read(path, encoding="utf-8")
    return conf


CONFIG = load_config()
logger.success("读取配置成功")


def loaded_config():
    return CONFIG


def save_to_config(*args) -> None:
    """
    设置配置项
    """
    try:
        loaded_config().set(*args)
        loaded_config().write(open(Config.CONFIG_FILE, "w+"))
    except Exception as e:
        logger.error("配置文件写入失败！原因：%s" % str(e))


__all__ = ("load_config", "loaded_config", "CONFIG")
