# main.py
import sys
from PySide6.QtWidgets import QApplication
from ui_main_window import MainWindow

# ========== 默认学生名单（与 name.txt 内容一致） ==========
DEFAULT_STUDENTS = [
    "01.(高宇辰)", "02.(臧庆宇)", "03.(郁永涛)", "04.(殷浩)", "05.(王鑫园)",
    "06.(李潇)", "07.(陈阳)", "08.(张昊)", "09.(邬成运)", "10.(余自强)",
    "11.(耿鹏)", "12.(洪先耀)", "13.(沈明春)", "14.(王犇)", "15.(祁永旭)",
    "16.(方启源)", "17.(孙博奥)", "18.(许明萱)", "19.(王鹏程)", "20.(陈永恒)",
    "21.(崔传信)", "22.(胡文乐)", "23.(李松泽)", "24.(郑俊贤)", "25.(殷乾杭)",
    "26.(朱家豪)", "27.(程坤)", "28.(陈浩运)", "29.(郑灿强)", "30.(左雅洁)",
    "31.(任远明慧)", "32.(李美玲)", "33.(简晓丹)", "34.(张丽)", "35.(何彤萱)",
    "36.(蔡栉垠)", "37.(张彤彤)", "38.(王雯雯)", "39.(徐豫滇)", "40.(李思含)",
    "41.(任滢滢)", "42.(王欣茹)", "43.(章清风)", "44.(杨默含)", "45.(陈西雨)",
    "46.(王晶晶)", "47.(郭雅婷)", "48.(丁曼玲)", "49.(祁爱婷)", "50.(梁雅琦)",
    "51.(刘姝涵)", "52.(李若素)", "53.(朱妍润)", "54.(简子倩)", "55.(郑梦圆)"
]

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("智能抽号系统 v3.0 - PySide6 完全版")
    # 全局样式表（暗黑风格）
    app.setStyleSheet("""
        QMainWindow { background-color: #1e1f2c; }
        QWidget { background-color: #1e1f2c; color: #e5e7eb; }
        QPushButton {
            background-color: #3b82f6;
            border: none;
            border-radius: 6px;
            padding: 6px 12px;
            color: white;
            font-weight: bold;
        }
        QPushButton:hover { background-color: #2563eb; }
        QPushButton:pressed { background-color: #1d4ed8; }
        QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox {
            background-color: #2d2e3e;
            border: 1px solid #4b4c5e;
            border-radius: 4px;
            padding: 4px;
            color: #e5e7eb;
        }
        QListWidget {
            background-color: #2a2b3c;
            border: none;
            outline: none;
        }
        QListWidget::item {
            padding: 8px;
            color: #cbd5e1;
        }
        QListWidget::item:selected {
            background-color: #3b82f6;
            color: white;
        }
        QScrollArea { border: none; background: transparent; }
        QScrollBar:vertical {
            background: #2a2b3c;
            width: 10px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical {
            background: #4b4c5e;
            border-radius: 5px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover { background: #6b6c7e; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
    """)
    window = MainWindow(default_students=DEFAULT_STUDENTS)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()