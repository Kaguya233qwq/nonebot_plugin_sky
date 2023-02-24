from datetime import datetime


def time_no_more(date, hour, minute):
    """
    UTC时间判断工具
    """
    time_obj = datetime.strptime(date, '%a %b %d %H:%M:%S +0800 %Y')
    if time_obj.hour == hour and time_obj.minute <= minute:
        return True
    else:
        return False


if __name__ == '__main__':
    date_ = 'Tue Feb 21 12:02:10 +0800 2023'
    print(time_no_more(date_, 12, 10))
