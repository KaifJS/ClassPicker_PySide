# ui_draw_page.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox, QCheckBox, QFrame, QMessageBox
from PySide6.QtCore import Qt, QTimer
from ui_components import AnimatedButton
import random
import os

class DrawPage(QWidget):
    def __init__(self, core, music, settings, save_callback):
        super().__init__()
        self.core = core
        self.music = music
        self.settings = settings
        self.save_callback = save_callback
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation_frame)
        self.anim_step = 0
        self.anim_results = []
        self.setup_ui()
        self.update_status()
        self.repeat_checkbox.setChecked(self.core.allow_repeat)
        self.exclude_checkbox.setChecked(self.core.exclude_after_draw)
        self.on_repeat_mode_changed(self.core.allow_repeat)

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)

        left = QFrame()
        left.setStyleSheet("background-color: #2a2b3c; border-radius: 20px;")
        left_layout = QVBoxLayout(left)
        left_layout.setSpacing(20)

        music_frame = QFrame()
        music_layout = QHBoxLayout(music_frame)
        self.music_check = QCheckBox("背景音乐")
        self.music_check.setChecked(self.music.enabled)
        self.music_check.toggled.connect(self.toggle_music)
        self.play_btn = QPushButton("播放")
        self.pause_btn = QPushButton("暂停")
        self.stop_btn = QPushButton("停止")
        self.play_btn.clicked.connect(self.music.play)
        self.pause_btn.clicked.connect(self.music.pause)
        self.stop_btn.clicked.connect(self.music.stop)
        music_layout.addWidget(self.music_check)
        music_layout.addWidget(self.play_btn)
        music_layout.addWidget(self.pause_btn)
        music_layout.addWidget(self.stop_btn)
        left_layout.addWidget(music_frame)

        count_frame = QFrame()
        count_layout = QHBoxLayout(count_frame)
        count_layout.addWidget(QLabel("每轮抽取人数:"))
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 50)
        self.count_spin.setValue(5)
        count_layout.addWidget(self.count_spin)
        left_layout.addWidget(count_frame)

        self.repeat_checkbox = QCheckBox("允许重复抽取")
        self.repeat_checkbox.toggled.connect(self.on_repeat_mode_changed)
        left_layout.addWidget(self.repeat_checkbox)

        self.exclude_checkbox = QCheckBox("抽取后排除")
        self.exclude_checkbox.toggled.connect(self.on_exclude_mode_changed)
        left_layout.addWidget(self.exclude_checkbox)

        self.draw_btn = AnimatedButton("🎯 开始抽取")
        self.draw_btn.clicked.connect(self.start_draw)
        left_layout.addWidget(self.draw_btn)

        self.reset_btn = AnimatedButton("🔄 重置记录", bg_color="#6b7280", hover_color="#4b5563")
        self.reset_btn.clicked.connect(self.reset_draw)
        left_layout.addWidget(self.reset_btn)

        self.archive_btn = AnimatedButton("💾 手动存档", bg_color="#10b981", hover_color="#059669")
        self.archive_btn.clicked.connect(self.manual_save)
        left_layout.addWidget(self.archive_btn)

        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        left_layout.addWidget(self.status_label)
        left_layout.addStretch()

        right = QFrame()
        right.setStyleSheet("background-color: #2a2b3c; border-radius: 20px;")
        right_layout = QVBoxLayout(right)
        title = QLabel("抽取结果")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        right_layout.addWidget(title)

        self.result_display = QLabel("✨ 等待抽取 ✨")
        self.result_display.setAlignment(Qt.AlignCenter)
        self.result_display.setWordWrap(True)
        self.result_display.setStyleSheet("font-size: 36px; padding: 20px; background-color: #1e1f2c; border-radius: 20px;")
        right_layout.addWidget(self.result_display, 1)

        export_btn = QPushButton("导出结果")
        export_btn.clicked.connect(self.export_results)
        right_layout.addWidget(export_btn)

        main_layout.addWidget(left, 1)
        main_layout.addWidget(right, 2)

        self.apply_font_settings()

    def on_repeat_mode_changed(self, checked):
        self.core.allow_repeat = checked
        if checked:
            self.exclude_checkbox.setEnabled(True)
        else:
            self.core.exclude_after_draw = True
            self.exclude_checkbox.setChecked(True)
            self.exclude_checkbox.setEnabled(False)
        self.update_status()

    def on_exclude_mode_changed(self, checked):
        self.core.exclude_after_draw = checked
        self.update_status()

    def apply_font_settings(self):
        family = self.settings.get('result_font_family', 'Microsoft YaHei')
        size = self.settings.get('result_font_size', 36)
        color = self.settings.get('result_font_color', '#ffffff')
        self.result_display.setStyleSheet(f"font-family: {family}; font-size: {size}px; color: {color}; padding: 20px; background-color: #1e1f2c; border-radius: 20px;")

    def toggle_music(self, checked):
        self.music.enabled = checked
        self.settings['music_enabled'] = checked
        self.save_callback()
        if checked:
            self.music.play()
        else:
            self.music.stop()

    def update_status(self):
        remaining = len(self.core.random_permutation) - self.core.current_permutation_index
        mode_desc = ""
        if not self.core.allow_repeat:
            mode_desc = f"不重复模式（剩余顺序名额: {remaining})"
        elif self.core.exclude_after_draw:
            mode_desc = f"可重复+排除模式（剩余学生: {len(self.core.students)})"
        else:
            mode_desc = "真随机模式（可重复）"
        self.status_label.setText(f"学生总数: {len(self.core.students)}  已抽取: {self.core.total_draws_count}  模式: {mode_desc}")

    def start_draw(self):
        if not self.core.students:
            QMessageBox.warning(self, "警告", "请先在设置中添加学生名单")
            return
        count = self.count_spin.value()
        selected = self.core.draw(count, parent_window=self)
        if not selected:
            QMessageBox.information(self, "提示", "抽取失败，人数不足且用户取消重置")
            return
        # 根据设置决定是否播放动画
        if self.settings.get('animation_enabled', False):
            self._play_animation(selected)
        else:
            # 直接显示结果
            self.result_display.setText(" ".join(selected))
            self.update_status()

    def _play_animation(self, results):
        duration = self.settings.get('animation_duration', 0.5)
        interval = self.settings.get('animation_interval', 30)
        total_frames = max(1, int(duration * 1000 / interval))
        self.anim_results = results
        self.anim_current_frame = 0
        self.anim_total_frames = total_frames
        if self.animation_timer.isActive():
            self.animation_timer.stop()
        self.animation_timer.start(interval)

    def _update_animation_frame(self):
        if self.anim_current_frame < self.anim_total_frames:
            fake = [str(random.randint(1, 999)) for _ in self.anim_results]
            self.result_display.setText(" ".join(fake))
            self.anim_current_frame += 1
        else:
            self.animation_timer.stop()
            self.result_display.setText(" ".join(self.anim_results))
            self.update_status()

    def reset_draw(self):
        self.core.reset()
        self.result_display.setText("✨ 记录已重置 ✨")
        self.update_status()

    def manual_save(self):
        if not self.core.random_permutation:
            QMessageBox.warning(self, "警告", "没有可保存的随机排列，请先设置学生名单")
            return
        filepath = self.core.save_archive()
        if filepath:
            QMessageBox.information(self, "成功", f"已手动存档到：{os.path.basename(filepath)}")
        else:
            QMessageBox.critical(self, "错误", "存档保存失败")

    def export_results(self):
        try:
            filename = self.core.export_results()
            QMessageBox.information(self, "成功", f"结果已导出到: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def sync_from_core(self):
        self.repeat_checkbox.setChecked(self.core.allow_repeat)
        self.exclude_checkbox.setChecked(self.core.exclude_after_draw)
        self.on_repeat_mode_changed(self.core.allow_repeat)
        self.update_status()
        self.result_display.setText("✨ 已加载存档 ✨")