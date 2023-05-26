import datetime
import os

import httpx
from nonebot import logger


class NormalTravel(object):
    """
    通常复刻周期函数 类
    """
    def travel_status(self, date: str) -> dict:
        """
        - 获取最近一次通常旅行先祖公布的时间点
        - return: dict{
            status :bool 是否在复刻周期内
            current_release: str 本次复刻公布的时间
            coming_at: str 本次复刻先祖到来时间
            leaves_at: str 本次复刻先祖离开时间
            next_release: str 下次复刻公布的时间
        }
        """
        start = date  # 之前任意一个复刻先祖公布的时间点
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date_start = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S").date()
        date_now = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S").date()
        margin_days = (date_now - date_start).days
        if margin_days >= 14:
            change = -(margin_days % 14)
        else:
            change = -margin_days
        results = datetime.datetime.now() + datetime.timedelta(days=change)
        #  判断当前时间是否在复刻期间
        coming_at = (results + datetime.timedelta(days=2)).strftime('%Y-%m-%d')
        leaves_at = (results + datetime.timedelta(days=6)).strftime('%Y-%m-%d')
        next_at = (results + datetime.timedelta(days=14)).strftime('%Y-%m-%d')
        if now < leaves_at:
            current_travel = results.strftime('%Y-%m-%d')
            return {
                'status': True,
                'current_release': f'{current_travel} 12:00:00',
                'coming_at': f'{coming_at} 06:00:00',
                'leaves_at': f'{leaves_at} 12:00:00'
            }
        else:
            return {
                'status': False,
                'next_release': f'{next_at} 12:00:00'
            }  # 这么写有点不太pydantic

    def national(self):
        """
        国服
        """
        status = self.travel_status()


class ExtraTravel(object):
    """
    加载复刻类 （逻辑过于复杂，暂时咕了）
    """


def download_img(img_url: str, file_name: str):
    """
    下载复刻图片到本地
    """
    try:
        path = f'Sky/TravelCache/{file_name}.jpg'
        async with httpx.AsyncClient() as client:
            res = await client.get(
                url=img_url
            ).content
        with open(path, 'wb') as f:
            f.write(res)
        logger.success('复刻先祖图片保存成功')
    except Exception as e:
        e.__str__()
        logger.error('下载图片失败')


def is_exist(file_name: str):
    """
    本地是否存在复刻缓存
    :return:
    """
    path = f'Sky/TravelCache/{file_name}.jpg'
    if os.path.isdir(path):
        abs_path = os.path.abspath(path)
        return f'file:///{abs_path}'
    return False
