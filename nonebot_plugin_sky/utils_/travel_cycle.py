import datetime
import os
import random


class NormalTravel:
    """
    通常复刻周期函数 类
    """

    @staticmethod
    def __travel_status(date: str) -> dict:
        """
        获取最近一次通常旅行先祖公布的时间点

        - date: 之前任意一个复刻先祖公布的时间点
        返回: dict :
            - status :bool 是否在复刻周期内
            - current_release: str 本次复刻公布的时间
            - coming_at: str 本次复刻先祖到来时间
            - leaves_at: str 本次复刻先祖离开时间
            - next_release: str 下次复刻公布的时间

        """
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date_start = datetime.datetime.strptime(
            date,
            "%Y-%m-%d %H:%M:%S"
        ).date()
        date_now = datetime.datetime.strptime(
            now, "%Y-%m-%d %H:%M:%S"
        ).date()
        margin_days = (date_now - date_start).days
        if margin_days >= 14:
            change = -(margin_days % 14)
        else:
            change = -margin_days
        results = datetime.datetime.now() + datetime.timedelta(days=change)
        #  判断当前时间是否在复刻期间
        coming_at = (
                results + datetime.timedelta(days=2)
        ).strftime('%Y-%m-%d 06:00:00')
        leaves_at = (
                results + datetime.timedelta(days=6)
        ).strftime('%Y-%m-%d 12:00:00')
        next_at = (
                results + datetime.timedelta(days=14)
        ).strftime('%Y-%m-%d 12:00:00')
        if now < leaves_at:
            current_travel = results.strftime('%Y-%m-%d 12:00:00')
            return {
                'status': True,
                'current_release': f'{current_travel}',
                'coming_at': f'{coming_at}',
                'leaves_at': f'{leaves_at}'
            }
        else:
            return {
                'status': False,
                'next_release': f'{next_at}'
            }  # 这么写有点不太pythonic

    def national(self) -> dict:
        """
        国服通常复刻周期计算函数
        """
        status = self.__travel_status('2023-05-16 12:00:00')
        return status

    # def international(self):
    #     """
    #     国际服 国际服的时间比较混乱，暂时没有好的解决方案
    #     :return:
    #     """
    #     status = self.__travel_status('2023-05-10 2:00:00')
    #     return status


class ExtraTravel(object):
    """
    加塞复刻类 （这个逻辑目前还不知怎么写，暂时咕了）
    """


def is_exist(file_name: str):
    """
    本地是否存在复刻缓存
    :return:
    """
    path = f'Sky/Cache/{file_name}.jpg'
    if os.path.isfile(path):
        abs_path = os.path.abspath(path)
        return f'file:///{abs_path}'
    return False


def bot_tips(struct: dict) -> str:
    """
    根据传入的dict自动生成温馨提示语
    """
    if struct.get('status') is True:
        coming_at = struct.get('coming_at')
        leaves_at = struct.get('leaves_at')
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if now < coming_at:
            now = datetime.datetime.strptime(
                now,
                "%Y-%m-%d %H:%M:%S"
            ).timestamp()
            coming_at = datetime.datetime.strptime(
                coming_at,
                "%Y-%m-%d %H:%M:%S"
            ).timestamp()
            days = (coming_at - now)/60/60/24
            if days < 1:
                tips = [
                    f'还有{days}天先祖就来了哦,请耐心等待',
                    f'先祖已经在赶来的路上啦，还有{days}天',
                    f'我知道你很急但你先别急，再等{days}天先祖就来啦'
                ]
                return random.choice(tips)
            else:
                return '先祖明天就来啦，今晚安心睡个好觉吧！'
        elif coming_at < now < leaves_at:
            now = datetime.datetime.strptime(
                now,
                "%Y-%m-%d %H:%M:%S"
            ).timestamp()
            leaves_at = datetime.datetime.strptime(
                leaves_at,
                "%Y-%m-%d %H:%M:%S"
            ).timestamp()
            days = (leaves_at - now) / 60 / 60 / 24
            hours = (leaves_at - now) / 60 / 60
            if days > 1:
                return f'距离先祖离去还有{days}天'
            else:
                heads = f'距离先祖离去害有%.1f小时\n' % hours
                tips = [
                    f'{heads}先祖就要离开了，他会想你们的！',
                    f'{heads}本次旅行先祖即将离去，请各位想要兑换的旅人及时兑换',
                    f'{heads}复刻临近尾声，结束是新的开始',
                    f'{heads}这个老东西总算要走了！.....咳咳'
                ]
                return random.choice(tips)
    else:
        tips = [
            f'下次会是什么呢？很期待哦',
            f'希望国服不要再让我们捡破烂了',
            f'风平浪静，没有任何事情发生。',
            f'武士裤复刻全是我的功劳！',
            f'时间还长着呢，先看看书吧',
            f'我认为作者是个大天才。',
            f'和朋友在一起玩的时间越来越少了。相遇不易，希望各位旅人能珍惜',
            f'这年头谁还跑图啊',
            f'昨天少拿一根季蜡，好亏',
            f'当初带你入坑光遇的那个人，ta还好吗？',
            f'请不要忘记，那天陪你一起看的景色',
            f'我们都曾拥有，我们从未失去',
            f'LightCute什么时候开源？',
            f'啥？这游戏不是单机游戏吗？那些小黑不是npc吗？'
        ]
        bonus_tips = [
            f"不会吧不会吧，不会真有人为了看我说什么在这一直发吧",
            f'不是，你指望着我一个光遇插件给你讲笑话听吗',
            f'好玩吗?',
            f'你猜猜我下次会说什么'
        ]
        extra_tips = f"恭喜你中了大奖。我发送这段文字的概率只有1%，快去买彩票吧= ="
        choice = random.randint(0, 99)
        if choice == 0:
            return extra_tips
        elif 1 <= choice <= 5:
            return random.choice(bonus_tips)
        else:
            return random.choice(tips)
