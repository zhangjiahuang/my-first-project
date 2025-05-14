import PyInstaller.__main__
import os
import sys


# 获取 youtube-dl 的安装路径
# youtube_dl_path = os.path.dirname(youtube_dl.__file__)

PyInstaller.__main__.run([
    'youtube_dl_gui.py',
    '--name=YouTube-DL-GUI',
    '--onefile',
    '--windowed',
    '--icon=C:\\Users\\zhang-jiahuang\\Downloads\\dl.png',  # 如果您有图标文件，请指定路径
    # '--add-data=LICENSE;.',  # 如果有许可证文件
    # 在build.py中添加
    '--add-binary=C:\\Users\\zhang-jiahuang\\yt-dlp.exe;.',
    '--hidden-import=PyQt5',
    # 不再需要 '--hidden-import=youtube_dl',
    # 如果您的程序中使用了 youtube_dl 模块，而不仅仅是调用可执行文件，则仍需保留
    # f'--add-data={youtube_dl_path};youtube_dl',  # 添加 youtube-dl 库文件
    # '--collect-all=youtube_dl',  # 收集所有 youtube-dl 相关文件
])