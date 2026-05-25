# ui_settings_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QStackedWidget,
    QLabel, QPushButton, QFileDialog, QColorDialog, QScrollArea,
    QGridLayout, QLineEdit, QSlider, QPlainTextEdit, QMessageBox,
    QListWidgetItem, QInputDialog, QTableWidget, QTableWidgetItem, QCheckBox, QComboBox
)
from PySide6.QtCore import Qt, QTimer
from ui_components import CardWidget
import os, json, subprocess, sys
from win32com.client import Dispatch
import pygame

class SettingsPage(QWidget):
    def __init__(self, core, settings, save_callback, refresh_draw_callback, draw_page):
        super().__init__()
        self.core = core
        self.settings = settings
        self.save_callback = save_callback
        self.refresh_draw_callback = refresh_draw_callback
        self.draw_page = draw_page
        self.setup_ui()
        self.load_panels()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.stacked = QStackedWidget()
        self.menu_list = QListWidget()
        self.menu_list.setFixedWidth(180)
        self.menu_list.setStyleSheet("background-color: #2a2b3c; border: none;")
        self.menu_list.currentRowChanged.connect(self.stacked.setCurrentIndex)

        main_layout.addWidget(self.menu_list)
        main_layout.addWidget(self.stacked, 1)

    def load_panels(self):
        self.student_panel = StudentManagerPanel(self.core, self.on_student_changed)
        self.add_menu_item("👥 人员管理", self.student_panel)

        self.font_panel = FontSettingsPanel(self.settings, self.on_font_changed)
        self.add_menu_item("🔤 字体设置", self.font_panel)

        self.animation_panel = AnimationSettingsPanel(self.settings, self.on_animation_changed)
        self.add_menu_item("🎬 抽号动画", self.animation_panel)

        self.archive_panel = ArchiveManagerPanel(self.core, self.draw_page, self.student_panel)
        self.add_menu_item("💾 记忆存档", self.archive_panel)

        self.console_panel = DeveloperConsolePanel(self.core, self.on_console_command)
        self.add_menu_item("🖥️ 开发者命令", self.console_panel)

        self.stat_panel = StatisticsPanel(self.core)
        self.add_menu_item("📊 统计信息", self.stat_panel)

        self.entertainment_panel = EntertainmentPanel(self.core, self.draw_page.music, self.settings, self.save_callback)
        self.add_menu_item("🎵 娱乐功能", self.entertainment_panel)

        self.auto_panel = AutoStartPanel()
        self.add_menu_item("⚡ 开机自启动", self.auto_panel)

    def add_menu_item(self, name, widget):
        item = QListWidgetItem(name)
        self.menu_list.addItem(item)
        self.stacked.addWidget(widget)

    def on_student_changed(self):
        if self.core.students:
            self.core.generate_random_permutation()
        self.refresh_draw_callback()
        self.stat_panel.refresh()

    def on_font_changed(self):
        self.save_callback()
        self.refresh_draw_callback()
        # 立即应用字体设置到抽号页面
        self.draw_page.apply_font_settings()

    def on_animation_changed(self):
        self.save_callback()

    def on_console_command(self):
        self.refresh_draw_callback()
        self.student_panel.refresh_cards()


# ---------- 人员管理面板 ----------
class StudentManagerPanel(QWidget):
    def __init__(self, core, update_callback):
        super().__init__()
        self.core = core
        self.update_callback = update_callback
        self.selected_student = None
        self.setup_ui()
        self.refresh_cards()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ 增加")
        self.del_btn = QPushButton("➖ 删除")
        self.edit_btn = QPushButton("✏️ 编辑")
        self.add_btn.clicked.connect(self.add_student)
        self.del_btn.clicked.connect(self.delete_student)
        self.edit_btn.clicked.connect(self.edit_student)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.del_btn)
        btn_layout.addWidget(self.edit_btn)
        layout.addLayout(btn_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.card_container = QWidget()
        self.card_layout = QGridLayout(self.card_container)
        self.scroll_area.setWidget(self.card_container)
        layout.addWidget(self.scroll_area)

    def refresh_cards(self):
        self.clear_layout(self.card_layout)
        students = self.core.get_students()
        cols = 5
        for idx, stu in enumerate(students):
            display = stu.split('.', 1)[1].strip('()') if '(' in stu else stu
            card = CardWidget(display)
            card.mousePressEvent = lambda e, s=stu, c=card: self.select_card(s, c)
            row, col = divmod(idx, cols)
            self.card_layout.addWidget(card, row, col)
        self.selected_student = None

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def select_card(self, student, card):
        for i in range(self.card_layout.count()):
            w = self.card_layout.itemAt(i).widget()
            if isinstance(w, CardWidget):
                w.set_selected(False)
        card.set_selected(True)
        self.selected_student = student

    def add_student(self):
        name, ok = QInputDialog.getText(self, "增加成员", "请输入新成员的姓名：")
        if ok and name:
            self.core.add_student(name)
            self.refresh_cards()
            self.update_callback()

    def delete_student(self):
        if self.selected_student:
            reply = QMessageBox.question(self, "确认删除", f"确定要删除成员 {self.selected_student} 吗？")
            if reply == QMessageBox.Yes:
                self.core.delete_student(self.selected_student)
                self.refresh_cards()
                self.update_callback()
        else:
            QMessageBox.warning(self, "警告", "请先点击卡片选中要删除的成员")

    def edit_student(self):
        if self.selected_student:
            if '.' in self.selected_student and '(' in self.selected_student:
                parts = self.selected_student.split('.', 1)
                stu_num = parts[0]
                old_name = parts[1].strip('()')
            else:
                stu_num = ""
                old_name = self.selected_student
            new_name, ok = QInputDialog.getText(self, "编辑成员", f"修改成员 {stu_num}.({old_name}) 的姓名：", text=old_name)
            if ok and new_name and new_name != old_name:
                self.core.edit_student(self.selected_student, new_name)
                self.refresh_cards()
                self.update_callback()
        else:
            QMessageBox.warning(self, "警告", "请先点击卡片选中要编辑的成员")


# ---------- 字体设置面板 ----------
class FontSettingsPanel(QWidget):
    def __init__(self, settings, apply_callback):
        super().__init__()
        self.settings = settings
        self.apply_callback = apply_callback
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("字体大小:"))
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(20, 60)
        self.size_slider.setValue(self.settings.get('result_font_size', 36))
        self.size_slider.valueChanged.connect(self.preview)
        size_layout.addWidget(self.size_slider)
        layout.addLayout(size_layout)

        family_layout = QHBoxLayout()
        family_layout.addWidget(QLabel("字体:"))
        self.family_combo = QComboBox()
        common_fonts = [
            'Microsoft YaHei', 'SimHei', 'SimSun', 'KaiTi', 'FangSong',
            'Arial', 'Times New Roman', 'Consolas', 'Courier New',
            'Segoe UI', 'Verdana', 'Tahoma', '微软雅黑', '黑体', '宋体', '楷体', '仿宋'
        ]
        self.family_combo.addItems(common_fonts)
        self.family_combo.setEditable(True)
        current_family = self.settings.get('result_font_family', 'Microsoft YaHei')
        if current_family in common_fonts:
            self.family_combo.setCurrentText(current_family)
        else:
            self.family_combo.addItem(current_family)
            self.family_combo.setCurrentText(current_family)
        self.family_combo.currentTextChanged.connect(self.preview)
        family_layout.addWidget(self.family_combo)
        layout.addLayout(family_layout)

        color_btn = QPushButton("选择颜色")
        color_btn.clicked.connect(self.choose_color)
        layout.addWidget(color_btn)

        self.preview_label = QLabel("预览: 01.(张三)")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("padding: 20px; background-color: #1e1f2c; border-radius: 12px;")
        layout.addWidget(self.preview_label)

        apply_btn = QPushButton("应用并保存")
        apply_btn.clicked.connect(self.apply)
        layout.addWidget(apply_btn)

        self.preview()

    def preview(self):
        family = self.family_combo.currentText()
        size = self.size_slider.value()
        color = self.settings.get('result_font_color', '#ffffff')
        self.preview_label.setStyleSheet(f"font-family: {family}; font-size: {size}px; color: {color}; padding: 20px; background-color: #1e1f2c; border-radius: 12px;")

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings['result_font_color'] = color.name()
            self.preview()

    def apply(self):
        self.settings['result_font_size'] = self.size_slider.value()
        self.settings['result_font_family'] = self.family_combo.currentText()
        self.apply_callback()
        QMessageBox.information(self, "成功", "字体设置已保存并应用")


# ---------- 抽号动画设置面板 ----------
class AnimationSettingsPanel(QWidget):
    def __init__(self, settings, change_callback):
        super().__init__()
        self.settings = settings
        self.change_callback = change_callback
        self.setup_ui()
        self.load_values()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        self.enable_checkbox = QCheckBox("启用抽取浮动动画")
        self.enable_checkbox.toggled.connect(self.on_value_changed)
        layout.addWidget(self.enable_checkbox)

        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("动画时长 (秒):"))
        self.duration_slider = QSlider(Qt.Horizontal)
        self.duration_slider.setRange(2, 20)
        self.duration_slider.setTickInterval(2)
        self.duration_slider.valueChanged.connect(self.on_value_changed)
        self.duration_label = QLabel("0.5 s")
        duration_layout.addWidget(self.duration_slider)
        duration_layout.addWidget(self.duration_label)
        layout.addLayout(duration_layout)

        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("数字跳动速度 (毫秒/帧):"))
        self.interval_slider = QSlider(Qt.Horizontal)
        self.interval_slider.setRange(10, 100)
        self.interval_slider.valueChanged.connect(self.on_value_changed)
        self.interval_label = QLabel("30 ms")
        interval_layout.addWidget(self.interval_slider)
        interval_layout.addWidget(self.interval_label)
        layout.addLayout(interval_layout)

        layout.addStretch()
        info = QLabel("提示：动画时长越短、速度越快，跳动越急促；关闭动画则直接显示结果。")
        info.setWordWrap(True)
        info.setStyleSheet("color: #9ca3af; font-size: 12px;")
        layout.addWidget(info)

    def load_values(self):
        enabled = self.settings.get('animation_enabled', False)
        self.enable_checkbox.setChecked(enabled)

        duration = self.settings.get('animation_duration', 0.5)
        slider_val = int(duration * 10)
        self.duration_slider.setValue(slider_val)
        self.duration_label.setText(f"{duration:.1f} s")

        interval = self.settings.get('animation_interval', 30)
        self.interval_slider.setValue(interval)
        self.interval_label.setText(f"{interval} ms")

    def on_value_changed(self):
        enabled = self.enable_checkbox.isChecked()
        duration = self.duration_slider.value() / 10.0
        interval = self.interval_slider.value()
        self.duration_label.setText(f"{duration:.1f} s")
        self.interval_label.setText(f"{interval} ms")

        self.settings['animation_enabled'] = enabled
        self.settings['animation_duration'] = duration
        self.settings['animation_interval'] = interval
        self.change_callback()


# ---------- 记忆存档面板 ----------
class ArchiveManagerPanel(QWidget):
    def __init__(self, core, draw_page, student_panel):
        super().__init__()
        self.core = core
        self.draw_page = draw_page
        self.student_panel = student_panel
        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("刷新列表")
        refresh_btn.clicked.connect(self.refresh_list)
        open_folder_btn = QPushButton("打开存档文件夹")
        open_folder_btn.clicked.connect(self.open_folder)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(open_folder_btn)
        layout.addLayout(btn_layout)

        self.archive_list = QListWidget()
        self.archive_list.itemDoubleClicked.connect(self.load_archive)
        layout.addWidget(self.archive_list)

    def refresh_list(self):
        self.archive_list.clear()
        archives = self.core.list_archives()
        for path in archives:
            info = self.core.get_archive_info(path)
            if info:
                timestamp = info['timestamp'].replace('_', ' ').replace('-', ':') if '_' in info['timestamp'] else info['timestamp']
                text = f"{timestamp} | 学生: {info['student_count']} | 剩余: {info['remaining']}"
                item = QListWidgetItem(text)
                item.setData(Qt.UserRole, path)
                self.archive_list.addItem(item)
        if not archives:
            self.archive_list.addItem("暂无存档")

    def open_folder(self):
        folder = self.core.archive_dir
        if not os.path.exists(folder):
            os.makedirs(folder)
        if os.name == 'nt':
            os.startfile(folder)
        else:
            subprocess.call(["open", folder])

    def load_archive(self, item):
        path = item.data(Qt.UserRole)
        if path and os.path.exists(path):
            try:
                self.core.load_archive(path)
                self.draw_page.sync_from_core()
                self.student_panel.refresh_cards()
                QMessageBox.information(self, "成功", f"已加载存档：{os.path.basename(path)}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载存档失败：{str(e)}")
        else:
            QMessageBox.warning(self, "错误", "存档文件不存在")


# ---------- 开发者控制台面板 ----------
class DeveloperConsolePanel(QWidget):
    def __init__(self, core, command_callback):
        super().__init__()
        self.core = core
        self.command_callback = command_callback
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        input_layout = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("输入开发者命令... (如 /set(1,54) 或 v)")
        self.command_input.returnPressed.connect(self.execute)
        execute_btn = QPushButton("执行")
        execute_btn.clicked.connect(self.execute)
        clear_btn = QPushButton("清空输出")
        clear_btn.clicked.connect(self.clear_output)
        input_layout.addWidget(self.command_input)
        input_layout.addWidget(execute_btn)
        input_layout.addWidget(clear_btn)
        layout.addLayout(input_layout)

        self.output_area = QPlainTextEdit()
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        self.append_output("开发者控制台已就绪\n输入 v 查看随机排列列表，输入 /help 查看命令帮助")

    def execute(self):
        cmd = self.command_input.text().strip()
        if not cmd:
            return
        result = self.core.process_cheat_command(cmd)
        self.append_output(f"> {cmd}\n{result}")
        self.command_input.clear()
        self.command_callback()

    def append_output(self, text):
        self.output_area.appendPlainText(text)

    def clear_output(self):
        self.output_area.clear()
        self.append_output("输出已清空")


# ---------- 统计信息面板 ----------
class StatisticsPanel(QWidget):
    def __init__(self, core):
        super().__init__()
        self.core = core
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.text_area = QPlainTextEdit()
        self.text_area.setReadOnly(True)
        refresh_btn = QPushButton("刷新统计")
        refresh_btn.clicked.connect(self.refresh)
        layout.addWidget(self.text_area)
        layout.addWidget(refresh_btn)

    def refresh(self):
        info = self.core.get_statistics_info()
        self.text_area.setPlainText(info)


# ---------- 娱乐功能面板 ----------
class EntertainmentPanel(QWidget):
    def __init__(self, core, music, settings, save_callback):
        super().__init__()
        self.core = core
        self.music = music
        self.settings = settings
        self.save_callback = save_callback
        self.setup_ui()
        self.load_settings()
        self.timer = QTimer()
        self.timer.timeout.connect(self._check_music_state)
        self.timer.start(500)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("音乐文件夹:"))
        self.folder_path = QLineEdit()
        self.folder_path.setReadOnly(True)
        self.folder_path.setPlaceholderText("未选择")
        folder_btn = QPushButton("浏览")
        folder_btn.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_path)
        folder_layout.addWidget(folder_btn)
        layout.addLayout(folder_layout)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("播放模式:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["顺序播放", "随机播放", "单曲播放", "单曲循环"])
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("音量:"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.music.volume * 100))
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        volume_layout.addWidget(self.volume_slider)
        self.volume_label = QLabel(f"{int(self.music.volume*100)}%")
        volume_layout.addWidget(self.volume_label)
        layout.addLayout(volume_layout)

        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("⏮ 上一首")
        self.play_btn = QPushButton("▶ 播放")
        self.pause_btn = QPushButton("⏸ 暂停")
        self.stop_btn = QPushButton("⏹ 停止")
        self.next_btn = QPushButton("⏭ 下一首")
        self.prev_btn.clicked.connect(self.music.previous)
        self.play_btn.clicked.connect(self.music.play)
        self.pause_btn.clicked.connect(self.music.pause)
        self.stop_btn.clicked.connect(self.music.stop)
        self.next_btn.clicked.connect(self.music.next)
        for btn in (self.prev_btn, self.play_btn, self.pause_btn, self.stop_btn, self.next_btn):
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)

        self.current_track = QLabel("当前未播放")
        self.current_track.setWordWrap(True)
        layout.addWidget(self.current_track)

        self.enable_checkbox = QCheckBox("启用背景音乐")
        self.enable_checkbox.toggled.connect(self.on_enable_toggled)
        layout.addWidget(self.enable_checkbox)

        layout.addStretch()

    def load_settings(self):
        music_folder = self.settings.get('music_folder', '')
        if music_folder and os.path.exists(music_folder):
            self.folder_path.setText(music_folder)
            self.music.set_playlist(music_folder)
        self.music.set_volume(self.music.volume)
        mode_map = {"order": 0, "shuffle": 1, "single": 2, "loop_one": 3}
        current_mode = self.settings.get('music_mode', 'order')
        self.mode_combo.setCurrentIndex(mode_map.get(current_mode, 0))
        self.enable_checkbox.setChecked(self.music.enabled)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择音乐文件夹")
        if folder:
            self.folder_path.setText(folder)
            self.settings['music_folder'] = folder
            self.save_callback()
            self.music.set_playlist(folder)
            if self.music.enabled and self.music.playlist:
                self.music.play()

    def on_mode_changed(self, index):
        modes = ["order", "shuffle", "single", "loop_one"]
        mode = modes[index]
        self.music.set_mode(mode)
        self.settings['music_mode'] = mode
        self.save_callback()

    def on_volume_changed(self, value):
        vol = value / 100.0
        self.music.set_volume(vol)
        self.volume_label.setText(f"{value}%")
        self.settings['music_volume'] = vol
        self.save_callback()

    def on_enable_toggled(self, checked):
        self.music.enabled = checked
        self.settings['music_enabled'] = checked
        self.save_callback()
        if checked and self.music.playlist:
            self.music.play()
        elif not checked:
            self.music.stop()

    def _check_music_state(self):
        if self.music.enabled and self.music.playlist and not pygame.mixer.music.get_busy() and self.music.playing:
            self.music.on_finished()
        if self.music.playlist and 0 <= self.music.current_index < len(self.music.playlist):
            file = self.music.playlist[self.music.current_index]
            name = os.path.basename(file)
            status = "播放中" if self.music.playing else "暂停"
            self.current_track.setText(f"当前: {name} ({status})")
        else:
            self.current_track.setText("未选择音乐文件夹或列表为空")


# ---------- 开机自启动面板 ----------
class AutoStartPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.check_status()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.status_label = QLabel("检查中...")
        self.status_label.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(self.status_label)

        btn_layout = QHBoxLayout()
        self.enable_btn = QPushButton("设置开机自启动")
        self.enable_btn.clicked.connect(self.enable)
        self.disable_btn = QPushButton("取消开机自启动")
        self.disable_btn.clicked.connect(self.disable)
        btn_layout.addWidget(self.enable_btn)
        btn_layout.addWidget(self.disable_btn)
        layout.addLayout(btn_layout)

        info = QLabel("说明：开机自启动会在 Windows 启动时自动运行本程序。\n程序安装在D盘时，自启动会稳定指向D盘程序，不受冰点还原影响。")
        info.setWordWrap(True)
        info.setStyleSheet("color: #9ca3af; font-size: 11px;")
        layout.addWidget(info)
        layout.addStretch()

    def get_shortcut_path(self):
        startup = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
        return os.path.join(startup, "RandomDrawSystem.lnk")

    def check_status(self):
        if os.name != 'nt':
            self.status_label.setText("当前系统不是 Windows，不支持开机自启动")
            self.enable_btn.setEnabled(False)
            self.disable_btn.setEnabled(False)
            return
        try:
            shortcut_path = self.get_shortcut_path()
            if os.path.exists(shortcut_path):
                self.status_label.setText("✅ 已设置开机自启动")
            else:
                self.status_label.setText("❌ 未设置开机自启动")
        except Exception as e:
            self.status_label.setText(f"检查失败: {str(e)}")

    def enable(self):
        if os.name != 'nt':
            QMessageBox.information(self, "提示", "仅支持 Windows 系统")
            return
        try:
            main_window = self.window()
            target_path = None
            if hasattr(main_window, 'settings'):
                install_path = main_window.settings.get('install_path')
                if install_path:
                    exe_name = "智能抽号系统_v3.0_beta.exe"
                    candidate = os.path.join(install_path, exe_name)
                    if os.path.exists(candidate):
                        target_path = candidate
            if not target_path:
                if getattr(sys, 'frozen', False):
                    target_path = sys.executable
                else:
                    target_path = os.path.abspath(sys.argv[0])
            
            shell = Dispatch("WScript.Shell")
            shortcut_path = self.get_shortcut_path()
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = target_path
            shortcut.WorkingDirectory = os.path.dirname(target_path)
            shortcut.IconLocation = target_path
            shortcut.Save()
            QMessageBox.information(self, "成功", f"已设置开机自启动，目标程序：{target_path}")
            self.check_status()
        except PermissionError:
            QMessageBox.critical(self, "权限不足", "请以管理员身份运行本程序后重试")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"设置失败：{str(e)}")

    def disable(self):
        if os.name != 'nt':
            return
        try:
            shortcut_path = self.get_shortcut_path()
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                QMessageBox.information(self, "成功", "已取消开机自启动")
            else:
                QMessageBox.information(self, "提示", "未找到自启动快捷方式")
            self.check_status()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"取消失败：{str(e)}")