import json
from nonebot.adapters.onebot.v11 import MessageSegment


# 卡片已被和谐，必须破解token算法，暂时弃用

def card_group_bot(
        *args: str,
        title: str,
        prompt: str = "自定义消息"
) -> MessageSegment:
    """
    发送样式为“group_bot”的json卡片
    """
    fields_list = []
    for text in args:
        fields_list.append({"name": text})
    card = {
        "app": "com.tencent.bot.groupbot",
        "meta": {
            "embed": {
                "fields": fields_list,
                "title": title
            }},
        "prompt": prompt,
        "ver": "1.0.0.9",
        "view": "index"
    }
    return MessageSegment.json(json.dumps(card))
