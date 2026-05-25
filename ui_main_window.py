# ui_main_window.py
import os
import sys
import json
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QStackedWidget, QLabel, QPushButton, QFrame,
                               QMenuBar, QMenu, QDialog, QTextBrowser, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from ui_draw_page import DrawPage
from ui_settings_page import SettingsPage
from core import DrawCore
from music import MusicPlayer

try:
    from win32com.client import Dispatch
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False

class MainWindow(QMainWindow):
    def __init__(self, default_students=None):
        super().__init__()
        self.core = DrawCore()
        if default_students:
            self.core.load_students(default_students)
        self.music = MusicPlayer()
        self.settings = self.load_settings()
        self.music.enabled = self.settings.get('music_enabled', False)
        self.music.file = self.settings.get('music_file', '')
        self.music.volume = self.settings.get('music_volume', 0.5)
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_connections()
        # 检测并保存安装路径（关键：解决冰点还原下自启动路径错误问题）
        self._detect_and_save_install_path()
        # 确保桌面快捷方式指向安装路径
        self._ensure_desktop_shortcut()

    # ---------- 安装路径检测与保存 ----------
    def _detect_and_save_install_path(self):
        """检测当前程序所在目录，并保存为安装路径（如果尚未保存）"""
        # 获取当前运行的可执行文件路径
        if getattr(sys, 'frozen', False):
            current_exe = sys.executable
        else:
            current_exe = os.path.abspath(sys.argv[0])
        current_dir = os.path.dirname(current_exe)

        # 如果配置中没有 install_path，则写入
        if 'install_path' not in self.settings:
            self.settings['install_path'] = current_dir
            self.save_settings()
            # 可选：静默保存，不打扰用户
        else:
            saved_path = self.settings['install_path']
            if saved_path != current_dir:
                # 若当前运行路径与保存的不一致，可能用户从非安装目录启动了程序
                # 此时仍使用保存的路径进行后续操作，但可以控制台输出警告
                print(f"警告：程序运行路径({current_dir})与安装路径({saved_path})不一致，开机自启动将使用安装路径。")

    # ---------- 桌面快捷方式（强制使用安装路径） ----------
    def _ensure_desktop_shortcut(self):
        """在桌面创建指向安装目录下 exe 的快捷方式，绕过冰点还原"""
        if not HAS_WIN32COM:
            return
        try:
            # 从配置中获取安装路径
            install_path = self.settings.get('install_path')
            if install_path:
                exe_name = "智能抽号系统_v3.0_beta.exe"
                target = os.path.join(install_path, exe_name)
                if not os.path.exists(target):
                    # 如果安装目录下找不到 exe，回退到当前运行路径
                    if getattr(sys, 'frozen', False):
                        target = sys.executable
                    else:
                        target = os.path.abspath(sys.argv[0])
            else:
                # 没有保存安装路径，回退
                if getattr(sys, 'frozen', False):
                    target = sys.executable
                else:
                    target = os.path.abspath(sys.argv[0])

            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop):
                desktop = os.path.join(os.path.expanduser("~"), "桌面")
            shortcut_path = os.path.join(desktop, "智能抽号系统.lnk")

            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = target
            shortcut.WorkingDirectory = os.path.dirname(target)
            shortcut.IconLocation = target
            shortcut.Save()
        except Exception:
            pass  # 静默失败，不影响主程序

    # ---------- 设置加载/保存 ----------
    def load_settings(self):
        default = {
            'result_font_size': 36,
            'result_font_family': 'Microsoft YaHei',
            'result_font_color': '#ffffff',
            'auto_save': True,
            'music_enabled': False,
            'music_volume': 0.5,
            'music_file': '',
            'theme': 'dark',
            'animation_enabled': False,
            'animation_duration': 0.5,
            'animation_interval': 30,
        }
        if os.path.exists('app_settings.json'):
            try:
                with open('app_settings.json', 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    default.update(saved)
            except:
                pass
        return default

    def save_settings(self):
        try:
            with open('app_settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except:
            pass

    # ---------- 菜单栏 ----------
    def setup_menu_bar(self):
        menubar = self.menuBar()
        help_menu = menubar.addMenu("帮助")
        about_action = help_menu.addAction("关于")
        about_action.triggered.connect(self.show_about)
        changelog_action = help_menu.addAction("更新日志")
        changelog_action.triggered.connect(self.show_changelog)

    def show_about(self):
        QMessageBox.about(self, "关于智能抽号系统",
                          "<h3>智能抽号系统 v3.0.1</h3>"
                          "<p>基于 PySide6 开发的课堂抽号工具</p>"
                          "<p>作者：开方居士</p>"
                          "<p>项目地址：<a href='https://github.com/你的用户名/random-draw-pyside6'>GitHub</a></p>")

    def show_changelog(self):
        """读取外部 CHANGELOG.md 文件并显示"""
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        changelog_path = os.path.join(base_path, "CHANGELOG.md")
        dialog = QDialog(self)
        dialog.setWindowTitle("更新日志")
        dialog.resize(700, 500)
        layout = QVBoxLayout(dialog)
        text_browser = QTextBrowser()
        if os.path.exists(changelog_path):
            with open(changelog_path, 'r', encoding='utf-8') as f:
                content = f.read()
            text_browser.setMarkdown(content)
        else:
            text_browser.setPlainText("未找到 CHANGELOG.md 文件，请从项目主页查看更新记录。")
        layout.addWidget(text_browser)
        dialog.exec_()

    # ---------- 主界面布局 ----------
    def setup_ui(self):
        self.setWindowTitle("智能抽号系统 v3.0 - PySide6 完全版")
        self.resize(1300, 850)
        self.setMinimumSize(1100, 700)
        self.setWindowIcon(QIcon("app_icon.ico"))
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        nav_bar = QFrame()
        nav_bar.setFixedWidth(200)
        nav_bar.setObjectName("navBar")
        nav_bar.setStyleSheet("background-color: #2a2b3c; border-right: 1px solid #3a3b4c;")
        nav_layout = QVBoxLayout(nav_bar)
        nav_layout.setAlignment(Qt.AlignTop)
        nav_layout.setSpacing(20)
        nav_layout.setContentsMargins(20, 40, 20, 40)

        logo = QLabel("✨ 随机抽号")
        logo.setStyleSheet("font-size: 20px; font-weight: bold; color: #60a5fa;")
        logo.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(logo)

        self.nav_btns = []
        nav_items = [("🎲 抽号", 0), ("⚙️ 设置", 1)]
        for text, idx in nav_items:
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #cbd5e1;
                    font-size: 16px;
                    text-align: left;
                    padding: 12px 16px;
                    border-radius: 12px;
                }
                QPushButton:hover { background-color: #3b3c4e; color: white; }
            """)
            btn.clicked.connect(lambda checked, i=idx: self.stacked.setCurrentIndex(i))
            nav_layout.addWidget(btn)
            self.nav_btns.append(btn)
        nav_layout.addStretch()

        self.stacked = QStackedWidget()
        self.draw_page = DrawPage(self.core, self.music, self.settings, self.save_settings)
        self.settings_page = SettingsPage(self.core, self.settings, self.save_settings, self.draw_page.update_status, self.draw_page)
        self.stacked.addWidget(self.draw_page)
        self.stacked.addWidget(self.settings_page)

        main_layout.addWidget(nav_bar)
        main_layout.addWidget(self.stacked, 1)

        self.stacked.setCurrentIndex(0)
        self.nav_btns[0].setStyleSheet("background-color: #3b3c4e; color: white; border-radius: 12px;")

    def setup_connections(self):
        self.stacked.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        for i, btn in enumerate(self.nav_btns):
            if i == index:
                btn.setStyleSheet("background-color: #3b3c4e; color: white; border-radius: 12px;")
            else:
                btn.setStyleSheet("background-color: transparent; color: #cbd5e1; font-size: 16px; text-align: left; padding: 12px 16px; border-radius: 12px;")