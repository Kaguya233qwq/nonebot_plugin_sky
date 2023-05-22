<div align="center">

<p align="center">
  <a href=""><img src="https://img1.baidu.com/it/u=3563761161,679242917&fm=253&fmt=auto&app=138&f=PNG?w=360&h=360" width="200" height="200" alt="sky"></a>
</p>

# nonebot_plugin_sky

_✨ 基于 [NoneBot2](https://v2.nonebot.dev/) 的光遇每日攻略插件 ✨_

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/nonebot-2.0.0b4+-red.svg" alt="NoneBot">
  <a href="https://pypi.org/project/nonebot-plugin-sky/">
    <img src="https://badgen.net/pypi/v/nonebot-plugin-sky" alt="pypi">
  </a>
</p>

_“因光而遇”_

</div>

# ✨安装与部署✨

##以下三种类型请选择适合自己的方案进行部署：

<details>

<summary>1.我从未接触过Nonebot框架</summary>

 如果你仅仅想简单部署一个光遇功能的机器人,
 不想太操心其他繁杂琐事的话，
 那么我推荐你加入我们的插件交流群获取：

【Nonebot+go-cqhttp集成光遇插件一键部署包】↓ ↓ ↓

<p align="center">
<img src="https://gitee.com/Kaguyaaa/nonebot_plugin_sky/raw/main/.README_images/group.png" width="200" height="350" alt="sky"></a>
</p>

</details>

<details>

<summary>2.我喜欢自己配置Nonebot框架</summary>

## 1.安装nonebot2框架及环境部署：

以下为Nonebot2环境配置基础，你需要对Nonebot2框架有一个足够的了解

这里只简单介绍步骤，新手教程推荐：

[Nonebot2文档](https://nb2.baka.icu/docs/start/installation)

[Nonebot2保姆级部署教程](https://www.bilibili.com/video/BV1aZ4y1f7e2)

执行`pip install nb-cli`

安装完就可以执行`nb create`命令来初始化项目模板文件。适配器请选择onebot-v11

之后根据文档中配置好env文件的地址、端口等内容

交互端推荐[go-cqhttp的rc3版本](https://github.com/Mrs4s/go-cqhttp/releases/v1.0.0-rc3)

（rc4版本存在无法发送图片的bug）

需要配置和nb一样的IP地址和端口

...


## 2.检查前置插件依赖：

### 一般情况下这个依赖是自动装好的

apscheduler:
[Github项目地址](https://github.com/nonebot/plugin-apscheduler)

或 使用nb-cli：

`nb plugin install nonebot_plugin_apscheduler`

## 3.配置bot.py文件，配置群号（雨林干饭小助手必要的，如果不配置会报错）

您必须确保您的bot.py配置中定时器默认关闭状态，即添加：

`nonebot.init(apscheduler_autostart=False)`

如果你不要求也可以忽略

在.env.xxx文件中配置接收小助手消息的群号，如果.env中ENVIRONMENT=prod,
则在.env.prod中添加以下内容：

`recv_group_id="12345"`(单个)

`recv_group_id=["12345","66666",...]`(多个)

### _**在新版的nonebot2中nb create命令默认不再生成bot.py文件，需要手动使用nb命令生成：**_

`nb` 选择 `生成机器人的入口文件`

## 4.安装本插件

1.使用nb插件管理器安装(**推荐**)：

先cd到你创建的项目文件夹内，再执行

`nb plugin install nonebot-plugin-sky`即可完成安装

或

2.克隆本项目到本地，在bot.py中导入插件：（不推荐 可忽略）

`nonebot.load_plugin(r"nonebot_plugin_sky")`

</details>

<details>

<summary>3.我是nonebot开发者/插件作者</summary>

### 1.使用nb-cli进行安装：

<code>~~ddl nb !~~</code>(划掉)

<code>nb plugin install nonebot-plugin-sky</code>

###2.以下操作是为了使干饭小助手正常运行：

您必须确保您的bot.py配置中定时器默认关闭状态，即添加：

`nonebot.init(apscheduler_autostart=False)`

在.env.xxx文件中配置接收小助手消息的群号:

`recv_group_id="12345"`(单个)

`recv_group_id=["12345","66666",...]`(多个)



</details>

# ✨命令列表✨

在有bot的群内发送`光遇菜单`或`sky`来获取菜单（遵循[命令前缀]）

<details>

<summary>当前最新版本包含的命令：</summary>

| 命令                    | 说明                            |
|-----------------------|-------------------------------|
| `sky`/`光遇菜单`          | 获取菜单（列出指令列表）                  |
| `sky -cn`/`今日国服`      | 获取今日国服攻略                      |
| `sky -in`/`今日国际服`     | 获取近日国际服攻略                     |
| `queue`/`排队`          | 获取服务器排队状态                     |
| `notice`/`公告`         | 获取光遇国服官方公告                    |
| `小助手启动`       | 启动定时任务并开启雨林干饭小助手              |
| `小助手关闭`       | 关闭定时任务并关闭雨林干饭小助手              |
| `小助手状态`       | 查询当前小助手运行状态                   |
| `return -cn`/`国服复刻`   | 查询最近的国服复刻先祖                   |
| `return -in`/`国际服复刻`  | 查询最近的国际服复刻先祖                  |
| `remain -cn`/`国服季节剩余` | 查询国服最新季节的剩余时间                 |
| `remain -in`/`国际服季节剩余` | 查询国际服最新季节的剩余时间                 |
| `开启/关闭转发模式`           | 开启和关闭全局消息转发形式                 |
| `开启/关闭艾特全体`           | 开启和关闭雨林干饭小助手的艾特全体消息           |
| `安装数据包`               | 安装光遇相关攻略的静态资源数据包              |
| `菜单v2`                | 查看数据包的文件名注入命令，这些命令都需要遵循命令前缀规则 |
| `插件公告`               | 获取插件官方公告                         |
| `check`/`检查更新`       | 检查插件、数据包版本是否有更新             |
| `光遇绑定+[原id]`        | 仅私聊模式有效，绑定光遇原id用于蜡烛查询    |
| `查询白蜡`               | 查询普通蜡烛的变化记录                    |
| `查询季蜡`               | 查询季节蜡烛的变化记录                    |
| `蜡烛`                  | 查询蜡烛总览                             |
| `更新插件`               | 检查插件更新进行升级操作                 |
| `光遇天气预报`/`sky天气`/`光遇天气` | 查询今日天气预报               |
| `活动日历`               | 查询活动日历                           |

</details>

### **任何情况下攻略最后的版权信息请勿私自移除**

**【攻略数据来自微博@今天游离翻车了吗 @旧日与春 @光遇陈陈和包包 @张张幼稚园】**

## 全局缓存目录：

Nonebot项目文件夹下的`sky/`目录

## --全局命令管理--

在2.2版本中引入了【全局命令管理】功能

以下是【全局命令模板】的路径：

`Sky/cmd_template.txt`

你可以在【全局命令模板】中自定义自己的命令，每次重启后都会自动导入生效，示例：

`menu=菜单,sky菜单`

## ✨★新版数据包说明★✨

在2.0版本中引入了光遇数据包（SkyDataPack）系统

### 特性：

1.数据包完全独立，与代码互相依存但互不干扰

2.安装后即可立即使用，无需重启NoneBot

3.支持自定义修改或扩充

<details>

<summary>使用说明</summary>

1.在群聊内或私聊bot发送`安装数据包`即可开始下载安装数据包

2.提示安装成功即可开始使用。发送命令`菜单v2`即可查看当前数据包内所有命令

3.自定义方法：数据包的安装路径为：你的Nonebot根目录下`的/SkyDataPack`文件夹

该文件夹的所有子文件夹即为‘命令’文件夹，每个‘命令’文件夹下的所有图片为命令成功执行需要发送的对象。

新建一个命令文件夹，命名为你想设置的命令语句，将要发送的图片对象放入此文件夹内即可。

空文件夹可能会报错，后续修复

***注意***：

1.命令只能为SkyDataPack文件夹内的文件夹，暂不支持子命令和更多极的文件夹

2.命令文件夹下目前只支持图片文件（jpg，png，bmp）

</details>


## ✨TODO？✨

* [X]  每日干饭提醒小助手
* [X]  更多光遇攻略
* [X]  数据包扩充
* [X]  命令管理器
* [ ]  光遇扩展插件
* [ ]  菜单生成器

# ✨效果展示✨

<p align="center">
<img src="https://gitee.com/Kaguyaaa/nonebot_plugin_sky/raw/main/.README_images/view.png" width="400" height="740" alt="sky"></a>
</p>

# ✨遇到问题✨

## 扫码加入我们的qq群，在线答疑解惑

(群文件有一键启动包)

<p align="center">
<img src="https://gitee.com/Kaguyaaa/nonebot_plugin_sky/raw/main/.README_images/group.png" width="200" height="350" alt="sky"></a>
</p>

## ✨感谢名单（不分先后）✨

新浪微博@光遇陈陈和包包 —> *攻略内容*

新浪微博@旧日与春 —> *攻略内容*

新浪微博@今天游离翻车了吗 —> *攻略内容*

新浪微博@张张幼稚园 —> *攻略内容*

新浪微博&哔哩哔哩@木易不高兴了啊 —> *攻略内容*

## ✨更新日志✨

2023.5.22 v2.2.8

【修复中】复刻问题正在修复

2023.4.30 v2.2.7

1.在这个版本之后所有querytools命令均废弃不再生效。

2.更新季节时间（暂时不是很准确

2023.4.25 v2.2.6

1.修复获取uid帮助图片无法发送的问题

2.当处于季节真空期时查询季蜡、蜡烛数返回相应提示

2023.4.12 v2.2.5.post2

修复已知问题

2023.4.4 v2.2.5.post1

修复插件公告镜像源地址

2023.4.4 v2.2.5

1.修复国际服任务获取不到的问题

2.修复复刻相关问题

3.现在图片发送不再受go-cqhttp版本的影响

4.复刻兑换图不再使用转发消息模式

2023.3.23 v2.2.4

修复已知问题，更换项目的gitee镜像仓库

2023.3.21 v2.2.3

修复已知的问题

2023.3.7 v2.2.2

光遇陈陈因工作忙没有时间更新，

更换复刻数据源为微博@光遇包包1号

2023.3.2 v2.2.1

1.修复光遇官方公告与插件公告冲突问题

2.修复添加指令命令死循环问题

3.修复lxml警告问题

4.蜡烛查询增加对应异常捕获处理

<details>

<summary>更早的记录（2023.3.1之前）</summary>

2023.3.1 v2.2

1.新增全局自定义命令管理器，支持了99%的命令（只有定时器命令暂时无法自定义）

2.使大部分命令都适配了私聊场景

3.优化更新插件的手感（什）

4.修改文档内图片为gitee镜像源

5.重构部分文件结构

6.一些简单的工具类代码块优化

2023.2.24 v2.1.2

1.修复id绑定IO读写问题，增加禁止重复绑定的逻辑

2.适配多人id绑定

3.修复国服季节剩余时间问题，新增国际服剩余命令

2023.2.24 v2.1.1

1.修复绑定id、查询天气和活动日历时特定条件下触发的bug

2.修复配置文件加载的bug，及初次初始化转发消息失效的问题

2023.2.24 v2.1

1.增加时间点判断逻辑，全面提升复刻匹配准确度

2.重构配置文件路径到Sky文件夹下方便统一管理

3.蜡烛查询全面重写，升级为官方接口，命令无变化

4.新增天气预报、活动日历命令，同蜡烛查询系列命令一样需绑定光遇uid

5.简化完善了文档说明，使用户有更佳的选择与体验

6.修复版本号问题

7.其他优化处理

2023.2.21 v2.0.11.post1

修复已知问题

2023.2.20 v2.0.11

1.增加 “更新插件”命令，更新后需要重启

2.增加若干__all__声明

3.json卡片因被和谐暂时弃用

2023.2.18 v2.0.10

1.修复了国服复刻和国际服复刻（大概是最后一次）

2.将插件公告源换为Gitee镜像源

3.将数据包检查更新与下载源换为Gitee镜像源

4.修复了lxml依赖问题

2023.2.16 v2.0.9

1.新增蜡烛查询三个命令，及绑定i的d命令

2.修正消息转发的注解类型

2023.2.1 v2.0.8.post1

修复国际服复刻匹配错误

2023.1.29 v2.0.8

1.修复和优化了国服复刻和国际服复刻的匹配准确度

2.数据包下载增加异常捕获和错误日志

2023.1.28 v2.0.7

1.修复当国际服复刻信息为视频内容不能匹配的问题

2.修复木易的国服复刻信息的匹配问题

3.更新追忆季季节倒计时查询

4.修复数据包安装时不能正确删除旧版的问题

5.新增 检查更新的命令

6.数据包更新到1.0.1春节版本

2023.1.19 v2.0.6.post3

1.更换国服复刻数据源为微博@木易不高兴了啊

2.修复国际服复刻的匹配问题

2023.1.10 v2.0.6.post1

紧急修复版本：

1.修复国服复刻匹配问题

2.修正插件公告的行扫描

2023.1.9 v2.0.6

修复主菜单命令与数据包命令冲突问题

2023.1.9 v2.0.4

1.修复了上个版本数据包命令失效问题

2.新增：“插件公告”命令，可获取插件官方的公告

3.修复国服季节剩余命令导包问题

2023.1.2 v2.0.3

1.新增国际服复刻

2.修复数据包中发送无关命令仍会报错的问题

3.修复文件无法删除拒绝访问的问题

4.补充部分命令匹配

5.修改数据包命令为精准匹配而不是模糊匹配

6.修改菜单图路径

2022.12.30 v2.0.2

适配linux端

2022.12.30 v2.0.1

1.修复数据包菜单重复追加的问题

2.菜单升级为图片版

2022.12.30 v2.0

新增数据包系统，拥有较好扩展性，支持自定义

2022.12.22 v1.2.10

1.更换国服复刻先祖的数据源

2.小助手支持多个群异步发送定时消息

2022.12.12 v1.2.9

修改国服复刻先祖的数据源

2022.12.10 v1.2.8

新增小助手艾特全体开关

2022.12.5 v1.2.7

修复setups文件及打包

2022.12.5 v1.2.6

新增配置文件，新增全局消息转发配置，支持命令开关

2022 12.3 v1.2.5

修复雨林干饭小助手linux环境下的路径识别问题。

2022 12.2 v1.2.4

修复复刻先祖的搜索逻辑

2022 12.2 v1.2.3

新增国服复刻先祖查询

2022 11.28 v1.2.2

移除小助手时间测试脏数据

2022 11.27 v1.2.1

修复雨林干饭小助手无法发送到群的问题

2022 11.22 v1.2.0

新增雨林干饭小助手（国服时间，国际服暂不考虑）开启后每到饭点提前五分钟自动提醒

2022 11.21 v1.1.5

取消消息转发机制规避部分账号风控问题

2022 11.19 v1.1.4

修复pypi打包不全问题

2022 11.18 v1.1.3

修复国际服攻略解析失败的问题

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

</code></pre>

</details>

## 已通过墨菲安全检测：

[![Security Status](https://www.murphysec.com/platform3/v3/badge/1614390303725748224.svg?t=1)](https://www.murphysec.com/accept?code=42caa007865facda50ed119894201320&type=1&from=2&t=2)

