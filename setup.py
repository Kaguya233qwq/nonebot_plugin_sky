import os

import setuptools


def get_files(path) -> list:
    """获取路径下所有文件相对路径"""
    file_list = []
    files = os.listdir(path)
    for file in files:
        file_list.append(path + '/' + file)
    file_list.append('nonebot_plugin_sky/tools/menu_image/menu.png')
    return file_list


Files = get_files(r'nonebot_plugin_sky/tools/helper_image')

with open("README.md", "r", encoding="utf-8", errors="ignore") as f:
    long_description = f.read()
setuptools.setup(
    name='nonebot-plugin-sky',
    version='v2.2.11.post3',
    author='Kaguya233qwq',
    author_email='1435608435@qq.com',
    keywords=["pip", "nonebot2", "nonebot", "sky光遇", "光遇"],
    url='https://github.com/Kaguya233qwq/nonebot_plugin_sky',
    description='''nonebot2 plugin sky''',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    data_files=Files,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: Chinese (Simplified)"
    ],
    include_package_data=True,
    platforms="any",
    install_requires=[
        "bs4", 'lxml', 'httpx', 'nonebot2>=2.0.0', 'nonebot-adapter-onebot>=2.0.0-beta.1',
        'nonebot_plugin_apscheduler', 'pydantic'
    ])
