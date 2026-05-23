from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QColor

class AnimatedButton(QPushButton):
    """带动画的按钮"""
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
        """)
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(100)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event):
        geo = self.geometry()
        self._animation.setStartValue(geo)
        geo.setHeight(geo.height() + 2)
        geo.setWidth(geo.width() + 5)
        self._animation.setEndValue(geo)
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        geo = self.geometry()
        self._animation.setStartValue(geo)
        geo.setHeight(geo.height() - 2)
        geo.setWidth(geo.width() - 5)
        self._animation.setEndValue(geo)
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