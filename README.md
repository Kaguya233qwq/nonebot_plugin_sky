<div align="center">

<p align="center">
  <a href=""><img src="https://img1.baidu.com/it/u=3563761161,679242917&fm=253&fmt=auto&app=138&f=PNG?w=360&h=360" width="200" height="200" alt="kfc"></a>
</p>

# nonebot_plugin_sky

_✨ 基于 [NoneBot2](https://v2.nonebot.dev/) 的光遇每日攻略插件 ✨_

<p align="center">
  <img src="https://img.shields.io/github/license/EtherLeaF/nonebot-plugin-colab-novelai" alt="license">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/nonebot-2.0.0b4+-red.svg" alt="NoneBot">
  <a href="https://pypi.org/project/nonebot-plugin-sky/">
    <img src="https://badgen.net/pypi/v/nonebot-plugin-sky" alt="pypi">
  </a>
</p>
</div>

# 开始使用

1.使用pip包管理器安装(推荐)：

`pip install nonebot-plugin-sky`

或

2.克隆本项目到本地，在bot.py中导入插件：

`nonebot.load_plugin(r"nonebot_plugin_sky")`

# 使用命令

在有bot的群内发送`[命令前缀]+光遇`或`[命令前缀]+sky`来获取菜单

_当前版本包含的命令_：


| 命令                   | 说明                     |
| ------------------------ | -------------------------- |
| `sky`/`光遇`           | 获取菜单（列出指令列表） |
| `sky -cn`/`今日国服`   | 获取今日国服攻略         |
| `sky -in`/`今日国际服` | 获取近日国际服攻略       |
| `queue`/`排队`         | 获取服务器排队状态       |
| `notice`/`公告`        | 获取光遇国服官方公告     |

### **//【攻略数据来自微博@今天游离翻车了吗 @旧日与春】**

### **任何情况下攻略最后的版权信息请勿私自移除**

## TODO？

* [ ]  每日干饭提醒小助手
* [ ]  更多光遇攻略

# 效果展示

![](.README_images/test.jpg)

## **联系我**

<p align="center">
  <a href="https://github.com/"><img src="https://github.com/Kaguya233qwq/nonebot_plugin_alicdk_get/blob/main/.README_images/17623ac4.png?raw=true" width="300" height="350" alt="QRCode"></a>
</p>

## 更新日志

2022.11.18 v1.1.1

新增获取公告命令

2022.11.18 v1.1

1.重构项目结构

2.新增国际服今日攻略

3.新增排队人数查询

4.新增菜单命令

2022.11.14 v1.0.4

修复已知问题

2022.11.14 v1.0.3

修复当bot的昵称配置为空时获取的数据为空记录的问题

2022.11.14 v1.0.2

修复当游离未将今日攻略顶置时获取不到数据的问题

2022.11.5 v1.0.1

1.将结果用聊天记录转发的形式展现

2.修复已知问题

2022.11.3 v1.0

初推版本
