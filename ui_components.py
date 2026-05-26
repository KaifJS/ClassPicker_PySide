# ui_components.py
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QColor

class RoundShadowWidget(QFrame):
    """圆角阴影容器 (可选，未在主界面使用但保留)"""
    def __init__(self, parent=None, radius=10, color="#2a2b3c"):
        super().__init__(parent)
        self.setObjectName("RoundShadow")
        self.setStyleSheet(f"#RoundShadow {{ background-color: {color}; border-radius: {radius}px; }}")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

class AnimatedButton(QPushButton):
    """带动画的按钮 - 修复悬停缩放漂移问题"""
    def __init__(self, text="", parent=None, bg_color="#3b82f6", hover_color="#2563eb"):
        super().__init__(text, parent)
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(hover_color)};
            }}
        """)
        # 记录原始大小
        self.original_geometry = None
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(100)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)

    def darken_color(self, color):
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            r = max(0, r - 30)
            g = max(0, g - 30)
            b = max(0, b - 30)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color

    def showEvent(self, event):
        """确保在首次显示时记录原始几何"""
        super().showEvent(event)
        if self.original_geometry is None:
            self.original_geometry = self.geometry()

    def enterEvent(self, event):
        if self.original_geometry is None:
            self.original_geometry = self.geometry()
        # 基于原始几何计算放大后的矩形
        enlarged = QRect(
            self.original_geometry.x() - 2,      # 向左偏移2，保持中心
            self.original_geometry.y() - 1,
            self.original_geometry.width() + 5,
            self.original_geometry.height() + 2
        )
        self._animation.setStartValue(self.geometry())
        self._animation.setEndValue(enlarged)
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.original_geometry is None:
            self.original_geometry = self.geometry()
        self._animation.setStartValue(self.geometry())
        self._animation.setEndValue(self.original_geometry)
        self._animation.start()
        super().leaveEvent(event)

class CardWidget(QFrame):
    """人员卡片"""
    def __init__(self, text="", parent=None, selected=False):
        super().__init__(parent)
        self.setFixedSize(120, 80)
        self.setObjectName("Card")
        self.selected = selected
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(0, 0, 120, 80)
        self.update_style()

    def update_style(self):
        if self.selected:
            self.setStyleSheet("""
                QFrame#Card {
                    background-color: #3b82f6;
                    border-radius: 12px;
                    border: 2px solid #2563eb;
                }
                QFrame#Card:hover { background-color: #2563eb; }
            """)
            self.label.setStyleSheet("color: white; background: transparent; font-size: 14px;")
        else:
            self.setStyleSheet("""
                QFrame#Card {
                    background-color: #3b3c4e;
                    border-radius: 12px;
                    border: 1px solid #4b4c5e;
                }
                QFrame#Card:hover { background-color: #4b4c5e; }
            """)
            self.label.setStyleSheet("color: #e5e7eb; background: transparent; font-size: 14px;")

    def set_selected(self, selected):
        self.selected = selected
        self.update_style()