from nonebot import on_command, logger

from ..config.load_config import get_config as config
from ..config.load_config import cfg_path

cfg_path_ = cfg_path()


def get_cache_state():
    try:
        value = config().getboolean('Travelling', 'cache')
        return value
    except Exception as e:
        str(e)


def cache_on():
    global cfg_path_
    config().set('Travelling', 'cache', 'True')

    config().write(open(cfg_path_, 'w+'))
    logger.success('先祖复刻缓存已开启')


def cache_off():
    global cfg_path_
    config().set('Travelling', 'cache', 'False')

    config().write(open(cfg_path_, 'w+'))
    logger.success('先祖复刻缓存已关闭')


Cache = get_cache_state()

CacheOn = on_command("开启复刻缓存")
CacheOff = on_command("关闭复刻缓存")


@CacheOn.handle()
async def cache_on_handle():
    try:
        global Cache
        cache_on()
        await CacheOn.send('复刻缓存开启成功')
        Cache = get_cache_state()

    except Exception as e:
        logger.error('复刻缓存开启失败')
        await CacheOn.send('开启失败！原因：%s' % str(e))


@CacheOff.handle()
async def cache_off_handle():
    try:
        global Cache
        cache_off()
        await CacheOff.send('复刻缓存关闭成功')
        Cache = get_cache_state()

    except Exception as e:
        logger.error('复刻缓存关闭失败')
        await CacheOff.send('开启失败！原因：%s' % str(e))


def is_cache():
    return Cache
