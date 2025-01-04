import os
from pathlib import Path

from nonebot.adapters.onebot.v11 import MessageSegment


async def get_menu():
    path = Path(__file__.strip("menu.py")) / 'menu_image' /'menu.png'
    menu = MessageSegment.image(path.absolute().as_uri())
    return menu
