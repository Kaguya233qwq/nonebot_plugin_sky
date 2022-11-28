import setuptools
import os


def get_files(path):
    """获取路径下所有文件相对路径"""
    file_list = []
    files = os.listdir(path)
    for file in files:
        file_list.append(path + '/' + file)
    print(file_list)
    return file_list


Files = get_files(r'nonebot_plugin_sky/tools/image')

with open("README.md", "r", encoding="utf-8", errors="ignore") as f:
    long_description = f.read()
setuptools.setup(
    name='nonebot-plugin-sky',
    version='1.2.2',
    author='Kaguya233qwq',
    author_email='1435608435@qq.com',
    keywords=["pip", "nonebot2", "nonebot", "sky光遇", "光遇"],
    url='https://github.com/Kaguya233qwq/nonebot_plugin_sky',
    description='''nonebot2 plugin sky''',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=[
        'nonebot_plugin_sky',
        'nonebot_plugin_sky.utils_',
        'nonebot_plugin_sky.sky',
        'nonebot_plugin_sky.tools'
    ],
    data_files=Files,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: Chinese (Simplified)"
    ],
    include_package_data=True,
    platforms="any",
    install_requires=[
        'httpx', 'nonebot2>=2.0.0-beta.1', 'nonebot-adapter-onebot>=2.0.0-beta.1', 'nonebot_plugin_apscheduler'
    ])
