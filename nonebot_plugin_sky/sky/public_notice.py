import json

import httpx


async def get_notice():
    """获取官方公告"""
    url = 'https://ma75.update.netease.com/game_notice/announcement_live.json'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                      '/62.0.3202.9 Safari/537.36',
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=url,
            headers=headers)
        content = json.loads(response.text)
        notice = content['OtherChannelMessage']
        return notice
