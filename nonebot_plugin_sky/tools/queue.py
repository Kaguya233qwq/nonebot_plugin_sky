import json

import httpx


async def get_state():
    """获取排队状态"""
    url = 'https://live-queue-sky-merge.game.163.com/queue'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                      '/62.0.3202.9 Safari/537.36',
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=url,
            headers=headers)
        if response.status_code != 200:
            return '服务器返回状态码异常'
        content = json.loads(response.text)
        state = content['text']
        if 'enter' in state:
            return '当前服务器畅通，无需排队'
        elif 'queue' in state:
            wait_time = content['wait_time']
            players = content['pos']
            return '当前排队人数：' + str(players) + \
                '\n预计排队时间：' + str(wait_time)
        else:
            return '服务器又炸啦！'  # 破土豆服务器（
