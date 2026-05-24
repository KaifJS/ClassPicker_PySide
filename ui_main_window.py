# ui_main_window.py
import os
import sys
import json
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QStackedWidget, QLabel, QPushButton, QFrame,
                               QMenuBar, QMenu, QDialog, QTextBrowser, QMessageBox)
from PySide6.QtCore import Qt
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
        self.setup_menu_bar()          # 新增：创建菜单栏
        self.setup_connections()
        self._ensure_desktop_shortcut()

    # ---------- 桌面快捷方式（绕过冰点还原） ----------
    def _ensure_desktop_shortcut(self):
        if not HAS_WIN32COM:
            return
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop):
                desktop = os.path.join(os.path.expanduser("~"), "桌面")
            shortcut_path = os.path.join(desktop, "智能抽号系统.lnk")
            if getattr(sys, 'frozen', False):
                target = sys.executable
            else:
                target = os.path.abspath(sys.argv[0])
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = target
            shortcut.WorkingDirectory = os.path.dirname(target)
            shortcut.IconLocation = target
            shortcut.Save()
        except Exception:
            pass

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
        # 帮助菜单
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
        # 确定文件路径（支持打包后的 exe）
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS   # PyInstaller 临时目录
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
            # 简单的 Markdown 支持（标题、列表等）
            text_browser.setMarkdown(content)
        else:
            text_browser.setPlainText("未找到 CHANGELOG.md 文件，请从项目主页查看更新记录。")
        layout.addWidget(text_browser)
        dialog.exec_()

    # ---------- UI 布局（与之前相同） ----------
    def setup_ui(self):
        self.setWindowTitle("智能抽号系统 v3.0 - PySide6 完全版")
        self.resize(1300, 850)
        self.setMinimumSize(1100, 700)

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