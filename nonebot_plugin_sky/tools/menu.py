import os

from nonebot.adapters.onebot.v11 import MessageSegment


async def get_menu():
    abspath_ = os.path.abspath(__file__).strip('menu.py')
    path = abspath_ + 'helper_image/'
    menu = MessageSegment.image('file:///' + path + 'menu.png')
    return menu
