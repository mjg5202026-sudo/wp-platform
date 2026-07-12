"""
便利贴待办工具 — 主程序入口

功能:
  - 桌面便利贴样式待办列表
  - 固定在桌面右上角
  - 开机自启动
  - 数据本地 SQLite 存储
  - 已完成任务历史记录
  - 拖动记忆位置

技术栈: Python + PySide6 + SQLite
"""

import sys
import os
import winreg

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from database import init_db
from todo_widget import StickyNote


APP_NAME = "StickyNotesTodo"
REG_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def set_auto_start(enable: bool = True):
    """Add or remove this app from Windows startup."""
    exe_path = sys.argv[0]
    if not exe_path.endswith(".exe"):
        # Running as script — skip auto-start registration
        return

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REG_KEY_PATH,
            0,
            winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE,
        )
        try:
            winreg.QueryValueEx(key, APP_NAME)
            already_set = True
        except FileNotFoundError:
            already_set = False

        if enable and not already_set:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
        elif not enable and already_set:
            winreg.DeleteValue(key, APP_NAME)

        winreg.CloseKey(key)
    except Exception:
        pass  # Silently ignore registry errors


def main():
    # Initialize database
    init_db()

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("StickyNotes")

    # Set default font for CJK support
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)

    # Set global style
    app.setStyle("Fusion")

    # Enable high-DPI scaling
    app.setStyleSheet("""
        QToolTip {
            background-color: #FFF9C4;
            color: #3E2723;
            border: 1px solid #E6C34A;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 12px;
        }
    """)

    # Register auto-start (only when running as EXE)
    set_auto_start(True)

    # Launch main window
    window = StickyNote()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
