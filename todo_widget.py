"""
Sticky note main widget — the todo list UI.

Features:
  - Numbered task list with auto-renumber
  - Checkbox completion with fade-out
  - Minimize to system tray
  - Screen edge auto-collapse (sidebar style)
  - History with restore capability
"""

import sys
import os

from PySide6.QtCore import (
    Qt, QPoint, QSize, Signal, QPropertyAnimation,
    QEasingCurve, QTimer, QRect
)
from PySide6.QtGui import QFont, QIcon, QColor, QCursor, QPixmap, QPainter
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QCheckBox,
    QLineEdit, QApplication, QMenu, QDialog, QListWidget,
    QListWidgetItem, QTextEdit, QMainWindow, QToolTip, QSizePolicy,
    QMessageBox, QSystemTrayIcon, QAbstractItemView
)

from database import (
    get_active_tasks, add_task, complete_task, restore_task,
    get_completed_tasks, get_setting, set_setting,
)


# ── Constants ────────────────────────────────────────────────────

CANARY_YELLOW       = "#FFF9C4"
CANARY_YELLOW_DARKER = "#FFF59D"
CANARY_YELLOW_HEADER = "#F0E68C"
TEXT_COLOR          = "#3E2723"
TEXT_SECONDARY      = "#5D4037"
DIVIDER_COLOR       = "#E6C34A"
HOVER_BG            = "#FFF176"
BUTTON_COLOR        = "#F9A825"
NUMBER_COLOR        = "#BCAAA4"

EXPANDED_WIDTH      = 320
COLLAPSED_WIDTH     = 14
COLLAPSE_THRESHOLD  = 20
COLLAPSE_EDGE_MARGIN = 8
COLLAPSE_HIDE_DELAY = 1200  # ms before auto-collapse after mouse leaves


# ── Task Item Widget ──────────────────────────────────────────────

class TaskItem(QFrame):
    """A single todo row: number + checkbox + text."""

    task_completed = Signal(int)

    def __init__(self, task_id: int, index: int, content: str, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self._setup_ui(index, content)

    def _setup_ui(self, index: int, content: str):
        self.setObjectName("taskItem")
        self.setStyleSheet(f"""
            #taskItem {{
                background-color: transparent;
                border: none;
                border-bottom: 1px solid {DIVIDER_COLOR};
                padding: 4px 0;
            }}
            #taskItem:hover {{
                background-color: {HOVER_BG};
                border-radius: 4px;
            }}
        """)
        self.setCursor(Qt.CursorShape.ArrowCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 8, 4)
        layout.setSpacing(6)

        # Number label
        self.number_label = QLabel(str(index))
        self.number_label.setFixedWidth(22)
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.number_label.setStyleSheet(f"""
            QLabel {{
                color: {NUMBER_COLOR};
                font-size: 12px;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
                font-weight: bold;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(self.number_label)

        # Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet(f"""
            QCheckBox {{
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {BUTTON_COLOR};
                border-radius: 4px;
                background-color: white;
            }}
            QCheckBox::indicator:hover {{
                background-color: #FFF9C4;
            }}
            QCheckBox::indicator:checked {{
                background-color: {BUTTON_COLOR};
                border: 2px solid {BUTTON_COLOR};
            }}
        """)
        self.checkbox.setToolTip("标记为已完成")
        self.checkbox.stateChanged.connect(self._on_check)
        layout.addWidget(self.checkbox)

        # Task text
        self.label = QLabel(content)
        self.label.setWordWrap(True)
        self.label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 14px;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
                background: transparent;
                border: none;
                padding: 2px 0;
            }}
        """)
        self.label.setCursor(Qt.CursorShape.IBeamCursor)
        layout.addWidget(self.label, 1)

    def set_number(self, index: int):
        """Update the displayed number."""
        self.number_label.setText(str(index))

    def _on_check(self, state):
        if state == 2:  # Qt.Checked
            self._fade_out()

    def _fade_out(self):
        self.setStyleSheet(f"""
            #taskItem {{
                background-color: transparent;
                border: none;
                border-bottom: 1px solid {DIVIDER_COLOR};
            }}
        """)
        QTimer.singleShot(300, lambda: self.task_completed.emit(self.task_id))


# ── Add Task Input ────────────────────────────────────────────────

class AddTaskBar(QFrame):
    """The input bar at bottom with + button and inline editor."""

    task_added = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._editing = False
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("addTaskBar")
        self.setStyleSheet(f"""
            #addTaskBar {{
                background-color: {CANARY_YELLOW_DARKER};
                border: none;
                border-radius: 6px;
                padding: 2px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(6)

        # "+" button
        self.add_btn = QPushButton("＋")
        self.add_btn.setFixedSize(28, 28)
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_COLOR};
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #F57F17;
            }}
            QPushButton:pressed {{
                background-color: #E65100;
            }}
        """)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.clicked.connect(self._start_editing)
        layout.addWidget(self.add_btn)

        # Inline editor (hidden by default)
        self.editor = QLineEdit()
        self.editor.setPlaceholderText("输入待办事项...")
        self.editor.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid {BUTTON_COLOR};
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 14px;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
                color: {TEXT_COLOR};
                background-color: white;
                selection-background-color: #FFE082;
            }}
        """)
        self.editor.returnPressed.connect(self._confirm)
        self.editor.hide()
        layout.addWidget(self.editor, 1)

    def _start_editing(self):
        self.add_btn.hide()
        self.editor.show()
        self.editor.setFocus()
        self.editor.clear()
        self._editing = True

    def _confirm(self):
        text = self.editor.text().strip()
        if text:
            self.task_added.emit(text)
        self._stop_editing()

    def _stop_editing(self):
        self.editor.hide()
        self.editor.clear()
        self.add_btn.show()
        self._editing = False

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self._editing:
            self._stop_editing()


# ── Main Sticky Note Widget ──────────────────────────────────────

class StickyNote(QMainWindow):
    """The main sticky note window pinned to top-right of desktop."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("便利贴")
        # Collapse state
        self._collapsed = False
        self._normal_geometry = None
        self._collapse_timer = None
        self._collapse_right_x = None
        self._collapse_top_y = None

        self._setup_window_flags()
        self._build_ui()
        self._load_position()
        self._refresh_tasks()
        self._setup_tray_icon()

    def _setup_window_flags(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        # Enable mouse tracking for hover events on collapsed window
        self.setMouseTracking(True)

    def _build_ui(self):
        # Main container
        self.central = QWidget()
        self.central.setObjectName("centralWidget")
        self.central.setStyleSheet(f"""
            #centralWidget {{
                background-color: {CANARY_YELLOW};
                border: 1px solid {DIVIDER_COLOR};
                border-radius: 10px;
            }}
        """)
        # Enable mouse tracking on central widget for hover during collapse
        self.central.setMouseTracking(True)
        self.setCentralWidget(self.central)

        # Main layout
        main_layout = QVBoxLayout(self.central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ═══ Header (drag handle) ═══
        self._build_header(main_layout)

        # ═══ Task list ═══
        self._build_task_list(main_layout)

        # ═══ Add task bar ═══
        self._build_add_bar(main_layout)

        # Window size
        self.setFixedWidth(EXPANDED_WIDTH)
        self.adjust_height()

        # Drag state
        self._dragging = False
        self._drag_pos = QPoint()

    def _build_header(self, parent_layout):
        header = QFrame()
        header.setObjectName("header")
        header.setStyleSheet(f"""
            #header {{
                background-color: {CANARY_YELLOW_HEADER};
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom: 2px solid {DIVIDER_COLOR};
            }}
        """)
        header.setCursor(Qt.CursorShape.SizeAllCursor)
        header.setFixedHeight(40)
        header.setMouseTracking(True)

        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(12, 4, 8, 4)
        h_layout.setSpacing(6)

        # App icon / title
        icon_label = QLabel("📌")
        icon_label.setStyleSheet("font-size: 16px; background: transparent;")
        h_layout.addWidget(icon_label)

        title = QLabel("便利贴")
        title_font = QFont("Microsoft YaHei", 12, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {TEXT_COLOR}; background: transparent;")
        h_layout.addWidget(title)

        h_layout.addStretch(1)

        # History button
        history_btn = QPushButton("📋")
        history_btn.setFixedSize(28, 28)
        history_btn.setToolTip("查看历史记录")
        history_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 14px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {HOVER_BG};
            }}
        """)
        history_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        history_btn.clicked.connect(self._show_history)
        h_layout.addWidget(history_btn)

        # Minimize button
        minimize_btn = QPushButton("─")
        minimize_btn.setFixedSize(28, 28)
        minimize_btn.setToolTip("最小化到托盘")
        minimize_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 14px;
                font-size: 14px;
                color: {TEXT_COLOR};
            }}
            QPushButton:hover {{
                background-color: {BUTTON_COLOR};
                color: white;
            }}
        """)
        minimize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        minimize_btn.clicked.connect(self._minimize_to_tray)
        h_layout.addWidget(minimize_btn)

        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setToolTip("退出")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 14px;
                font-size: 14px;
                color: {TEXT_COLOR};
            }}
            QPushButton:hover {{
                background-color: #EF5350;
                color: white;
            }}
        """)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self._quit_app)
        h_layout.addWidget(close_btn)

        parent_layout.addWidget(header)

    def _build_task_list(self, parent_layout):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollArea * {{
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                width: 6px;
                background: transparent;
            }}
            QScrollBar::handle:vertical {{
                background-color: {DIVIDER_COLOR};
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)
        scroll_area.setMouseTracking(True)

        # Container inside scroll area
        self.task_container = QWidget()
        self.task_container.setStyleSheet("background-color: transparent;")
        self.task_container.setMouseTracking(True)
        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setContentsMargins(4, 4, 4, 4)
        self.task_layout.setSpacing(0)
        self.task_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # Placeholder label
        self.empty_label = QLabel("✨ 还没有待办事项\n点击「＋」添加新任务")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: 13px;
                font-family: 'Microsoft YaHei', sans-serif;
                background: transparent;
                padding: 30px 10px;
                border: none;
            }}
        """)
        self.task_layout.addWidget(self.empty_label)

        scroll_area.setWidget(self.task_container)
        parent_layout.addWidget(scroll_area, 1)

    def _build_add_bar(self, parent_layout):
        bar_frame = QFrame()
        bar_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {CANARY_YELLOW_DARKER};
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
                border-top: 1px solid {DIVIDER_COLOR};
                padding: 4px;
            }}
        """)
        bar_frame.setMouseTracking(True)
        bar_layout = QVBoxLayout(bar_frame)
        bar_layout.setContentsMargins(6, 4, 6, 6)
        bar_layout.setSpacing(2)

        self.add_bar = AddTaskBar()
        self.add_bar.task_added.connect(self._on_task_added)
        bar_layout.addWidget(self.add_bar)

        # Footer tip
        tip = QLabel("按 Enter 快速添加")
        tip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tip.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: 11px;
                background: transparent;
                border: none;
                padding: 0;
            }}
        """)
        bar_layout.addWidget(tip)

        parent_layout.addWidget(bar_frame)

    # ── Task management ───────────────────────────────────────────

    def _on_task_added(self, content: str):
        add_task(content)
        self._refresh_tasks()

    def _on_task_completed(self, task_id: int):
        complete_task(task_id)
        self._refresh_tasks()

    def _refresh_tasks(self):
        self._clear_task_list()
        tasks = get_active_tasks()
        if not tasks:
            self.task_layout.addWidget(self.empty_label)
        else:
            for i, t in enumerate(tasks, start=1):
                item = TaskItem(t["id"], i, t["content"])
                item.task_completed.connect(self._on_task_completed)
                self.task_layout.addWidget(item)
        self.task_layout.addStretch()
        self.adjust_height()

    def _clear_task_list(self):
        while self.task_layout.count():
            item = self.task_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def adjust_height(self):
        """Auto-adjust window height based on content."""
        if self._collapsed:
            return
        task_count = len(get_active_tasks())
        item_height = max(task_count, 1) * 48
        new_h = min(max(200, 80 + item_height), 600)
        self.setFixedHeight(new_h)

    # ── History ───────────────────────────────────────────────────

    def _show_history(self):
        dlg = HistoryDialog(self)
        dlg.finished.connect(lambda: self._refresh_tasks())
        dlg.exec()

    # ── Minimize / Tray ───────────────────────────────────────────

    def _setup_tray_icon(self):
        """Create system tray icon for minimize/restore."""
        self.tray_icon = QSystemTrayIcon(self)
        # Create a simple colored icon programmatically
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(CANARY_YELLOW_HEADER))
        painter = QPainter(pixmap)
        painter.setPen(QColor(BUTTON_COLOR))
        painter.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        painter.drawText(QRect(0, 0, 32, 32), Qt.AlignmentFlag.AlignCenter, "📌")
        painter.end()
        self.tray_icon.setIcon(QIcon(pixmap))
        self.tray_icon.setToolTip("便利贴")

        # Tray menu
        tray_menu = QMenu()
        show_action = tray_menu.addAction("显示 / 隐藏")
        show_action.triggered.connect(self._toggle_visible)
        tray_menu.addSeparator()
        quit_action = tray_menu.addAction("退出")
        quit_action.triggered.connect(self._quit_app)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._toggle_visible()

    def _minimize_to_tray(self):
        self.hide()

    def _toggle_visible(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            # If collapsed, re-check edge position
            if self._collapsed:
                self._expand_from_collapse()

    def _quit_app(self):
        self._save_position()
        self.tray_icon.hide()
        QApplication.quit()

    # ── Screen edge collapse ──────────────────────────────────────

    def _check_edge_collapse(self):
        """After drag end, check if window is near right screen edge → collapse."""
        if self._collapsed:
            return
        screen = QApplication.primaryScreen()
        if not screen:
            return
        sgeom = screen.availableGeometry()
        win_right = self.pos().x() + self.width()
        screen_right = sgeom.right()

        distance_to_right = screen_right - win_right
        if 0 <= distance_to_right <= COLLAPSE_THRESHOLD:
            self._normal_geometry = self.geometry()
            self._collapse_right_x = screen_right
            self._collapse_top_y = self.pos().y()
            self._do_collapse()

    def _do_collapse(self):
        """Collapse to a thin strip at the right edge."""
        self._collapsed = True
        # Hide content widgets
        self._set_content_visible(False)
        # Shrink window
        collapsed_w = COLLAPSED_WIDTH
        collapsed_x = self._collapse_right_x - collapsed_w + 1
        self.setFixedWidth(collapsed_w)
        self.move(collapsed_x, self._collapse_top_y)
        self.setFixedHeight(120)  # Compact height when collapsed

    def _set_content_visible(self, visible: bool):
        """Show or hide scroll area and add bar."""
        for i in range(self.central.layout().count()):
            item = self.central.layout().itemAt(i)
            if item.widget():
                widget = item.widget()
                # Don't hide the header
                if widget.objectName() != "header":
                    widget.setVisible(visible)

    def _expand_from_collapse(self):
        """Restore window to normal expanded state."""
        if not self._collapsed:
            return
        self._collapsed = False
        # Restore content
        self._set_content_visible(True)
        # Restore geometry
        if self._normal_geometry:
            self.setFixedWidth(EXPANDED_WIDTH)
            self.setGeometry(self._normal_geometry)
        self.adjust_height()
        self._normal_geometry = None
        self._collapse_right_x = None

    def enterEvent(self, event):
        """Mouse enters the window — expand if collapsed."""
        if self._collapsed:
            self._expand_from_collapse()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Mouse leaves the window — start collapse timer."""
        if not self._collapsed and self._should_collapse():
            self._start_collapse_timer()
        super().leaveEvent(event)

    def _should_collapse(self):
        """Check if window position is near the right screen edge."""
        screen = QApplication.primaryScreen()
        if not screen:
            return False
        sgeom = screen.availableGeometry()
        win_right = self.pos().x() + self.width()
        screen_right = sgeom.right()
        distance = screen_right - win_right
        return 0 <= distance <= COLLAPSE_EDGE_MARGIN + 10

    def _start_collapse_timer(self):
        """Start timer to auto-collapse after mouse leaves."""
        self._cancel_collapse_timer()
        self._collapse_timer = QTimer(self)
        self._collapse_timer.setSingleShot(True)
        self._collapse_timer.timeout.connect(self._on_collapse_timeout)
        self._collapse_timer.start(COLLAPSE_HIDE_DELAY)

    def _cancel_collapse_timer(self):
        if self._collapse_timer:
            self._collapse_timer.stop()
            self._collapse_timer = None

    def _on_collapse_timeout(self):
        self._collapse_timer = None
        if not self._collapsed and self._should_collapse():
            screen = QApplication.primaryScreen()
            if not screen:
                return
            sgeom = screen.availableGeometry()
            self._normal_geometry = self.geometry()
            self._collapse_right_x = sgeom.right()
            self._collapse_top_y = self.pos().y()
            self._do_collapse()

    # ── Window dragging ───────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self._collapsed:
            self._cancel_collapse_timer()
            header = self.findChild(QFrame, "header")
            if header and header.geometry().contains(event.position().toPoint()):
                self._dragging = True
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if self._dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._dragging = False
            self._save_position()
            # Check for edge collapse
            self._check_edge_collapse()
            event.accept()

    # ── Position persistence ──────────────────────────────────────

    def _save_position(self):
        pos = self.pos()
        set_setting("window_x", str(pos.x()))
        set_setting("window_y", str(pos.y()))

    def _load_position(self):
        x = get_setting("window_x")
        y = get_setting("window_y")
        if x and y:
            self.move(int(x), int(y))
        else:
            # Default: top-right corner
            screen = QApplication.primaryScreen()
            if screen:
                geom = screen.availableGeometry()
                self.move(geom.width() - self.width() - 20, 80)
            else:
                self.move(100, 80)

    def closeEvent(self, event):
        self._save_position()
        self.tray_icon.hide()
        event.accept()


# ── History Dialog ────────────────────────────────────────────────

class HistoryDialog(QDialog):
    """Dialog showing completed tasks with restore ability."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("已完成任务")
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setFixedSize(420, 480)
        self._setup_ui()
        self._load_history()

    def _setup_ui(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {CANARY_YELLOW};
                border: 1px solid {DIVIDER_COLOR};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Title
        title = QLabel("📋 已完成任务")
        title_font = QFont("Microsoft YaHei", 14, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {TEXT_COLOR}; background: transparent;")
        layout.addWidget(title)

        # Subtitle hint
        hint = QLabel("双击任务可恢复到待办列表")
        hint.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; background: transparent; border: none;")
        layout.addWidget(hint)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet(f"background-color: {DIVIDER_COLOR}; border: none;")
        layout.addWidget(sep)

        # List
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(False)
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
                font-size: 13px;
                color: {TEXT_COLOR};
            }}
            QListWidget::item {{
                border-bottom: 1px solid {DIVIDER_COLOR};
                padding: 8px 4px;
            }}
            QListWidget::item:hover {{
                background-color: {HOVER_BG};
                border-radius: 4px;
            }}
        """)
        # Double-click to restore
        self.list_widget.itemDoubleClicked.connect(self._restore_selected)
        layout.addWidget(self.list_widget, 1)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        # Restore selected button
        restore_btn = QPushButton("↩ 恢复选中")
        restore_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_COLOR};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #F57F17;
            }}
        """)
        restore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restore_btn.clicked.connect(self._restore_selected)
        btn_layout.addWidget(restore_btn)

        # Restore all button
        restore_all_btn = QPushButton("↩ 恢复全部")
        restore_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_COLOR};
                border: 1px solid {BUTTON_COLOR};
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {HOVER_BG};
            }}
        """)
        restore_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restore_all_btn.clicked.connect(self._restore_all)
        btn_layout.addWidget(restore_all_btn)

        btn_layout.addStretch(1)

        clear_btn = QPushButton("清空历史")
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_SECONDARY};
                border: 1px solid {DIVIDER_COLOR};
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #EF5350;
                color: white;
                border-color: #EF5350;
            }}
        """)
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(self._clear_history)
        btn_layout.addWidget(clear_btn)

        layout.addLayout(btn_layout)

        # Close button at bottom
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_COLOR};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 32px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #F57F17;
            }}
        """)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def _load_history(self):
        self.list_widget.clear()
        tasks = get_completed_tasks()
        if not tasks:
            item = QListWidgetItem(" 暂无已完成的任务")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            item.setForeground(QColor(TEXT_SECONDARY))
            self.list_widget.addItem(item)
        else:
            for t in tasks:
                text = f"✅ {t['content']}"
                subtitle = f"   完成于: {t['completed_at']}"
                display = f"{text}\n{subtitle}"
                item = QListWidgetItem(display)
                item.setData(Qt.ItemDataRole.UserRole, t["id"])
                self.list_widget.addItem(item)

    def _restore_selected(self):
        """Restore the selected task back to active."""
        current = self.list_widget.currentItem()
        if not current:
            QMessageBox.information(self, "提示", "请先选择一个任务")
            return
        task_id = current.data(Qt.ItemDataRole.UserRole)
        if task_id:
            restore_task(task_id)
            self._load_history()

    def _restore_all(self):
        """Restore all completed tasks back to active."""
        tasks = get_completed_tasks()
        if not tasks:
            QMessageBox.information(self, "提示", "没有可恢复的任务")
            return
        for t in tasks:
            restore_task(t["id"])
        self._load_history()

    def _clear_history(self):
        reply = QMessageBox.question(
            self, "确认清空", "确定要清空所有历史记录吗？\n此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from database import get_connection
            conn = get_connection()
            try:
                conn.execute("DELETE FROM tasks WHERE is_completed = 1")
                conn.commit()
            finally:
                conn.close()
            self._load_history()
