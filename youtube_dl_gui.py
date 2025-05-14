import sys
import os
import subprocess
import json
import configparser
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QProgressBar, QComboBox, 
                            QCheckBox, QFileDialog, QTabWidget, QTextEdit, QGroupBox,
                            QRadioButton, QButtonGroup, QMessageBox, QSpinBox, QDialog,
                            QScrollArea, QToolTip, QMenu, QAction)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QProcess
from PyQt5.QtGui import QCursor

file_path = os.path.dirname(os.path.abspath(__file__))
# 添加获取应用程序路径的函数
def get_application_path():
    """获取应用程序路径，兼容打包后的环境"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的应用程序
        return os.path.dirname(sys.executable)
    else:
        # 如果是开发环境
        return os.path.dirname(os.path.abspath(__file__))

class HelpDialog(QDialog):
    """帮助对话框，显示参数说明"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("YouTube-DL 参数帮助")
        self.setGeometry(200, 200, 600, 500)
        
        layout = QVBoxLayout()
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 创建内容控件
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # 添加帮助内容
        help_text = """
<h2>YouTube-DL 常用参数说明</h2>

<h3>基本选项</h3>
<p><b>-f, --format FORMAT</b>: 指定下载的文件格式，例如 "best", "bestvideo+bestaudio" 等</p>
<p><b>-o, --output TEMPLATE</b>: 指定输出文件名模板，例如 "%(title)s-%(id)s.%(ext)s"</p>
<p><b>-x, --extract-audio</b>: 提取音频</p>
<p><b>--audio-format FORMAT</b>: 指定音频格式，例如 "mp3", "m4a", "wav" 等</p>
<p><b>--audio-quality QUALITY</b>: 指定音频质量，例如 "0"(最佳), "5"(中等), "9"(最差)</p>

<h3>字幕选项</h3>
<p><b>--write-sub</b>: 下载字幕</p>
<p><b>--write-auto-sub</b>: 下载自动生成的字幕</p>
<p><b>--all-subs</b>: 下载所有可用字幕</p>
<p><b>--sub-lang LANGS</b>: 指定字幕语言，例如 "en,zh-CN"</p>

<h3>播放列表选项</h3>
<p><b>--yes-playlist</b>: 下载整个播放列表</p>
<p><b>--no-playlist</b>: 不下载播放列表，即使URL指向播放列表</p>
<p><b>--playlist-items ITEM_SPEC</b>: 指定播放列表项目范围，例如 "1-3,7,10-13"</p>

<h3>代理和网络选项</h3>
<p><b>--proxy URL</b>: 使用代理</p>
<p><b>--socket-timeout SECONDS</b>: 设置网络超时时间</p>
<p><b>--limit-rate RATE</b>: 限制下载速度，例如 "50K" 或 "4.2M"</p>

<h3>文件系统选项</h3>
<p><b>--no-overwrites</b>: 不覆盖已存在的文件</p>
<p><b>--continue</b>: 断点续传，继续下载部分下载的文件</p>
<p><b>--no-mtime</b>: 不使用Last-modified header设置文件修改时间</p>

<h3>元数据选项</h3>
<p><b>--add-metadata</b>: 将元数据写入下载的文件</p>
<p><b>--embed-thumbnail</b>: 将缩略图嵌入音频文件</p>
<p><b>--embed-subs</b>: 将字幕嵌入视频文件</p>

<h3>后处理选项</h3>
<p><b>--merge-output-format FORMAT</b>: 指定合并后的输出格式，例如 "mp4", "mkv", "ogg", "webm", "flv"</p>
<p><b>--recode-video FORMAT</b>: 重新编码视频为指定格式</p>

<h3>其他选项</h3>
<p><b>--ignore-errors</b>: 忽略错误，继续下载播放列表中的其他视频</p>
<p><b>--download-archive FILE</b>: 记录已下载的视频ID</p>
<p><b>--write-description</b>: 将视频描述写入文件</p>
<p><b>--write-info-json</b>: 将视频元数据写入JSON文件</p>
<p><b>--cookies FILE</b>: 指定cookies文件，用于需要登录的网站</p>
<p><b>--user-agent UA</b>: 指定用户代理</p>
<p><b>--referer URL</b>: 指定referer，某些网站需要</p>
<p><b>--geo-bypass</b>: 绕过地理限制</p>
"""
        
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setTextFormat(Qt.RichText)
        content_layout.addWidget(help_label)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        self.setLayout(layout)


class AboutDialog(QDialog):
    """关于对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于 YouTube-DL GUI")
        self.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        about_text = """
<h2>YouTube-DL 图形界面</h2>
<p>版本: 1.0.0</p>
<p>这是一个基于 YouTube-DL 命令行工具的图形界面，使用 PyQt5 开发。</p>
<p>YouTube-DL 是一个功能强大的视频下载工具，支持多个视频网站。</p>
<p>本程序提供了友好的图形界面，让用户可以轻松使用 YouTube-DL 的各种功能。</p>
<p><a href="https://github.com/ytdl-org/youtube-dl">YouTube-DL 官方网站</a></p>
"""
        
        about_label = QLabel(about_text)
        about_label.setWordWrap(True)
        about_label.setTextFormat(Qt.RichText)
        about_label.setOpenExternalLinks(True)
        layout.addWidget(about_label)
        
        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        self.setLayout(layout)


class DownloadThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    progress_percent_signal = pyqtSignal(int)
    
    def __init__(self, command):
        super().__init__()
        self.command = command
        
    def run(self):
        try:
            process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            for line in iter(process.stdout.readline, ''):
                self.progress_signal.emit(line.strip())
                
                # 解析进度信息
                self.parse_progress(line)
            
            process.stdout.close()
            return_code = process.wait()
            
            if return_code == 0:
                self.finished_signal.emit(True, "下载完成！")
            else:
                self.finished_signal.emit(False, f"下载失败，错误代码: {return_code}")
                
        except Exception as e:
            self.finished_signal.emit(False, f"发生错误: {str(e)}")
            
    def parse_progress(self, line):
        """解析youtube-dl的进度输出，更新进度条"""
        # 匹配下载百分比
        percent_match = re.search(r'(\d+\.\d+)%', line)
        if percent_match:
            try:
                percent = float(percent_match.group(1))
                self.progress_percent_signal.emit(int(percent))
            except (ValueError, IndexError):
                pass


class YouTubeDLGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setToolTips()
        self.config_file = os.path.join(os.path.expanduser("~"), ".youtube_dl_gui.ini")
        
        # 检查youtube-dl是否已安装
        if not self.check_youtube_dl():
            QMessageBox.warning(self, "警告", "未检测到youtube-dl。请确保已安装youtube-dl并添加到系统PATH中。")
        
    def initUI(self):
        self.setWindowTitle('YouTube-DL 图形界面')
        self.setGeometry(100, 100, 800, 600)
        
        # 主布局
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10) # 设置主布局的边距
        main_layout.setSpacing(10) # 设置主布局中控件的间距
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 创建菜单栏
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        save_config_action = QAction('保存配置', self)
        save_config_action.triggered.connect(self.saveConfig)
        file_menu.addAction(save_config_action)
        
        load_config_action = QAction('加载配置', self)
        load_config_action.triggered.connect(self.loadConfig)
        file_menu.addAction(load_config_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具')
        
        check_update_action = QAction('检查更新', self)
        check_update_action.triggered.connect(self.checkUpdate)
        tools_menu.addAction(check_update_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        help_action = QAction('参数帮助', self)
        help_action.triggered.connect(self.showHelp)
        help_menu.addAction(help_action)
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.showAbout)
        help_menu.addAction(about_action)
        
        # 创建选项卡
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # 基本下载选项卡
        basic_tab = QWidget()
        basic_layout = QVBoxLayout()
        basic_layout.setSpacing(15) # 设置基本选项卡内控件的间距
        basic_layout.setContentsMargins(5, 5, 5, 5) # 设置基本选项卡内边距
        basic_tab.setLayout(basic_layout)
        
        # URL 输入
        url_layout = QHBoxLayout()
        url_label = QLabel("视频URL:")
        self.url_input = QLineEdit()
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        basic_layout.addLayout(url_layout)
        
        # 输出目录
        output_layout = QHBoxLayout()
        output_label = QLabel("保存位置:")
        self.output_path = QLineEdit()
        self.output_path.setText(os.path.expanduser("~/Downloads"))
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.browse_output)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(browse_button)
        basic_layout.addLayout(output_layout)
        
        # 下载类型选择
        type_group = QGroupBox("下载类型")
        type_layout = QVBoxLayout()
        
        self.type_buttons = QButtonGroup()
        self.video_audio_radio = QRadioButton("视频和音频")
        self.video_only_radio = QRadioButton("仅视频")
        self.audio_only_radio = QRadioButton("仅音频")
        
        self.type_buttons.addButton(self.video_audio_radio)
        self.type_buttons.addButton(self.video_only_radio)
        self.type_buttons.addButton(self.audio_only_radio)
        
        self.video_audio_radio.setChecked(True)
        
        type_layout.addWidget(self.video_audio_radio)
        type_layout.addWidget(self.video_only_radio)
        type_layout.addWidget(self.audio_only_radio)
        type_group.setLayout(type_layout)
        basic_layout.addWidget(type_group)
        
        # 质量选择
        quality_layout = QHBoxLayout()
        quality_label = QLabel("视频质量:")
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["最佳", "1080p", "720p", "480p", "360p", "240p", "144p"])
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_combo)
        basic_layout.addLayout(quality_layout)
        
        # 音频质量
        audio_quality_layout = QHBoxLayout()
        audio_quality_label = QLabel("音频质量:")
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(["最佳", "320k", "256k", "192k", "128k", "96k", "64k"])
        audio_quality_layout.addWidget(audio_quality_label)
        audio_quality_layout.addWidget(self.audio_quality_combo)
        basic_layout.addLayout(audio_quality_layout)
        
        # 字幕选项
        subtitle_group = QGroupBox("字幕选项")
        subtitle_layout = QVBoxLayout()
        
        self.download_subs = QCheckBox("下载字幕")
        self.auto_subs = QCheckBox("包含自动生成的字幕")
        self.all_subs = QCheckBox("下载所有可用字幕")
        
        subtitle_lang_layout = QHBoxLayout()
        subtitle_lang_label = QLabel("字幕语言:")
        self.subtitle_lang = QLineEdit()
        self.subtitle_lang.setPlaceholderText("例如: en,zh-CN (留空下载所有)")
        subtitle_lang_layout.addWidget(subtitle_lang_label)
        subtitle_lang_layout.addWidget(self.subtitle_lang)
        
        subtitle_layout.addWidget(self.download_subs)
        subtitle_layout.addWidget(self.auto_subs)
        subtitle_layout.addWidget(self.all_subs)
        subtitle_layout.addLayout(subtitle_lang_layout)
        subtitle_group.setLayout(subtitle_layout)
        basic_layout.addWidget(subtitle_group)
        
        # 播放列表选项
        playlist_group = QGroupBox("播放列表选项")
        playlist_layout = QVBoxLayout()
        
        self.download_playlist = QCheckBox("下载整个播放列表")
        
        playlist_range_layout = QHBoxLayout()
        playlist_range_label = QLabel("播放列表范围:")
        self.playlist_range = QLineEdit()
        self.playlist_range.setPlaceholderText("例如: 1-5,7,9 (留空下载全部)")
        playlist_range_layout.addWidget(playlist_range_label)
        playlist_range_layout.addWidget(self.playlist_range)
        
        playlist_layout.addWidget(self.download_playlist)
        playlist_layout.addLayout(playlist_range_layout)
        playlist_group.setLayout(playlist_layout)
        basic_layout.addWidget(playlist_group)
        
        # 高级选项卡
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout()
        advanced_layout.setSpacing(15) # 设置高级选项卡内控件的间距
        advanced_layout.setContentsMargins(5, 5, 5, 5) # 设置高级选项卡内边距
        advanced_tab.setLayout(advanced_layout)
        
        # 代理设置
        proxy_group = QGroupBox("代理设置")
        proxy_layout = QVBoxLayout()
        
        self.use_proxy = QCheckBox("使用代理")
        
        proxy_url_layout = QHBoxLayout()
        proxy_url_label = QLabel("代理URL:")
        self.proxy_url = QLineEdit()
        self.proxy_url.setPlaceholderText("例如: socks5://127.0.0.1:1080")
        proxy_url_layout.addWidget(proxy_url_label)
        proxy_url_layout.addWidget(self.proxy_url)
        
        proxy_layout.addWidget(self.use_proxy)
        proxy_layout.addLayout(proxy_url_layout)
        proxy_group.setLayout(proxy_layout)
        advanced_layout.addWidget(proxy_group)
        
        # 文件名模板
        filename_layout = QHBoxLayout()
        filename_label = QLabel("文件名模板:")
        self.filename_template = QLineEdit()
        self.filename_template.setPlaceholderText("例如: %(title)s-%(id)s.%(ext)s")
        filename_layout.addWidget(filename_label)
        filename_layout.addWidget(self.filename_template)
        advanced_layout.addLayout(filename_layout)
        
        # 限速设置
        speed_limit_layout = QHBoxLayout()
        speed_limit_label = QLabel("下载速度限制 (KB/s):")
        self.speed_limit = QSpinBox()
        self.speed_limit.setRange(0, 100000)
        self.speed_limit.setValue(0)
        self.speed_limit.setSpecialValueText("无限制")
        speed_limit_layout.addWidget(speed_limit_label)
        speed_limit_layout.addWidget(self.speed_limit)
        advanced_layout.addLayout(speed_limit_layout)
        
        # 新增高级选项
        advanced_options_group = QGroupBox("其他高级选项")
        advanced_options_layout = QVBoxLayout()
        
        # 断点续传
        self.continue_dl = QCheckBox("断点续传")
        advanced_options_layout.addWidget(self.continue_dl)
        
        # 不覆盖已存在的文件
        self.no_overwrites = QCheckBox("不覆盖已存在的文件")
        advanced_options_layout.addWidget(self.no_overwrites)
        
        # 添加元数据
        self.add_metadata = QCheckBox("添加元数据")
        advanced_options_layout.addWidget(self.add_metadata)
        
        # 嵌入缩略图
        self.embed_thumbnail = QCheckBox("嵌入缩略图到音频文件")
        advanced_options_layout.addWidget(self.embed_thumbnail)
        
        # 嵌入字幕
        self.embed_subs = QCheckBox("嵌入字幕到视频文件")
        advanced_options_layout.addWidget(self.embed_subs)
        
        # 忽略错误
        self.ignore_errors = QCheckBox("忽略错误并继续下载")
        advanced_options_layout.addWidget(self.ignore_errors)
        
        # 地理位置绕过
        self.geo_bypass = QCheckBox("绕过地理限制")
        advanced_options_layout.addWidget(self.geo_bypass)
        
        # 合并输出格式
        merge_format_layout = QHBoxLayout()
        merge_format_label = QLabel("合并输出格式:")
        self.merge_format_combo = QComboBox()
        self.merge_format_combo.addItems(["默认", "mp4", "mkv", "ogg", "webm", "flv"])
        merge_format_layout.addWidget(merge_format_label)
        merge_format_layout.addWidget(self.merge_format_combo)
        advanced_options_layout.addLayout(merge_format_layout)
        
        advanced_options_group.setLayout(advanced_options_layout)
        advanced_layout.addWidget(advanced_options_group)
        
        # 自定义参数
        custom_args_layout = QVBoxLayout()
        custom_args_label = QLabel("自定义参数:")
        self.custom_args = QTextEdit()
        self.custom_args.setPlaceholderText("每行一个参数，例如:\n--no-mtime\n--no-overwrites")
        custom_args_layout.addWidget(custom_args_label)
        custom_args_layout.addWidget(self.custom_args)
        advanced_layout.addLayout(custom_args_layout)
        
        # 命令预览
        command_preview_layout = QVBoxLayout()
        command_preview_label = QLabel("命令预览:")
        self.command_preview = QTextEdit()
        self.command_preview.setReadOnly(True)
        command_preview_layout.addWidget(command_preview_label)
        command_preview_layout.addWidget(self.command_preview)
        advanced_layout.addLayout(command_preview_layout)
        
        # 添加选项卡
        tabs.addTab(basic_tab, "基本选项")
        tabs.addTab(advanced_tab, "高级选项")
        
        # 下载按钮和进度
        download_layout = QVBoxLayout()
        
        button_layout = QHBoxLayout()
        
        self.download_button = QPushButton("开始下载")
        self.download_button.clicked.connect(self.start_download)
        button_layout.addWidget(self.download_button)
        
        # 更新命令预览按钮
        update_preview_button = QPushButton("更新命令预览")
        update_preview_button.clicked.connect(self.update_command_preview)
        button_layout.addWidget(update_preview_button)
        
        # 帮助按钮
        help_button = QPushButton("参数帮助")
        help_button.clicked.connect(self.showHelp)
        button_layout.addWidget(help_button)
        
        download_layout.addLayout(button_layout)
        
        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("准备就绪")
        download_layout.addWidget(self.progress_bar)
        
        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        download_layout.addWidget(self.progress_text)
        
        main_layout.addLayout(download_layout)
        
        # 初始化下载线程
        self.download_thread = None
        
    def setToolTips(self):
        """设置控件的悬停提示"""
        self.url_input.setToolTip("输入要下载的视频URL，支持YouTube、Bilibili等多网站")
        self.output_path.setToolTip("选择下载文件的保存位置")
        
        self.video_audio_radio.setToolTip("下载最佳质量的视频和音频并自动合并")
        self.video_only_radio.setToolTip("仅下载视频部分，不包含音频")
        self.audio_only_radio.setToolTip("仅提取音频部分，转换为MP3格式")
        
        self.quality_combo.setToolTip("选择视频的最大分辨率")
        self.audio_quality_combo.setToolTip("选择音频的比特率质量")
        
        self.download_subs.setToolTip("下载视频的字幕文件")
        self.auto_subs.setToolTip("包含自动生成的字幕（如有）")
        self.all_subs.setToolTip("下载所有可用语言的字幕")
        self.subtitle_lang.setToolTip("指定要下载的字幕语言代码，多个语言用逗号分隔")
        
        self.download_playlist.setToolTip("如果URL指向播放列表，下载整个播放列表")
        self.playlist_range.setToolTip("指定要下载的播放列表项目范围")
        
        self.use_proxy.setToolTip("使用代理服务器进行下载")
        self.proxy_url.setToolTip("代理服务器URL，支持HTTP、SOCKS等多种协议")
        
        self.filename_template.setToolTip("自定义输出文件名模板，使用youtube-dl支持的格式")
        self.speed_limit.setToolTip("限制下载速度，单位为KB/s，0表示不限制")
        
        self.continue_dl.setToolTip("断点续传，继续下载部分下载的文件")
        self.no_overwrites.setToolTip("不覆盖已存在的文件")
        self.add_metadata.setToolTip("将元数据写入下载的文件")
        self.embed_thumbnail.setToolTip("将视频缩略图嵌入到音频文件中")
        self.embed_subs.setToolTip("将字幕嵌入到视频文件中")
        self.ignore_errors.setToolTip("忽略错误，继续下载播放列表中的其他视频")
        self.geo_bypass.setToolTip("绕过地理限制，适用于某些地区限制的视频")
        self.merge_format_combo.setToolTip("指定视频和音频合并后的输出格式")
        
        self.custom_args.setToolTip("添加其他youtube-dl命令行参数，每行一个")
        self.command_preview.setToolTip("显示将要执行的完整命令")
        
        self.download_button.setToolTip("开始下载视频")
        
    def saveConfig(self):
        """保存当前配置到配置文件"""
        config = configparser.ConfigParser()
        
        # 基本设置
        config['Basic'] = {
            'OutputPath': self.output_path.text(),
            'DownloadType': 'video_audio' if self.video_audio_radio.isChecked() else 
                           ('video_only' if self.video_only_radio.isChecked() else 'audio_only'),
            'VideoQuality': self.quality_combo.currentText(),
            'AudioQuality': self.audio_quality_combo.currentText()
        }
        
        # 字幕设置
        config['Subtitle'] = {
            'DownloadSubs': str(self.download_subs.isChecked()),
            'AutoSubs': str(self.auto_subs.isChecked()),
            'AllSubs': str(self.all_subs.isChecked()),
            'SubtitleLang': self.subtitle_lang.text()
        }
        
        # 播放列表设置
        config['Playlist'] = {
            'DownloadPlaylist': str(self.download_playlist.isChecked()),
            'PlaylistRange': self.playlist_range.text()
        }
        
        # 代理设置
        config['Proxy'] = {
            'UseProxy': str(self.use_proxy.isChecked()),
            'ProxyURL': self.proxy_url.text()
        }
        
        # 高级设置
        config['Advanced'] = {
            'FilenameTemplate': self.filename_template.text(),
            'SpeedLimit': str(self.speed_limit.value()),
            'ContinueDL': str(self.continue_dl.isChecked()),
            'NoOverwrites': str(self.no_overwrites.isChecked()),
            'AddMetadata': str(self.add_metadata.isChecked()),
            'EmbedThumbnail': str(self.embed_thumbnail.isChecked()),
            'EmbedSubs': str(self.embed_subs.isChecked()),
            'IgnoreErrors': str(self.ignore_errors.isChecked()),
            'GeoBypass': str(self.geo_bypass.isChecked()),
            'MergeFormat': self.merge_format_combo.currentText(),
            'CustomArgs': self.custom_args.toPlainText()
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                config.write(f)
            QMessageBox.information(self, "成功", "配置已保存")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存配置失败: {str(e)}")
    
    def loadConfig(self):
        """从配置文件加载配置"""
        if not os.path.exists(self.config_file):
            QMessageBox.information(self, "提示", "没有找到配置文件")
            return
            
        config = configparser.ConfigParser()
        
        try:
            config.read(self.config_file, encoding='utf-8')
            
            # 基本设置
            if 'Basic' in config:
                if 'OutputPath' in config['Basic']:
                    self.output_path.setText(config['Basic']['OutputPath'])
                
                if 'DownloadType' in config['Basic']:
                    download_type = config['Basic']['DownloadType']
                    if download_type == 'video_audio':
                        self.video_audio_radio.setChecked(True)
                    elif download_type == 'video_only':
                        self.video_only_radio.setChecked(True)
                    elif download_type == 'audio_only':
                        self.audio_only_radio.setChecked(True)
                
                if 'VideoQuality' in config['Basic']:
                    index = self.quality_combo.findText(config['Basic']['VideoQuality'])
                    if index >= 0:
                        self.quality_combo.setCurrentIndex(index)
                
                if 'AudioQuality' in config['Basic']:
                    index = self.audio_quality_combo.findText(config['Basic']['AudioQuality'])
                    if index >= 0:
                        self.audio_quality_combo.setCurrentIndex(index)
            
            # 字幕设置
            if 'Subtitle' in config:
                if 'DownloadSubs' in config['Subtitle']:
                    self.download_subs.setChecked(config['Subtitle']['DownloadSubs'].lower() == 'true')
                
                if 'AutoSubs' in config['Subtitle']:
                    self.auto_subs.setChecked(config['Subtitle']['AutoSubs'].lower() == 'true')
                
                if 'AllSubs' in config['Subtitle']:
                    self.all_subs.setChecked(config['Subtitle']['AllSubs'].lower() == 'true')
                
                if 'SubtitleLang' in config['Subtitle']:
                    self.subtitle_lang.setText(config['Subtitle']['SubtitleLang'])
            
            # 播放列表设置
            if 'Playlist' in config:
                if 'DownloadPlaylist' in config['Playlist']:
                    self.download_playlist.setChecked(config['Playlist']['DownloadPlaylist'].lower() == 'true')
                
                if 'PlaylistRange' in config['Playlist']:
                    self.playlist_range.setText(config['Playlist']['PlaylistRange'])
            
            # 代理设置
            if 'Proxy' in config:
                if 'UseProxy' in config['Proxy']:
                    self.use_proxy.setChecked(config['Proxy']['UseProxy'].lower() == 'true')
                
                if 'ProxyURL' in config['Proxy']:
                    self.proxy_url.setText(config['Proxy']['ProxyURL'])
            
            # 高级设置
            if 'Advanced' in config:
                if 'FilenameTemplate' in config['Advanced']:
                    self.filename_template.setText(config['Advanced']['FilenameTemplate'])
                
                if 'SpeedLimit' in config['Advanced']:
                    try:
                        self.speed_limit.setValue(int(config['Advanced']['SpeedLimit']))
                    except ValueError:
                        pass
                
                if 'ContinueDL' in config['Advanced']:
                    self.continue_dl.setChecked(config['Advanced']['ContinueDL'].lower() == 'true')
                
                if 'NoOverwrites' in config['Advanced']:
                    self.no_overwrites.setChecked(config['Advanced']['NoOverwrites'].lower() == 'true')
                
                if 'AddMetadata' in config['Advanced']:
                    self.add_metadata.setChecked(config['Advanced']['AddMetadata'].lower() == 'true')
                
                if 'EmbedThumbnail' in config['Advanced']:
                    self.embed_thumbnail.setChecked(config['Advanced']['EmbedThumbnail'].lower() == 'true')
                
                if 'EmbedSubs' in config['Advanced']:
                    self.embed_subs.setChecked(config['Advanced']['EmbedSubs'].lower() == 'true')
                
                if 'IgnoreErrors' in config['Advanced']:
                    self.ignore_errors.setChecked(config['Advanced']['IgnoreErrors'].lower() == 'true')
                
                if 'GeoBypass' in config['Advanced']:
                    self.geo_bypass.setChecked(config['Advanced']['GeoBypass'].lower() == 'true')
                
                if 'MergeFormat' in config['Advanced']:
                    index = self.merge_format_combo.findText(config['Advanced']['MergeFormat'])
                    if index >= 0:
                        self.merge_format_combo.setCurrentIndex(index)
                
                if 'CustomArgs' in config['Advanced']:
                    self.custom_args.setPlainText(config['Advanced']['CustomArgs'])
            
            QMessageBox.information(self, "成功", "配置已加载")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载配置失败: {str(e)}")
    
    def checkUpdate(self):
        """检查youtube-dl更新"""
        self.progress_text.clear()
        self.progress_text.append("正在检查更新...")
        self.download_button.setEnabled(False)
        
        # 创建一个线程来检查更新
        # command = ["C:\\Users\\zhang-jiahuang\\yt-dlp.exe", "--update"]
        # 获取应用程序路径
        app_path = get_application_path()
        # 构建yt-dlp.exe的路径
        ytdlp_path = os.path.join(app_path, "yt-dlp.exe")
        
        # 如果打包后的yt-dlp.exe存在，使用它
        if os.path.exists(ytdlp_path):
            command = [ytdlp_path, "--update"]
        else:
            # 否则尝试使用系统PATH中的yt-dlp.exe
            command = [f"{file_path}\\yt-dlp.exe", "--update"]
        self.update_thread = DownloadThread(command)
        self.update_thread.progress_signal.connect(self.update_progress)
        self.update_thread.finished_signal.connect(self.update_finished)
        self.update_thread.start()
    
    def update_progress(self, text):
        """更新进度文本"""
        self.progress_text.append(text)
    
    def update_finished(self, success, message):
        """更新完成的回调"""
        self.progress_text.append(message)
        self.download_button.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "更新", "YouTube-DL 已更新到最新版本")
        else:
            QMessageBox.warning(self, "更新失败", f"更新失败: {message}")
    
    def showHelp(self):
        """显示帮助对话框"""
        help_dialog = HelpDialog(self)
        help_dialog.exec_()
    
    def showAbout(self):
        """显示关于对话框"""
        about_dialog = AboutDialog(self)
        about_dialog.exec_()
    
    def check_youtube_dl(self):
        """检查youtube-dl是否已安装"""
        try:
            # 获取应用程序路径
            app_path = get_application_path()
            # 构建yt-dlp.exe的路径
            ytdlp_path = os.path.join(app_path, "yt-dlp.exe")
            
            # 如果打包后的yt-dlp.exe存在，使用它
            if os.path.exists(ytdlp_path):
                cmd = [ytdlp_path, "--version"]
            else:
                # 否则尝试使用系统PATH中的yt-dlp.exe
                cmd = [f"{file_path}\\yt-dlp.exe", "--version"]
            result = subprocess.run(
                # ["C:\\Users\\zhang-jiahuang\\yt-dlp.exe", "--version"], 
                cmd,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def browse_output(self):
        """浏览并选择输出目录"""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "选择保存位置", 
            self.output_path.text(),
            QFileDialog.ShowDirsOnly
        )
        if directory:
            self.output_path.setText(directory)
    
    def update_command_preview(self):
        """更新命令预览"""
        command = self.build_command(preview=True)
        if command:
            self.command_preview.setText(" ".join(command))
    
    def build_command(self, preview=False):
        """构建youtube-dl命令"""
        url = self.url_input.text().strip()
        output_path = self.output_path.text().strip()
        
        if not url and not preview:
            QMessageBox.warning(self, "错误", "请输入视频URL")
            return None            
        # command = ["C:\\Users\\zhang-jiahuang\\yt-dlp.exe"]  # 使用C:\\Users\\zhang-jiahuang\\yt-dlp.exe替代youtube-dl
        # 获取应用程序路径
        app_path = get_application_path()
        # 构建yt-dlp.exe的路径
        ytdlp_path = os.path.join(app_path, "yt-dlp.exe")
        
        # 如果打包后的yt-dlp.exe存在，使用它
        if os.path.exists(ytdlp_path):
            command = [ytdlp_path]
        else:
            # 否则尝试使用系统PATH中的yt-dlp.exe
            command = [f"{file_path}\\yt-dlp.exe"]
        # 基本选项
        if self.video_audio_radio.isChecked():
            command.append("-f")  # -f/--format：指定下载的文件格式
            command.append("bestvideo+bestaudio/best")  # 最佳视频+最佳音频/最佳质量
        elif self.video_only_radio.isChecked():
            command.append("-f")  # -f/--format：指定下载的文件格式
            quality = self.quality_combo.currentText()
            if quality == "最佳":
                command.append("bestvideo")  # 最佳视频质量
            else:
                # 提取数字部分
                resolution = quality.replace("p", "")
                command.append(f"bestvideo[height<={resolution}]/best[height<={resolution}]")  # 指定最大高度的视频
        elif self.audio_only_radio.isChecked():
            command.append("-x")  # -x/--extract-audio：提取音频
            command.append("--audio-format")  # --audio-format：指定音频格式
            command.append("mp3")  # mp3格式
            
            audio_quality = self.audio_quality_combo.currentText()
            if audio_quality != "最佳":
                command.append("--audio-quality")  # --audio-quality：指定音频质量
                command.append(audio_quality)  # 音频比特率
        
        # 输出路径
        if output_path:
            command.append("-o")  # -o/--output：指定输出文件名模板
            
            # 文件名模板
            filename = self.filename_template.text().strip()
            if filename:
                output_template = os.path.join(output_path, filename)
            else:
                output_template = os.path.join(output_path, "%(title)s.%(ext)s")  # 默认模板：标题.扩展名
                
            command.append(output_template)
            
        # 字幕选项
        if self.download_subs.isChecked():
            command.append("--write-sub")  # --write-sub：下载字幕
            
            if self.auto_subs.isChecked():
                command.append("--write-auto-sub")  # --write-auto-sub：下载自动生成的字幕
                
            if self.all_subs.isChecked():
                command.append("--all-subs")  # --all-subs：下载所有可用字幕
            else:
                subtitle_lang = self.subtitle_lang.text().strip()
                if subtitle_lang:
                    command.append("--sub-lang")  # --sub-lang：指定字幕语言
                    command.append(subtitle_lang)  # 字幕语言代码，如en,zh-CN
        
        # 播放列表选项
        if self.download_playlist.isChecked():
            command.append("--yes-playlist")  # --yes-playlist：下载整个播放列表
            
            playlist_range = self.playlist_range.text().strip()
            if playlist_range:
                command.append("--playlist-items")  # --playlist-items：指定播放列表项目范围
                command.append(playlist_range)  # 播放列表范围，如1-5,7,9
        else:
            command.append("--no-playlist")  # --no-playlist：不下载播放列表，即使URL指向播放列表
            
        # 代理设置
        if self.use_proxy.isChecked():
            proxy_url = self.proxy_url.text().strip()
            if proxy_url:
                command.append("--proxy")  # --proxy：使用代理
                command.append(proxy_url)  # 代理URL，如socks5://127.0.0.1:1080
                
        # 限速设置
        speed_limit = self.speed_limit.value()
        if speed_limit > 0:
            command.append("--limit-rate")  # --limit-rate：限制下载速度
            command.append(f"{speed_limit}K")  # 速度限制，单位KB/s
        
        # 高级选项
        if self.continue_dl.isChecked():
            command.append("--continue")  # --continue：断点续传
            
        if self.no_overwrites.isChecked():
            command.append("--no-overwrites")  # --no-overwrites：不覆盖已存在的文件
            
        if self.add_metadata.isChecked():
            command.append("--add-metadata")  # --add-metadata：将元数据写入下载的文件
            
        if self.embed_thumbnail.isChecked():
            command.append("--embed-thumbnail")  # --embed-thumbnail：将缩略图嵌入音频文件
            
        if self.embed_subs.isChecked():
            command.append("--embed-subs")  # --embed-subs：将字幕嵌入视频文件
            
        if self.ignore_errors.isChecked():
            command.append("--ignore-errors")  # --ignore-errors：忽略错误，继续下载
            
        if self.geo_bypass.isChecked():
            command.append("--geo-bypass")  # --geo-bypass：绕过地理限制
            
        # 合并输出格式
        merge_format = self.merge_format_combo.currentText()
        if merge_format != "默认":
            command.append("--merge-output-format")  # --merge-output-format：指定合并后的输出格式
            command.append(merge_format.lower())  # 输出格式，如mp4, mkv等
            
        # 自定义参数
        custom_args = self.custom_args.toPlainText().strip()
        if custom_args:
            for arg in custom_args.split("\n"):
                arg = arg.strip()
                if arg:
                    command.append(arg)  # 添加用户自定义的参数
                    
        # 添加URL
        if url:
            command.append(url)  # 视频URL
            
        return command
    
    def start_download(self):
        """开始下载"""
        command = self.build_command()
        if not command:
            return
            
        self.progress_text.clear()
        self.progress_text.append("准备下载...")
        self.download_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("下载中 %p%")
        
        self.download_thread = DownloadThread(command)
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.progress_percent_signal.connect(self.update_progress_bar)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.start()
        
    def update_progress_bar(self, percent):
        """更新进度条"""
        self.progress_bar.setValue(percent)
    
    def download_finished(self, success, message):
        """下载完成的回调"""
        self.progress_text.append(message)
        self.download_button.setEnabled(True)
        self.progress_bar.setFormat("准备就绪")
        
        if success:
            QMessageBox.information(self, "完成", "下载已完成！")
        else:
            QMessageBox.warning(self, "错误", f"下载失败: {message}")
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 应用全局样式
    qss_style = """
QWidget {
    font-size: 10pt; /* 统一字体大小 */
}

QMainWindow {
    background-color: #f0f0f0; /* 主窗口背景色 */
}

QTabWidget::pane {
    border-top: 2px solid #C2C7CB;
    background-color: #ffffff; /* 标签页内容区域背景色 */
}

QTabBar::tab {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
    border: 1px solid #C4C4C3;
    border-bottom-color: #C2C7CB; /* 与pane的border连接 */
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    min-width: 8ex;
    padding: 5px;
    margin-right: 2px;
}

QTabBar::tab:selected, QTabBar::tab:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #fafafa, stop: 0.4 #f4f4f4,
                                stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);
}

QTabBar::tab:selected {
    border-color: #9B9B9B;
    border-bottom-color: #C2C7CB; /* 与pane的border连接 */
}

QGroupBox {
    background-color: #f7f7f7; /* 分组框背景色 */
    border: 1px solid #cccccc;
    border-radius: 5px;
    margin-top: 1ex; /* 上边距，为标题留出空间 */
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left; /* 标题位置 */
    padding: 0 3px;
    background-color: #f0f0f0; /* 标题背景，使其与主背景融合 */
    border-radius: 3px;
}

QPushButton {
    background-color: #4CAF50; /* 按钮背景色 - 绿色 */
    border: none;
    color: white; /* 按钮文字颜色 - 白色 */
    padding: 8px 16px;
    text-align: center;
    text-decoration: none;
    font-size: 10pt;
    margin: 4px 2px;
    border-radius: 4px; /* 圆角 */
}

QPushButton:hover {
    background-color: #45a049; /* 鼠标悬停时颜色变深 */
}

QPushButton:pressed {
    background-color: #3e8e41; /* 按下时颜色更深 */
}

QLineEdit, QTextEdit, QSpinBox, QComboBox {
    padding: 5px;
    border: 1px solid #cccccc;
    border-radius: 3px;
    background-color: white;
}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #4CAF50; /* 焦点时的边框颜色 */
}

QProgressBar {
    border: 1px solid #cccccc;
    border-radius: 3px;
    text-align: center;
    background-color: white;
}

QProgressBar::chunk {
    background-color: #4CAF50; /* 进度条颜色 */
    width: 10px; /* 进度块宽度 */
    margin: 0.5px;
}

QCheckBox::indicator {
    width: 13px;
    height: 13px;
}

QRadioButton::indicator {
    width: 13px;
    height: 13px;
}

QScrollBar:horizontal {
    border: 1px solid #cccccc;
    background: #f0f0f0;
    height: 15px;
    margin: 0px 20px 0 20px;
}
QScrollBar::handle:horizontal {
    background: #c0c0c0;
    min-width: 20px;
    border-radius: 7px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    border: 1px solid #cccccc;
    background: #e0e0e0;
    width: 20px;
    subcontrol-position: right;
    subcontrol-origin: margin;
}
QScrollBar::add-line:horizontal:hover, QScrollBar::sub-line:horizontal:hover {
    background: #d0d0d0;
}
QScrollBar::add-line:horizontal {
    right: 0px;
}
QScrollBar::sub-line:horizontal {
    left: 0px;
}


QScrollBar:vertical {
    border: 1px solid #cccccc;
    background: #f0f0f0;
    width: 15px;
    margin: 20px 0 20px 0;
}
QScrollBar::handle:vertical {
    background: #c0c0c0;
    min-height: 20px;
    border-radius: 7px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: 1px solid #cccccc;
    background: #e0e0e0;
    height: 20px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}
QScrollBar::add-line:vertical:hover, QScrollBar::sub-line:vertical:hover {
    background: #d0d0d0;
}
QScrollBar::add-line:vertical {
    bottom: 0px;
}
QScrollBar::sub-line:vertical {
    top: 0px;
}
    """
    app.setStyleSheet(qss_style)
    
    window = YouTubeDLGUI()
    window.show()
    sys.exit(app.exec_())
