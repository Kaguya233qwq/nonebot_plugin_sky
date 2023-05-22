import datetime


class NormalTravel(object):
    """
    通常复刻类
    """

    @staticmethod
    def travel_status():
        """
        获取最近一次通常旅行先祖公布的时间点
        :return:
        """
        start = '2023-05-02 12:00:00'  # 之前任意一个复刻先祖公布的时间点
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
            }


class ExtraTravel(object):
    """
    加载复刻类 （逻辑过于复杂，暂时咕了）
    """
