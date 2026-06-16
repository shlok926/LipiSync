# ui.py — Main PyQt6 Application Window (v2.0 with all 10 features)

import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QTextEdit, QComboBox, QFileDialog, QScrollArea,
    QFrame, QSplitter, QStackedWidget, QListWidget, QListWidgetItem,
    QSizePolicy, QMessageBox, QSpinBox, QSlider, QCheckBox, QProgressBar,
    QTabWidget, QTableWidget, QTableWidgetItem, QDialogButtonBox, QDialog,
    QLineEdit, QApplication
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPixmap, QFontDatabase

# Matplotlib for embedded charts in StatisticsPage
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
except Exception:
    Figure = None
    FigureCanvas = None

from braille_engine import text_to_braille, braille_to_text, get_braille_cells
from ocr_module import detect_braille_from_image
import os
from settings_manager import settings_manager

# Theme and color constants (used in styles)
ACCENT_GREEN = "#4FB69F"
ACCENT_BLUE = "#5AA6FF"
TEXT_MUTED = "#6b6f9a"
TEXT_PRIMARY = "#e6eef8"
CARD_BG = "#0f1720"
PANEL_BG = "#0b0d12"
BORDER_COL = "#1e2230"
DANGER_COL = "#ff6b6b"

# Import all new feature modules
from accessibility_features import announcer, announce, BlindUserHelper
from accessibility_features import KeyboardShortcutManager
from audio_feedback import audio_engine
from history_favorites import history_manager, favorites_manager
from clipboard_manager import clipboard_manager
from braille_grades import grade_converter
from math_notation import math_converter
from document_processor import doc_processor
from braille_learning import learning_tracker, LearningCurriculum, BrailleQuiz
from accessibility_audit import auditor

# Minimal stylesheet placeholder (was a large QSS string in the original ui)
STYLESHEET = """
QWidget { background: #0b0d12; color: #e6eef8; }
QLabel { background: transparent; }

/* Sidebar Background */
#sidebar {
    background-color: #07090e;
    border-right: 1px solid #141822;
}

/* Sidebar Navigation List Styling */
QListWidget {
    background: transparent;
    border: none;
    outline: none;
}
QListWidget::item {
    color: #8b92b6;
    background-color: transparent;
    border-radius: 6px;
    padding-left: 15px;
    margin: 2px 10px;
}
QListWidget::item:hover {
    background-color: #111520;
    color: #e6eef8;
}
QListWidget::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #8b5cf6);
    color: #ffffff;
    font-weight: bold;
}

/* Slim scrollbar for Navigation */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 5px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #1e2230;
    min-height: 20px;
    border-radius: 2px;
}
QScrollBar::handle:vertical:hover {
    background: #3b82f6;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

/* Global QSpinBox styling */
QSpinBox {
    background-color: #141b25;
    color: #e6eef8;
    border: 1px solid #1e2230;
    border-radius: 6px;
    padding: 5px 10px;
    padding-right: 20px;
}
QSpinBox:hover {
    border-color: #4FB69F;
}
QSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 18px;
    border-left: 1px solid #1e2230;
    border-top-right-radius: 6px;
    background: #1c2331;
}
QSpinBox::up-button:hover {
    background: #242c3e;
}
QSpinBox::up-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 4px solid #4FB69F;
    width: 0;
    height: 0;
}
QSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 18px;
    border-left: 1px solid #1e2230;
    border-bottom-right-radius: 6px;
    background: #1c2331;
}
QSpinBox::down-button:hover {
    background: #242c3e;
}
QSpinBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid #4FB69F;
    width: 0;
    height: 0;
}

/* Global QComboBox styling */
QComboBox {
    background-color: #141b25;
    color: #e6eef8;
    border: 1px solid #1e2230;
    border-radius: 6px;
    padding: 5px 10px;
    padding-right: 25px;
}
QComboBox:hover {
    border-color: #4FB69F;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #1e2230;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
    background: #1c2331;
}
QComboBox::drop-down:hover {
    background: #242c3e;
}
QComboBox::drop-down:pressed {
    background: #141b25;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid #4FB69F;
    width: 0;
    height: 0;
}
QComboBox QAbstractItemView {
    background-color: #141b25;
    color: #e6eef8;
    border: 1px solid #1e2230;
    selection-background-color: #1a2230;
    selection-color: #4FB69F;
    outline: none;
}
"""

# Dark background constant used by charts
DARK_BG = "#071017"


# Minimal Braille visualization widgets (lightweight placeholders)
class BrailleCellWidget(QWidget):
    def __init__(self, dots=None, parent=None):
        super().__init__(parent)
        self.dots = dots or [False, False, False, False, False, False]
        self.setMinimumSize(24, 36)

    def set_dots(self, dots):
        self.dots = dots
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        dot_w = w / 3.0
        dot_h = h / 3.5
        radius = min(dot_w, dot_h) / 4
        positions = [
            (dot_w * 0.5, dot_h * 0.8),
            (dot_w * 0.5, dot_h * 1.8),
            (dot_w * 0.5, dot_h * 2.8),
            (dot_w * 1.5, dot_h * 0.8),
            (dot_w * 1.5, dot_h * 1.8),
            (dot_w * 1.5, dot_h * 2.8),
        ]
        for i, pos in enumerate(positions):
            x, y = pos
            color = QColor(ACCENT_GREEN if self.dots[i] else '#2b2f3a')
            painter.setBrush(color)
            painter.setPen(QPen(color))
            painter.drawEllipse(int(x - radius), int(y - radius), int(radius * 2), int(radius * 2))


class BrailleDisplayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 10, 15, 10)
        self.layout.setSpacing(15)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setMinimumHeight(110)

    def set_text(self, braille_text: str):
        self.set_braille(braille_text)

    def set_braille(self, braille_text: str, char_list: list = None):
        # Clear existing widgets
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        from braille_maps import get_dots
        for i, ch in enumerate(braille_text):
            dot_nums = get_dots(ch)
            dots_bool = [dot in dot_nums for dot in [1, 2, 3, 4, 5, 6]]
            
            # Create a cell container to show letter label under the braille dots
            cell_container = QWidget()
            cell_layout = QVBoxLayout(cell_container)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.setSpacing(6)
            cell_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            cell_widget = BrailleCellWidget(dots_bool)
            cell_widget.setFixedSize(28, 42)
            cell_layout.addWidget(cell_widget)
            
            lbl = QLabel(char_list[i] if char_list and i < len(char_list) else "")
            lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-weight: bold; background: transparent;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell_layout.addWidget(lbl)
            
            self.layout.addWidget(cell_container)

    def paintEvent(self, event):
        # Layout manages child cell rendering now
        pass


class ConverterPage(QWidget):
    """Main Text ↔ Braille converter page with side-by-side column layout."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_mode = "text_to_braille"
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # ── HEADER & OPTIONS ROW ────────────────────────────
        header_layout = QHBoxLayout()
        
        title = QLabel("Converter")
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addSpacing(30)

        # Mode Tab Bar (Pill buttons container)
        tab_container = QFrame()
        tab_container.setStyleSheet(f"""
            QFrame {{
                background-color: #141b25;
                border: 1px solid {BORDER_COL};
                border-radius: 20px;
                padding: 2px;
            }}
        """)
        tab_layout = QHBoxLayout(tab_container)
        tab_layout.setContentsMargins(4, 4, 4, 4)
        tab_layout.setSpacing(4)
        
        self.mode_buttons = {}
        modes = [
            ("text_to_braille", "Text → Braille"),
            ("braille_to_text", "Braille → Text"),
            ("dot_notation", "Dot Notation"),
            ("dot_builder", "Dot Builder"),
            ("paste_braille", "Paste Braille")
        ]
        
        for mode_id, label in modes:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setFixedHeight(30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {TEXT_MUTED};
                    border: none;
                    border-radius: 15px;
                    padding: 0 15px;
                    font-size: 11px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    color: {TEXT_PRIMARY};
                    background: #1c2331;
                }}
                QPushButton:checked {{
                    background: {ACCENT_GREEN};
                    color: #1a1b26;
                }}
            """)
            btn.clicked.connect(lambda checked, m=mode_id: self._switch_mode(m))
            tab_layout.addWidget(btn)
            self.mode_buttons[mode_id] = btn

        header_layout.addWidget(tab_container)
        header_layout.addStretch()

        # Language Selector
        lang_layout = QHBoxLayout()
        lang_lbl = QLabel("Language:")
        lang_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-weight: bold;")
        lang_layout.addWidget(lang_lbl)
        
        self.lang_selector = QComboBox()
        self.lang_selector.addItems(["English", "Hindi", "Marathi", "Tamil", "Telugu", "Kannada", "French", "Spanish"])
        self.lang_selector.setFixedWidth(130)
        self.lang_selector.currentTextChanged.connect(self._on_language_change)
        lang_layout.addWidget(self.lang_selector)
        
        header_layout.addLayout(lang_layout)
        layout.addLayout(header_layout)

        # Set default active button and aliases
        self.mode_buttons["text_to_braille"].setChecked(True)
        self.btn_text_to_braille = self.mode_buttons["text_to_braille"]
        self.btn_braille_to_text = self.mode_buttons["braille_to_text"]
        self.btn_dot_notation = self.mode_buttons["dot_notation"]
        self.btn_dot_builder = self.mode_buttons["dot_builder"]
        self.btn_paste_braille = self.mode_buttons["paste_braille"]

        # ── MAIN STACKED PAGES ──────────────────────────────
        self.stacked_pages = QStackedWidget()
        self.stacked_pages.setStyleSheet("background: transparent; border: none;")
        
        self.stacked_pages.addWidget(self._build_text_to_braille_page())
        self.stacked_pages.addWidget(self._build_braille_to_text_page())
        self.stacked_pages.addWidget(self._build_dot_notation_page())
        self.stacked_pages.addWidget(self._build_dot_builder_page())
        self.stacked_pages.addWidget(self._build_paste_braille_page())
        
        layout.addWidget(self.stacked_pages, 1)

        # Status Footer
        self.status_lbl = QLabel("Ready")
        self.status_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; padding: 2px;")
        layout.addWidget(self.status_lbl)

    def _build_text_to_braille_page(self):
        """Page: Text → Braille conversion with side-by-side layout."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        cols_container = QWidget()
        cols_layout = QHBoxLayout(cols_container)
        cols_layout.setContentsMargins(0, 0, 0, 0)
        cols_layout.setSpacing(20)

        # Left Column: Input
        left_col = QWidget()
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)
        
        in_label = QLabel("TEXT INPUT")
        in_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Type text to convert to Braille...")
        self.input_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: #141b25;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
            }}
            QTextEdit:focus {{
                border-color: {ACCENT_GREEN};
            }}
        """)
        self.input_text.textChanged.connect(self._auto_convert)
        left_layout.addWidget(in_label)
        left_layout.addWidget(self.input_text)
        cols_layout.addWidget(left_col, 1)

        # Right Column: Output
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)
        
        out_label = QLabel("BRAILLE OUTPUT")
        out_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: #141b25;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
            }}
            QTextEdit:focus {{
                border-color: {ACCENT_GREEN};
            }}
        """)
        right_layout.addWidget(out_label)
        right_layout.addWidget(self.output_text)
        cols_layout.addWidget(right_col, 1)

        layout.addWidget(cols_container, 1)

        # Braille visualization
        viz_container = QWidget()
        viz_layout = QVBoxLayout(viz_container)
        viz_layout.setContentsMargins(0, 5, 0, 0)
        viz_layout.setSpacing(6)
        
        viz_label = QLabel("BRAILLE PATTERN")
        viz_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        self.dot_display = BrailleDisplayWidget()
        self.dot_display.setFixedHeight(120)
        viz_layout.addWidget(viz_label)
        viz_layout.addWidget(self.dot_display)
        
        layout.addWidget(viz_container)
        return widget

    def _build_braille_to_text_page(self):
        """Page: Braille → Text conversion with side-by-side layout."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        cols_container = QWidget()
        cols_layout = QHBoxLayout(cols_container)
        cols_layout.setContentsMargins(0, 0, 0, 0)
        cols_layout.setSpacing(20)

        # Left Column: Input
        left_col = QWidget()
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)
        
        in_label = QLabel("BRAILLE INPUT")
        in_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        self.braille_input_main = QTextEdit()
        self.braille_input_main.setPlaceholderText("Paste ⠓⠑⠇⠇⠕ style Braille here...")
        self.braille_input_main.setStyleSheet(f"""
            QTextEdit {{
                background-color: #141b25;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
            }}
            QTextEdit:focus {{
                border-color: {ACCENT_GREEN};
            }}
        """)
        self.braille_input_main.textChanged.connect(self._auto_convert)
        left_layout.addWidget(in_label)
        left_layout.addWidget(self.braille_input_main)
        cols_layout.addWidget(left_col, 1)

        # Right Column: Output
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)
        
        out_label = QLabel("TEXT OUTPUT")
        out_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: #141b25;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
            }}
            QTextEdit:focus {{
                border-color: {ACCENT_GREEN};
            }}
        """)
        right_layout.addWidget(out_label)
        right_layout.addWidget(self.text_output)
        cols_layout.addWidget(right_col, 1)

        layout.addWidget(cols_container, 1)
        return widget

    def _build_dot_notation_page(self):
        """Page: Dot notation input with side-by-side layout."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        cols_container = QWidget()
        cols_layout = QHBoxLayout(cols_container)
        cols_layout.setContentsMargins(0, 0, 0, 0)
        cols_layout.setSpacing(20)

        # Left Column: Input & Button
        left_col = QWidget()
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        in_label = QLabel("DOT NOTATION INPUT")
        in_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        left_layout.addWidget(in_label)

        self.dot_notation_input = QTextEdit()
        self.dot_notation_input.setPlaceholderText("Type dot numbers (e.g., 1 4 or 146)...")
        self.dot_notation_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: #141b25;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
            }}
            QTextEdit:focus {{
                border-color: {ACCENT_GREEN};
            }}
        """)
        left_layout.addWidget(self.dot_notation_input, 1)

        convert_btn = QPushButton("🔄 Convert to Text")
        convert_btn.setMinimumHeight(38)
        convert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        convert_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_GREEN}; color: #1a1b26; border: none; border-radius: 6px; font-weight: bold; font-size: 12px;
            }}
            QPushButton:hover {{ background: #00e896; }}
        """)
        convert_btn.clicked.connect(self._convert_dot_notation)
        left_layout.addWidget(convert_btn)
        
        cols_layout.addWidget(left_col, 1)

        # Right Column: Output
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)
        
        out_label = QLabel("RESULT")
        out_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        right_layout.addWidget(out_label)

        self.dot_notation_output = QTextEdit()
        self.dot_notation_output.setReadOnly(True)
        self.dot_notation_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: #141b25;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
            }}
        """)
        right_layout.addWidget(self.dot_notation_output, 1)
        cols_layout.addWidget(right_col, 1)

        layout.addWidget(cols_container, 1)
        return widget

    def _build_dot_builder_page(self):
        """Page: Interactive dot builder with side-by-side layout."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        cols_container = QWidget()
        cols_layout = QHBoxLayout(cols_container)
        cols_layout.setContentsMargins(0, 0, 0, 0)
        cols_layout.setSpacing(20)

        # Left Column: Builder
        left_col = QWidget()
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        builder_label = QLabel("DOT BUILDER")
        builder_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        left_layout.addWidget(builder_label)

        grid_frame = QFrame()
        grid_frame.setStyleSheet(f"background:#141b25; border-radius:10px; border:1px solid {BORDER_COL}; padding:15px;")
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setSpacing(10)

        self.dot_buttons = {}
        positions = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]

        for dot_num, pos in enumerate(positions, 1):
            btn = QPushButton(str(dot_num))
            btn.setCheckable(True)
            btn.setMinimumSize(50, 50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1e2230;
                    color: {TEXT_PRIMARY};
                    border: 1px solid {BORDER_COL};
                    border-radius: 25px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    border-color: {ACCENT_GREEN};
                }}
                QPushButton:checked {{
                    background-color: {ACCENT_GREEN};
                    color: #1a1b26;
                    border-color: {ACCENT_GREEN};
                }}
            """)
            btn.clicked.connect(lambda checked, d=dot_num: self._toggle_dot(d))
            self.dot_buttons[dot_num] = btn
            grid_layout.addWidget(btn, pos[0], pos[1], Qt.AlignmentFlag.AlignCenter)

        left_layout.addWidget(grid_frame, 1)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        add_btn = QPushButton("➕ Add Character")
        add_btn.setObjectName("primary")
        add_btn.setMinimumHeight(38)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_GREEN}; color: #1a1b26; border: none; border-radius: 6px; font-weight: bold; font-size: 12px;
            }}
            QPushButton:hover {{ background: #00e896; }}
        """)
        add_btn.clicked.connect(self._add_dot_builder_char)
        btn_layout.addWidget(add_btn)

        clear_btn = QPushButton("🔄 Clear")
        clear_btn.setMinimumHeight(38)
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-weight: bold; font-size: 12px;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        clear_btn.clicked.connect(self._clear_dot_builder)
        btn_layout.addWidget(clear_btn)

        left_layout.addLayout(btn_layout)
        cols_layout.addWidget(left_col, 1)

        # Right Column: Output
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)
        
        out_label = QLabel("BRAILLE BUILT")
        out_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        right_layout.addWidget(out_label)

        self.dot_builder_output = QTextEdit()
        self.dot_builder_output.setReadOnly(True)
        self.dot_builder_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: #141b25;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }}
        """)
        right_layout.addWidget(self.dot_builder_output, 1)
        cols_layout.addWidget(right_col, 1)

        layout.addWidget(cols_container, 1)
        return widget

    def _build_paste_braille_page(self):
        """Page: Paste Braille characters with side-by-side layout."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        cols_container = QWidget()
        cols_layout = QHBoxLayout(cols_container)
        cols_layout.setContentsMargins(0, 0, 0, 0)
        cols_layout.setSpacing(20)

        # Left Column: Input
        left_col = QWidget()
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        in_label = QLabel("PASTE BRAILLE")
        in_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        left_layout.addWidget(in_label)

        self.paste_braille_input = QTextEdit()
        self.paste_braille_input.setPlaceholderText("Paste ⠓⠑⠇⠇⠕ here...")
        self.paste_braille_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: #141b25;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
            }}
            QTextEdit:focus {{
                border-color: {ACCENT_GREEN};
            }}
        """)
        left_layout.addWidget(self.paste_braille_input, 1)

        convert_btn = QPushButton("🔄 Convert to Text")
        convert_btn.setMinimumHeight(38)
        convert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        convert_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_GREEN}; color: #1a1b26; border: none; border-radius: 6px; font-weight: bold; font-size: 12px;
            }}
            QPushButton:hover {{ background: #00e896; }}
        """)
        convert_btn.clicked.connect(self._convert_paste_braille)
        left_layout.addWidget(convert_btn)
        
        cols_layout.addWidget(left_col, 1)

        # Right Column: Output
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)
        
        out_label = QLabel("TEXT OUTPUT")
        out_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        right_layout.addWidget(out_label)

        self.paste_braille_output = QTextEdit()
        self.paste_braille_output.setReadOnly(True)
        self.paste_braille_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: #141b25;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
            }}
        """)
        right_layout.addWidget(self.paste_braille_output, 1)
        cols_layout.addWidget(right_col, 1)

        layout.addWidget(cols_container, 1)
        return widget

    def _switch_mode(self, mode):
        """Switch between different conversion modes."""
        self._current_mode = mode
        
        # Update button states
        for m_id, btn in self.mode_buttons.items():
            btn.setChecked(m_id == mode)
        
        page_map = {
            "text_to_braille": 0,
            "braille_to_text": 1,
            "dot_notation": 2,
            "dot_builder": 3,
            "paste_braille": 4,
        }
        self.stacked_pages.setCurrentIndex(page_map[mode])
        self._convert()

    def _on_language_change(self):
        """Handle language selection change."""
        if self._current_mode in ["text_to_braille", "braille_to_text"]:
            self._convert()

    def _convert(self):
        """Perform conversion based on current mode."""
        lang = self.lang_selector.currentText()
        
        if self._current_mode == "text_to_braille":
            src = self.input_text.toPlainText()
            if src.strip():
                result = text_to_braille(src, lang)
                self.output_text.setPlainText(result)
                self.dot_display.set_braille(result, list(src))
                self.status_lbl.setText(f"✓ {len(src)} chars → {len(result)} braille")
        
        elif self._current_mode == "braille_to_text":
            src = self.braille_input_main.toPlainText()
            if src.strip():
                result = braille_to_text(src, lang)
                self.text_output.setPlainText(result)
                self.status_lbl.setText(f"✓ Converted")

    def _auto_convert(self):
        """Auto-convert on text change."""
        if self._current_mode in ["text_to_braille", "braille_to_text"]:
            self._convert()

    def _convert_dot_notation(self):
        """Convert dot notation to text."""
        from braille_input import braille_input_converter
        
        notation = self.dot_notation_input.toPlainText()
        try:
            dots = braille_input_converter.parse_dot_notation(notation)
            char = braille_input_converter.dots_to_unicode(dots)
            text = braille_input_converter.braille_to_text_input(char, self.lang_selector.currentText())
            self.dot_notation_output.setText(f"Braille: {char}\nText: {text}")
        except Exception as e:
            self.dot_notation_output.setText(f"❌ Error: {str(e)}")

    def _toggle_dot(self, dot_num):
        """Toggle a dot in dot builder."""
        from braille_input import braille_input_converter
        
        braille_input_converter.toggle_dot(dot_num)
        
        for d in range(1, 7):
            is_active = d in braille_input_converter.current_pattern
            btn = self.dot_buttons[d]
            btn.setChecked(is_active)
            if is_active:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {ACCENT_GREEN};
                        color: #1a1b26;
                        border: 1px solid {ACCENT_GREEN};
                        border-radius: 25px;
                        font-size: 14px;
                        font-weight: bold;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #1e2230;
                        color: {TEXT_PRIMARY};
                        border: 1px solid {BORDER_COL};
                        border-radius: 25px;
                        font-size: 14px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        border-color: {ACCENT_GREEN};
                    }}
                """)
        
        char = braille_input_converter.get_current_character()
        self.dot_builder_output.setText(f"Pattern: {char}\nDots: {sorted(braille_input_converter.current_pattern)}")

    def _add_dot_builder_char(self):
        """Add character from dot builder."""
        from braille_input import braille_input_converter
        
        braille_input_converter.add_character()
        
        for btn in self.dot_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1e2230;
                    color: {TEXT_PRIMARY};
                    border: 1px solid {BORDER_COL};
                    border-radius: 25px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    border-color: {ACCENT_GREEN};
                }}
            """)
        
        braille_string = braille_input_converter.get_braille_string()
        self.dot_builder_output.setText(braille_string or "No characters added yet")

    def _clear_dot_builder(self):
        """Clear dot builder."""
        from braille_input import braille_input_converter
        
        braille_input_converter.current_pattern.clear()
        braille_input_converter.pattern_history.clear()
        
        for btn in self.dot_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1e2230;
                    color: {TEXT_PRIMARY};
                    border: 1px solid {BORDER_COL};
                    border-radius: 25px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    border-color: {ACCENT_GREEN};
                }}
            """)
        
        self.dot_builder_output.clear()

    def _convert_paste_braille(self):
        """Convert pasted Braille to text."""
        from braille_input import braille_input_converter
        
        braille = self.paste_braille_input.toPlainText()
        try:
            text = braille_input_converter.braille_to_text_input(braille, self.lang_selector.currentText())
            self.paste_braille_output.setText(text)
        except Exception as e:
            self.paste_braille_output.setText(f"❌ Error: {str(e)}")


class OCRPage(QWidget):
    """Image → Braille → Text OCR page with scanner feel."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._image_path = None
        
        # Scan animation timer setup
        self.scan_timer = QTimer(self)
        self.scan_timer.setInterval(16)  # ~60 fps
        self.scan_timer.timeout.connect(self._animate_scan)
        self.scan_y = 0
        self.scan_direction = 1
        
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # ── HEADER ROW ──────────────────────────────────────
        header_layout = QHBoxLayout()
        title = QLabel("OCR Reader")
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Language Selector
        lang_layout = QHBoxLayout()
        lang_lbl = QLabel("Output Language:")
        lang_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-weight: bold;")
        lang_layout.addWidget(lang_lbl)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Hindi", "Marathi"])
        self.lang_combo.setFixedWidth(130)
        lang_layout.addWidget(self.lang_combo)
        header_layout.addLayout(lang_layout)
        
        layout.addLayout(header_layout)

        # ── MAIN COLUMNS CONTAINER ──────────────────────────
        main_cols = QWidget()
        cols_layout = QHBoxLayout(main_cols)
        cols_layout.setContentsMargins(0, 0, 0, 0)
        cols_layout.setSpacing(25)
        layout.addWidget(main_cols, 1)

        # ── LEFT COLUMN: Scan Viewfinder ────────────────────
        left_col = QWidget()
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        # Viewport Frame
        self.image_frame = QFrame()
        self.image_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #0c0f14;
                border: 2px dashed {BORDER_COL};
                border-radius: 12px;
            }}
        """)
        self.image_frame.setFixedHeight(340)
        
        # Layout inside viewport
        img_container_layout = QGridLayout(self.image_frame)
        img_container_layout.setContentsMargins(15, 15, 15, 15)
        
        self.image_lbl = QLabel("Drag & Drop or click below to upload a Braille image")
        self.image_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_lbl.setWordWrap(True)
        self.image_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; font-weight: bold; border: none; background: transparent;")
        img_container_layout.addWidget(self.image_lbl, 0, 0)

        # Scanner animation overlay line
        self.scan_line = QFrame(self.image_frame)
        self.scan_line.setFixedHeight(4)
        self.scan_line.setStyleSheet("background-color: #00e896; border: none; border-radius: 2px;")
        self.scan_line.setVisible(False)
        
        left_layout.addWidget(self.image_frame)

        # Actions Layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        self.upload_btn = QPushButton("📂 Upload Image")
        self.upload_btn.setObjectName("primary")
        self.upload_btn.setMinimumHeight(40)
        self.upload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.upload_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_GREEN}; color: #1a1b26; border: none; border-radius: 6px; font-weight: bold; font-size: 12px;
            }}
            QPushButton:hover {{ background: #00e896; }}
        """)
        self.upload_btn.clicked.connect(self._upload)
        
        self.process_btn = QPushButton("🔍 Process OCR Scan")
        self.process_btn.setMinimumHeight(40)
        self.process_btn.setEnabled(False)
        self.process_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.process_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-weight: bold; font-size: 12px;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
            QPushButton:disabled {{ background: #131620; color: #4e556e; border: 1px solid #1c202d; }}
        """)
        self.process_btn.clicked.connect(self._start_scan_animation)
        
        btn_layout.addWidget(self.upload_btn, 1)
        btn_layout.addWidget(self.process_btn, 1)
        left_layout.addLayout(btn_layout)
        
        cols_layout.addWidget(left_col, 1)

        # ── RIGHT COLUMN: Results & Settings ────────────────
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)

        # Advanced Settings Panel
        settings_panel = QFrame()
        settings_panel.setStyleSheet(f"background: #141b25; border: 1px solid {BORDER_COL}; border-radius: 8px; padding: 12px;")
        sp_layout = QVBoxLayout(settings_panel)
        sp_layout.setSpacing(8)
        sp_layout.setContentsMargins(12, 12, 12, 12)
        
        sp_title = QLabel("⚙️ OCR SCANNER OPTIONS")
        sp_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        sp_layout.addWidget(sp_title)
        
        options_layout = QHBoxLayout()
        self.chk_invert = QCheckBox("Inverted Dots (Light on Dark)")
        self.chk_invert.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 11px;")
        self.chk_invert.setChecked(True)
        options_layout.addWidget(self.chk_invert)
        
        self.chk_enhance = QCheckBox("Enhance Image Contrast")
        self.chk_enhance.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 11px;")
        self.chk_enhance.setChecked(True)
        options_layout.addWidget(self.chk_enhance)
        
        sp_layout.addLayout(options_layout)
        right_layout.addWidget(settings_panel)

        # Detected Braille
        braille_container = QWidget()
        bc_layout = QVBoxLayout(braille_container)
        bc_layout.setContentsMargins(0, 0, 0, 0)
        bc_layout.setSpacing(6)
        
        b_header = QHBoxLayout()
        b_label = QLabel("DETECTED BRAILLE PATTERN")
        b_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        b_header.addWidget(b_label)
        b_header.addStretch()
        
        self.btn_copy_braille = QPushButton("📋 Copy")
        self.btn_copy_braille.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_braille.setStyleSheet("""
            QPushButton { background: transparent; color: #4FB69F; border: none; font-size: 10px; font-weight: bold; }
            QPushButton:hover { color: #00e896; }
        """)
        self.btn_copy_braille.clicked.connect(lambda: self._copy_to_clipboard(self.braille_out.toPlainText()))
        b_header.addWidget(self.btn_copy_braille)
        bc_layout.addLayout(b_header)

        self.braille_out = QTextEdit()
        self.braille_out.setReadOnly(True)
        self.braille_out.setStyleSheet(f"""
            QTextEdit {{
                background-color: #141b25;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
            }}
        """)
        self.braille_out.setPlaceholderText("OCR detected Braille characters will appear here...")
        self.braille_out.setMaximumHeight(65)
        bc_layout.addWidget(self.braille_out)
        right_layout.addWidget(braille_container)

        # Converted Text
        text_container = QWidget()
        tc_layout = QVBoxLayout(text_container)
        tc_layout.setContentsMargins(0, 0, 0, 0)
        tc_layout.setSpacing(6)
        
        t_header = QHBoxLayout()
        t_label = QLabel("TRANSLATED PLAIN TEXT")
        t_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        t_header.addWidget(t_label)
        t_header.addStretch()
        
        self.btn_copy_text = QPushButton("📋 Copy")
        self.btn_copy_text.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_text.setStyleSheet("""
            QPushButton { background: transparent; color: #4FB69F; border: none; font-size: 10px; font-weight: bold; }
            QPushButton:hover { color: #00e896; }
        """)
        self.btn_copy_text.clicked.connect(lambda: self._copy_to_clipboard(self.text_out.toPlainText()))
        t_header.addWidget(self.btn_copy_text)
        tc_layout.addLayout(t_header)

        self.text_out = QTextEdit()
        self.text_out.setReadOnly(True)
        self.text_out.setStyleSheet(f"""
            QTextEdit {{
                background-color: #141b25;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
            }}
        """)
        self.text_out.setPlaceholderText("Translated plain text will appear here...")
        self.text_out.setMaximumHeight(65)
        tc_layout.addWidget(self.text_out)
        right_layout.addWidget(text_container)

        # Braille Cell Visualizer Display
        viz_label = QLabel("BRAILLE CELL DETAILS")
        viz_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        right_layout.addWidget(viz_label)

        self.dot_display = BrailleDisplayWidget()
        self.dot_display.setFixedHeight(80)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.dot_display)
        scroll.setFixedHeight(80)
        scroll.setStyleSheet(f"background:#141b25; border-radius:8px; border:1px solid {BORDER_COL};")
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        right_layout.addWidget(scroll)

        cols_layout.addWidget(right_col, 1)

        # Status Footer
        self.status_lbl = QLabel("Ready — Upload a Braille image to begin scanning")
        self.status_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        layout.addWidget(self.status_lbl)

    def _upload(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Braille Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)"
        )
        if not path:
            return
        self._image_path = path
        pix = QPixmap(path)
        if not pix.isNull():
            w = max(100, self.image_frame.width() - 30)
            h = max(100, self.image_frame.height() - 30)
            scaled_pix = pix.scaled(
                w, h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_lbl.setPixmap(scaled_pix)
        else:
            self.image_lbl.setText(f"Loaded: {path.split('/')[-1]}")
        self.process_btn.setEnabled(True)
        self.status_lbl.setText(f"Image loaded: {path.split('/')[-1]}")

    def _start_scan_animation(self):
        if not self._image_path:
            return
        self.scan_line.setVisible(True)
        self.scan_y = 0
        self.scan_direction = 1
        self.scan_line.setGeometry(2, self.scan_y, self.image_frame.width() - 4, 4)
        
        self.process_btn.setEnabled(False)
        self.upload_btn.setEnabled(False)
        self.status_lbl.setText("🔍 Running OpenCV OCR Dot Analysis...")
        self.scan_timer.start()

    def _animate_scan(self):
        self.scan_y += 8 * self.scan_direction
        max_height = self.image_frame.height()
        
        if self.scan_y >= max_height - 10:
            self.scan_y = max_height - 10
            self.scan_direction = -1
        elif self.scan_y <= 2 and self.scan_direction == -1:
            self.scan_timer.stop()
            self.scan_line.setVisible(False)
            self.process_btn.setEnabled(True)
            self.upload_btn.setEnabled(True)
            self._process()
            return
            
        self.scan_line.setGeometry(2, self.scan_y, self.image_frame.width() - 4, 4)

    def _process(self):
        if not self._image_path:
            return
        braille, msg = detect_braille_from_image(self._image_path)
        lang = self.lang_combo.currentText()

        self.status_lbl.setText(msg)
        if braille:
            self.braille_out.setPlainText(braille)
            text = braille_to_text(braille, lang)
            self.text_out.setPlainText(text)
            self.dot_display.set_braille(braille)
        else:
            self.braille_out.setPlainText("")
            self.text_out.setPlainText("")
            self.dot_display.clear()

    def _copy_to_clipboard(self, text):
        if text:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(text)
            self.status_lbl.setText("✅ Text copied to clipboard!")




# ════════════════════════════════════════════════════════════════════════════════
# NEW PAGES: Home, Help/Support, Logs
# ════════════════════════════════════════════════════════════════════════════════

CHARACTER_DOTS = {
    'A': [True, False, False, False, False, False],
    'B': [True, True, False, False, False, False],
    'C': [True, False, False, True, False, False],
    'D': [True, False, False, True, True, False],
    'E': [True, False, False, False, True, False],
    'F': [True, True, False, True, False, False],
    'G': [True, True, False, True, True, False],
    'H': [True, True, False, False, True, False],
    'I': [False, True, False, True, False, False],
    'J': [False, True, False, True, True, False],
    'K': [True, False, True, False, False, False],
    'L': [True, True, True, False, False, False],
    'M': [True, False, True, True, False, False],
    'N': [True, False, True, True, True, False],
    'O': [True, False, True, False, True, False],
    'P': [True, True, True, True, False, False],
    'Q': [True, True, True, True, True, False],
    'R': [True, True, True, False, True, False],
    'S': [False, True, True, True, False, False],
    'T': [False, True, True, True, True, False],
    'U': [True, False, True, False, False, True],
    'V': [True, True, True, False, False, True],
    'W': [False, True, False, True, True, True],
    'X': [True, False, True, True, False, True],
    'Y': [True, False, True, True, True, True],
    'Z': [True, False, True, False, True, True],
}

class HomePage(QWidget):
    """Home / Dashboard page - Beautiful, Premium and Interactive."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_char = 'A'
        self._setup_ui()
        self.cycle_character()  # Initialize character of the day
        self.activate_auto_refresh()  # Populate greeting, tips, and stats immediately on startup

    def _setup_ui(self):
        # We wrap everything in a scroll area to guarantee it fits and scrolls beautifully
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        scroll.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # ── 1. Top Welcome Banner ────────────────────────
        welcome_card = QWidget()
        welcome_card.setObjectName("welcomeCard")
        welcome_card.setStyleSheet("background: transparent;")
        welcome_layout = QVBoxLayout(welcome_card)
        welcome_layout.setContentsMargins(0, 5, 0, 10)
        welcome_layout.setSpacing(15)

        # Top row: Greeting (Left) and Status/Clock (Right)
        top_row = QWidget()
        top_row_layout = QHBoxLayout(top_row)
        top_row_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left side info
        left_info = QVBoxLayout()
        left_info.setSpacing(4)
        
        self.welcome_label = QLabel("Good Morning!")
        self.welcome_label.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 24px; font-weight: bold; background: transparent;")
        
        sub_welcome = QLabel("LipiSync Workspace — Active and ready for translation.")
        sub_welcome.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; background: transparent;")
        
        left_info.addWidget(self.welcome_label)
        left_info.addWidget(sub_welcome)
        top_row_layout.addLayout(left_info, 1)

        # Right side info: Date/Time + Status Badge
        right_info = QVBoxLayout()
        right_info.setSpacing(4)
        right_info.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.date_label = QLabel()
        self.date_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: bold; background: transparent;")
        
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(6)
        status_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        status_dot = QLabel("●")
        status_dot.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 11px; background: transparent;")
        status_text = QLabel("Workspace Active")
        status_text.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; background: transparent;")
        
        status_layout.addWidget(status_dot)
        status_layout.addWidget(status_text)
        
        right_info.addWidget(self.date_label)
        right_info.addWidget(status_container)
        top_row_layout.addLayout(right_info)
        
        welcome_layout.addWidget(top_row)

        # Bottom row: Quick Actions
        quick_actions_title = QLabel("QUICK WORKSPACE SHORTCUTS")
        quick_actions_title.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px; font-weight: bold; letter-spacing: 0.5px; background: transparent;")
        welcome_layout.addWidget(quick_actions_title)

        shortcuts_widget = QWidget()
        shortcuts_layout = QHBoxLayout(shortcuts_widget)
        shortcuts_layout.setContentsMargins(0, 0, 0, 0)
        shortcuts_layout.setSpacing(10)

        # Helper for shortcut buttons
        def create_shortcut_btn(icon, title, target_page):
            btn = QPushButton(f"{icon}  {title}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: #141b25;
                    color: {TEXT_PRIMARY};
                    border: 1px solid #1c2331;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 11px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: #1c2435;
                    border-color: {ACCENT_GREEN};
                    color: {ACCENT_GREEN};
                }}
                QPushButton:pressed {{
                    background: #0f141d;
                }}
            """)
            btn.clicked.connect(lambda: self.window().navigate_to_page(target_page))
            return btn

        shortcuts_layout.addWidget(create_shortcut_btn("⇄", "Text Translator", "converter"))
        shortcuts_layout.addWidget(create_shortcut_btn("📷", "OCR Reader", "ocr"))
        shortcuts_layout.addWidget(create_shortcut_btn("🔊", "Vocalizer Studio", "vocalizer"))
        shortcuts_layout.addWidget(create_shortcut_btn("✓", "Accessibility Audit", "audit"))
        shortcuts_layout.addStretch()

        welcome_layout.addWidget(shortcuts_widget)

        # Dynamic Tip of the Day
        self.tip_label = QLabel()
        self.tip_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-style: italic; background: transparent;")
        welcome_layout.addWidget(self.tip_label)

        layout.addWidget(welcome_card)

        # ── 2. Metric / Stats Row ────────────────────────
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        self.stat_conversions = self._create_stat_card("Total Conversions", "0", "Updated in real-time")
        self.stat_favorites = self._create_stat_card("Saved Favorites", "0", "Quick bookmarks")
        self.stat_language = self._create_stat_card("Target Language", "English", "Active locale")
        self.stat_progress = self._create_stat_card("Learning Progress", "0%", "Interactive courses")

        stats_layout.addWidget(self.stat_conversions)
        stats_layout.addWidget(self.stat_favorites)
        stats_layout.addWidget(self.stat_language)
        stats_layout.addWidget(self.stat_progress)
        layout.addLayout(stats_layout)

        # ── 3. Middle Split Area (Launchpad & Character of the Day) ──────────────────
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(20)

        # Left Column: Quick Launchpad
        left_col = QVBoxLayout()
        left_col.setSpacing(10)
        
        launchpad_title = QLabel("Quick Launch Tools")
        launchpad_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        left_col.addWidget(launchpad_title)

        launchpad_grid = QGridLayout()
        launchpad_grid.setSpacing(12)

        tools = [
            ("Text Converter", "Translate text to Braille and back", "Converter", "#3b82f6"),
            ("OCR Reader", "Scan images for Braille text", "OCR", "#10b981"),
            ("Voice Translation", "Speak to generate Braille cells", "Speech", "#8b5cf6"),
            ("Vocalizer Studio", "Convert text to audio and speech", "Audio", "#f59e0b"),
            ("Math Notation", "Convert mathematical equations", "Math", "#ec4899"),
            ("Learning Center", "Start interactive exercises", "Learning", "#06b6d4"),
        ]

        for idx, (name, desc, target_page, color_hex) in enumerate(tools):
            btn_card = QFrame()
            btn_card.setObjectName(f"toolCard_{idx}")
            btn_card.setStyleSheet(f"""
                #toolCard_{idx} {{
                    background: {CARD_BG};
                    border: 1px solid {BORDER_COL};
                    border-radius: 8px;
                }}
                #toolCard_{idx}:hover {{
                    border-color: {color_hex};
                    background: #141b25;
                }}
            """)
            btn_card_layout = QVBoxLayout(btn_card)
            btn_card_layout.setContentsMargins(15, 12, 15, 12)
            btn_card_layout.setSpacing(4)

            title_lbl = QLabel(name)
            title_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: bold;")
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
            desc_lbl.setWordWrap(True)

            btn_card_layout.addWidget(title_lbl)
            btn_card_layout.addWidget(desc_lbl)

            # Install event filter to click the card
            btn_card.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_card.mousePressEvent = lambda event, target=target_page: self._go_to_page(target)

            row = idx // 2
            col = idx % 2
            launchpad_grid.addWidget(btn_card, row, col)

        left_col.addLayout(launchpad_grid)
        middle_layout.addLayout(left_col, 6)

        # Right Column: Character of the Day
        right_col = QVBoxLayout()
        right_col.setSpacing(10)

        char_title = QLabel("Character of the Day")
        char_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        right_col.addWidget(char_title)

        char_card = QFrame()
        char_card.setObjectName("charCard")
        char_card.setStyleSheet(f"""
            #charCard {{
                background: {CARD_BG};
                border: 1px solid {BORDER_COL};
                border-radius: 10px;
            }}
        """)
        char_card_layout = QVBoxLayout(char_card)
        char_card_layout.setContentsMargins(20, 20, 20, 20)
        char_card_layout.setSpacing(15)

        self.char_label = QLabel("Letter A")
        self.char_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.char_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: bold;")
        char_card_layout.addWidget(self.char_label)

        # Large Braille Cell
        self.large_cell = BrailleCellWidget()
        self.large_cell.setMinimumSize(100, 150)
        self.large_cell.setMaximumSize(120, 180)
        char_card_layout.addWidget(self.large_cell, 0, Qt.AlignmentFlag.AlignCenter)

        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        self.btn_speak_char = QPushButton("Listen")
        self.btn_speak_char.setMinimumHeight(35)
        self.btn_speak_char.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-size: 12px;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        self.btn_speak_char.clicked.connect(self.speak_character)
        controls_layout.addWidget(self.btn_speak_char)

        self.btn_next_char = QPushButton("Next")
        self.btn_next_char.setMinimumHeight(35)
        self.btn_next_char.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_GREEN}; color: #1a1b26; border: none; border-radius: 6px; font-size: 12px; font-weight: bold;
            }}
            QPushButton:hover {{ background: #00e896; }}
        """)
        self.btn_next_char.clicked.connect(self.cycle_character)
        controls_layout.addWidget(self.btn_next_char)

        char_card_layout.addLayout(controls_layout)
        right_col.addWidget(char_card)
        middle_layout.addLayout(right_col, 4)

        layout.addLayout(middle_layout)

        # ── 4. Recent Conversions Section ──────────────────
        recent_title = QLabel("Recent Translations")
        recent_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        layout.addWidget(recent_title)

        from PyQt6.QtWidgets import QHeaderView
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(4)
        self.recent_table.setHorizontalHeaderLabels(["Timestamp", "Type", "Input text", "Output Braille"])
        
        # Hide vertical row numbers header and disable table grid lines
        self.recent_table.verticalHeader().setVisible(False)
        self.recent_table.setShowGrid(False)
        self.recent_table.verticalHeader().setDefaultSectionSize(38)
        
        # Configure horizontal header alignment and equal column resize modes
        header = self.recent_table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.recent_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.recent_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.recent_table.setStyleSheet(f"""
            QTableWidget {{
                background: {CARD_BG};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                color: {TEXT_PRIMARY};
                gridline-color: transparent;
            }}
            QTableWidget::item {{
                padding: 6px 10px;
                border-bottom: 1px solid {BORDER_COL};
            }}
            QHeaderView::section {{
                background-color: #111822;
                color: {ACCENT_GREEN};
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
                border: none;
                border-bottom: 1px solid {BORDER_COL};
                padding: 8px 10px;
            }}
        """)
        self.recent_table.setMinimumHeight(140)
        self.recent_table.setMaximumHeight(180)
        layout.addWidget(self.recent_table)

        self.no_recent_lbl = QLabel("No translations performed yet. Start converting to view history!")
        self.no_recent_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_recent_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; padding: 20px;")
        layout.addWidget(self.no_recent_lbl)

        # Set main layout for self
        main_vbox = QVBoxLayout(self)
        main_vbox.setContentsMargins(0, 0, 0, 0)
        main_vbox.addWidget(scroll)

    def _create_stat_card(self, title_text, value_text, subtitle_text):
        card = QFrame()
        card.setObjectName("statCard")
        card.setStyleSheet(f"""
            #statCard {{
                background: {CARD_BG};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(4)

        t_lbl = QLabel(title_text)
        t_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-weight: bold;")
        card_layout.addWidget(t_lbl)

        v_lbl = QLabel(value_text)
        v_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 20px; font-weight: bold;")
        card_layout.addWidget(v_lbl)

        s_lbl = QLabel(subtitle_text)
        s_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px;")
        card_layout.addWidget(s_lbl)

        # Save references for updating values
        card.title_label = t_lbl
        card.value_label = v_lbl
        card.subtitle_label = s_lbl

        return card

    def _go_to_page(self, page_name):
        main_win = self.window()
        if main_win and hasattr(main_win, 'page_names'):
            try:
                idx = main_win.page_names.index(page_name)
                main_win.nav.setCurrentRow(idx)
            except ValueError:
                pass

    def cycle_character(self):
        import random
        # Character of the day letters and their 6-dot configurations
        chars = list(CHARACTER_DOTS.keys())
        self.current_char = random.choice(chars)
        dots = CHARACTER_DOTS[self.current_char]
        self.large_cell.set_dots(dots)
        self.char_label.setText(f"English Character: {self.current_char}")

    def speak_character(self):
        try:
            char_desc = f"Letter {self.current_char}"
            # Standard audio output using audio_engine
            audio_engine.speak(char_desc)
        except Exception:
            pass

    def activate_auto_refresh(self):
        # Time-based greeting without username
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good Morning"
        elif hour < 18:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"
        self.welcome_label.setText(f"{greeting}!")

        # Dynamic Date Display
        try:
            self.date_label.setText(datetime.now().strftime("%A, %d %B"))
        except Exception:
            self.date_label.setText("")

        # Dynamic Tip of the Day
        import random
        tips = [
            "Tip: Use Alt+1 to Alt+9 to navigate between app pages instantly.",
            "Tip: Toggle 'Real-time View' to see visual Braille cells as you type.",
            "Tip: You can save any text translation to an MP3 file on the Audio page.",
            "Tip: Drag and drop or browse images containing Braille to read them instantly.",
            "Tip: Translate complex algebraic expressions into Nemeth Braille code."
        ]
        self.tip_label.setText(random.choice(tips))

        # Refresh stats
        try:
            total_conv = len(history_manager.history)
            self.stat_conversions.value_label.setText(str(total_conv))
        except Exception:
            pass

        try:
            total_favs = len(favorites_manager.favorites)
            self.stat_favorites.value_label.setText(str(total_favs))
        except Exception:
            pass

        try:
            cur_lang = settings_manager.get_setting("braille_language", "English")
            self.stat_language.value_label.setText(cur_lang)
        except Exception:
            pass

        try:
            progress = learning_tracker.get_progress()
            self.stat_progress.value_label.setText(f"{progress['completion_percent']:.0f}%")
        except Exception:
            pass

        # Refresh recent conversions table
        try:
            recent = history_manager.get_history(3)
            if recent:
                self.recent_table.setVisible(True)
                self.no_recent_lbl.setVisible(False)
                self.recent_table.setRowCount(len(recent))
                for idx, record in enumerate(recent):
                    # Format timestamp cleanly
                    ts_str = record.timestamp
                    if "T" in ts_str:
                        ts_str = ts_str.split("T")[1][:5] # Show HH:MM
                    
                    type_str = "Text → Braille" if record.conversion_type == 'text_to_braille' else "Braille → Text"
                    
                    self.recent_table.setItem(idx, 0, QTableWidgetItem(ts_str))
                    self.recent_table.setItem(idx, 1, QTableWidgetItem(type_str))
                    self.recent_table.setItem(idx, 2, QTableWidgetItem(record.input_text))
                    self.recent_table.setItem(idx, 3, QTableWidgetItem(record.output_text))
            else:
                self.recent_table.setVisible(False)
                self.no_recent_lbl.setVisible(True)
        except Exception:
            self.recent_table.setVisible(False)
            self.no_recent_lbl.setVisible(True)

    def deactivate_auto_refresh(self):
        pass


class LogsPage(QWidget):
    """Activity Logs page."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(12)

        title = QLabel("Activity Logs")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Monitor recent app events, filter entries, and keep an eye on system activity.")
        subtitle.setObjectName("muted")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Quick filter row
        filter_row = QHBoxLayout()
        filter_label = QLabel("Filter:")
        filter_label.setMinimumWidth(55)
        filter_row.addWidget(filter_label)
        self.logs_filter = QLineEdit()
        self.logs_filter.setPlaceholderText("Search timestamp, action, details, or status...")
        self.logs_filter.textChanged.connect(self._filter_logs)
        filter_row.addWidget(self.logs_filter)
        layout.addLayout(filter_row)

        self.logs_summary = QLabel("8 sample log entries loaded")
        self.logs_summary.setObjectName("muted")
        layout.addWidget(self.logs_summary)

        self._sample_logs = [
            ("2026-05-27 14:35:22", "Text Conversion", "English → Braille (hello)", "Success"),
            ("2026-05-27 14:33:45", "Audio Export", "WAV file created", "Success"),
            ("2026-05-27 14:30:18", "Settings Changed", "Speed: 150 → 180 wpm", "Success"),
            ("2026-05-27 14:28:12", "PDF Upload", "document.pdf (5 pages)", "Success"),
            ("2026-05-27 14:25:33", "Statistics Logged", "Conversion tracked", "Success"),
            ("2026-05-27 14:22:10", "Language Switch", "English → Hindi", "Success"),
            ("2026-05-27 14:18:55", "OCR Processing", "Image analyzed", "Success"),
            ("2026-05-27 14:15:30", "History Cleared", "100 old entries removed", "Success"),
        ]

        # Create table for logs
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(4)
        self.logs_table.setHorizontalHeaderLabels(["Timestamp", "Action", "Details", "Status"])
        self.logs_table.setAlternatingRowColors(True)
        self.logs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.logs_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.logs_table.verticalHeader().setVisible(False)
        self.logs_table.setWordWrap(False)
        self.logs_table.setStyleSheet(f"""
            QTableWidget {{ background-color: {CARD_BG}; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 8px; }}
            QHeaderView::section {{ background-color: {BORDER_COL}; color: {TEXT_PRIMARY}; padding: 5px; border: none; }}
            QTableWidget::item {{ padding: 8px; }}
        """)
        layout.addWidget(self.logs_table)

        self.logs_empty = QLabel("No log entries match the current filter.")
        self.logs_empty.setObjectName("muted")
        self.logs_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logs_empty.setVisible(False)
        layout.addWidget(self.logs_empty)

        self._populate_logs(self._sample_logs)

        # Control buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        refresh_btn = QPushButton("Refresh Logs")
        refresh_btn.setObjectName("primary")
        refresh_btn.clicked.connect(self._refresh_logs)
        btn_layout.addWidget(refresh_btn)

        clear_btn = QPushButton("Clear Old Logs")
        clear_btn.setObjectName("danger")
        clear_btn.clicked.connect(self._clear_logs)
        btn_layout.addWidget(clear_btn)

        export_btn = QPushButton("Export Logs")
        export_btn.setObjectName("primary")
        btn_layout.addWidget(export_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _filter_logs(self, text: str):
        query = text.strip().lower()
        visible_count = 0

        for row in range(self.logs_table.rowCount()):
            visible = True
            if query:
                cells = []
                for col in range(self.logs_table.columnCount()):
                    item = self.logs_table.item(row, col)
                    cells.append(item.text().lower() if item else "")
                visible = any(query in cell for cell in cells)

            self.logs_table.setRowHidden(row, not visible)
            if visible:
                visible_count += 1

        self.logs_empty.setVisible(visible_count == 0)
        self.logs_summary.setText(f"{visible_count} / {self.logs_table.rowCount()} entries visible")

    def _populate_logs(self, logs):
        self.logs_table.setRowCount(0)
        for timestamp, action, details, status in logs:
            row = self.logs_table.rowCount()
            self.logs_table.insertRow(row)
            self.logs_table.setItem(row, 0, QTableWidgetItem(timestamp))
            self.logs_table.setItem(row, 1, QTableWidgetItem(action))
            self.logs_table.setItem(row, 2, QTableWidgetItem(details))

            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor(ACCENT_GREEN))
            self.logs_table.setItem(row, 3, status_item)

        self.logs_table.resizeColumnsToContents()
        self.logs_table.horizontalHeader().setStretchLastSection(True)
        self.logs_summary.setText(f"{self.logs_table.rowCount()} sample log entries loaded")
        self.logs_empty.setVisible(self.logs_table.rowCount() == 0)

    def _refresh_logs(self):
        self.logs_filter.clear()
        self._populate_logs(self._sample_logs)
        QMessageBox.information(self, "Logs", "Logs refreshed successfully!")

    def _clear_logs(self):
        reply = QMessageBox.question(self, "Clear Logs", "Clear all old logs? This cannot be undone.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.logs_filter.clear()
            self.logs_summary.setText("0 / 0 entries visible")
            self.logs_empty.setVisible(True)
            self.logs_table.setRowCount(0)
            QMessageBox.information(self, "Success", "Old logs cleared!")
class AboutPage(QWidget):
    """About / reference page."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # Header Title
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(15)

        title_lay = QVBoxLayout()
        title_lay.setSpacing(5)
        title = QLabel("LipiSync Workspace")
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        
        subtitle = QLabel("Empowering accessibility through real-time Braille translation & educational tools.")
        subtitle.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 12px; font-weight: bold;")
        
        title_lay.addWidget(title)
        title_lay.addWidget(subtitle)
        header_layout.addLayout(title_lay)
        header_layout.addStretch()
        layout.addWidget(header_widget)

        # Splitter for Left (Theory & Facts) and Right (Usefulness & Anatomy)
        main_split = QSplitter(Qt.Orientation.Horizontal)
        main_split.setStyleSheet("QSplitter::handle { background: transparent; }")
        
        # Left Panel (Open layout, no QFrames)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 15, 0)
        left_layout.setSpacing(20)

        # 1. Project Theory
        theory_lbl = QLabel("WHAT IS LIPISYNC?")
        theory_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 10px; font-weight: bold; letter-spacing: 0.8px; background: transparent;")
        left_layout.addWidget(theory_lbl)

        theory_details = QLabel(
            "LipiSync is an open accessibility hub designed to bridge the communication gap between sighted "
            "and visually impaired individuals. By integrating multi-grade Braille translation, document scanning, "
            "speech engines, and real-time screen reader feedback, it provides a comprehensive workspace "
            "for daily learning, conversion, and collaboration."
        )
        theory_details.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; background: transparent; line-height: 1.5;")
        theory_details.setWordWrap(True)
        left_layout.addWidget(theory_details)

        left_layout.addSpacing(10)

        # 2. Facts
        facts_lbl = QLabel("TACTILE WRITING & BRAILLE FACTS")
        facts_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 10px; font-weight: bold; letter-spacing: 0.8px; background: transparent;")
        left_layout.addWidget(facts_lbl)

        facts_details = QLabel(
            "• <b>Tactile Representation:</b> Braille is a code, not a language. It represents alphabets, numbers, and symbols tactilely across UEB and Bharati Braille conventions.<br><br>"
            "• <b>6-Dot Matrix:</b> The traditional cell contains 6 dots arranged in a 2x3 matrix, allowing exactly 64 binary combinations for characters.<br><br>"
            "• <b>Contractions:</b> Higher Braille grades introduce abbreviations to optimize physical page space, significantly increasing reading speed."
        )
        facts_details.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; background: transparent; line-height: 1.5;")
        facts_details.setTextFormat(Qt.TextFormat.RichText)
        facts_details.setWordWrap(True)
        left_layout.addWidget(facts_details)

        left_layout.addStretch()
        main_split.addWidget(left_widget)

        # Right Panel (Open layout, no QFrames)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(15, 0, 0, 0)
        right_layout.setSpacing(20)

        # 1. User Impact
        impact_lbl = QLabel("HOW LIPISYNC HELPS USERS")
        impact_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 10px; font-weight: bold; letter-spacing: 0.8px; background: transparent;")
        right_layout.addWidget(impact_lbl)

        impact_details = QLabel(
            "• <b>Visually Impaired Users:</b> Access instant voice feedback, full keyboard accessibility shortcuts, and quick conversion utilities.<br><br>"
            "• <b>Students & Teachers:</b> Reference interactive curriculums, standard quiz modules, and math notation conversions for school and college coursework.<br><br>"
            "• <b>Content Creators:</b> Digitize physical documents via OCR and export Braille output as high-fidelity audio files."
        )
        impact_details.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; background: transparent; line-height: 1.5;")
        impact_details.setTextFormat(Qt.TextFormat.RichText)
        impact_details.setWordWrap(True)
        right_layout.addWidget(impact_details)

        right_layout.addSpacing(10)

        # 2. Anatomy
        anatomy_lbl = QLabel("THE 6-DOT ANATOMY CELL")
        anatomy_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 10px; font-weight: bold; letter-spacing: 0.8px; background: transparent;")
        right_layout.addWidget(anatomy_lbl)

        illustration_container = QWidget()
        illustration_layout = QHBoxLayout(illustration_container)
        illustration_layout.setContentsMargins(0, 0, 0, 0)
        illustration_layout.setSpacing(20)
        
        anatomy_cell = QFrame()
        anatomy_cell.setFixedSize(84, 120)
        anatomy_cell.setStyleSheet(f"background: #101520; border: 1px solid {BORDER_COL}; border-radius: 8px;")
        cell_grid = QGridLayout(anatomy_cell)
        cell_grid.setContentsMargins(14, 14, 14, 14)
        cell_grid.setSpacing(8)
        
        dot_labels = ["1", "2", "3", "4", "5", "6"]
        positions = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)]
        for dot_num, (r, c) in zip(dot_labels, positions):
            dot_w = QFrame()
            dot_w.setFixedSize(18, 18)
            dot_w.setStyleSheet(f"background: #182823; border-radius: 9px; border: 1.5px solid {ACCENT_GREEN};")
            d_lay = QHBoxLayout(dot_w)
            d_lay.setContentsMargins(0, 0, 0, 0)
            lbl = QLabel(dot_num)
            lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 9px; font-weight: bold; background: transparent;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            d_lay.addWidget(lbl)
            cell_grid.addWidget(dot_w, r, c)
            
        illustration_layout.addWidget(anatomy_cell)
        
        desc_lbl = QLabel(
            "Dots are numbered top-to-bottom in two vertical columns:<br><br>"
            "• <b>Left Column:</b> Dots 1, 2, and 3<br><br>"
            "• <b>Right Column:</b> Dots 4, 5, and 6"
        )
        desc_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; background: transparent; line-height: 1.4;")
        desc_lbl.setTextFormat(Qt.TextFormat.RichText)
        desc_lbl.setWordWrap(True)
        illustration_layout.addWidget(desc_lbl)
        
        right_layout.addWidget(illustration_container)
        right_layout.addStretch()
        main_split.addWidget(right_widget)
        
        main_split.setStretchFactor(0, 1)
        main_split.setStretchFactor(1, 1)
        layout.addWidget(main_split, 1)

        # Bottom Panel (Interactive live-rendered example)
        bottom_widget = QWidget()
        bottom_lay = QVBoxLayout(bottom_widget)
        bottom_lay.setContentsMargins(0, 10, 0, 0)
        bottom_lay.setSpacing(10)
        
        dot_demo_lbl = QLabel("SAMPLE TRANSLATED OUTPUT — 'hello'")
        dot_demo_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 10px; font-weight: bold; letter-spacing: 0.8px; background: transparent;")
        bottom_lay.addWidget(dot_demo_lbl)

        from braille_engine import text_to_braille
        hello_braille = text_to_braille("hello", "English")
        
        self.demo_display = BrailleDisplayWidget()
        self.demo_display.set_braille(hello_braille, list("hello"))
        
        demo_scroll = QScrollArea()
        demo_scroll.setWidgetResizable(True)
        demo_scroll.setFixedHeight(120)
        demo_scroll.setWidget(self.demo_display)
        demo_scroll.setStyleSheet("background: #07090e; border-radius: 6px; border: 1px solid #141b22;")
        bottom_lay.addWidget(demo_scroll)
        
        layout.addWidget(bottom_widget)


class BlindUserGuidePage(QWidget):
    """Comprehensive guide for blind users."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(14)

        title = QLabel("♿ Guide for Blind & Visually Impaired Users")
        title.setObjectName("title")
        layout.addWidget(title)

        # Create scrollable text area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        guide_widget = QWidget()
        guide_layout = QVBoxLayout(guide_widget)

        guide_text = """
        ═══════════════════════════════════════════════════════════════════════════
        LIPISYNC v2.0 — THE INTELLIGENT BRAILLE WORKSPACE
        ═══════════════════════════════════════════════════════════════════════════
        
        ⭐ PRIMARY PURPOSE:
        This tool converts TEXT to BRAILLE for printing on embossers.
        The braille you can READ with your fingers (tactile), not your eyes.
        
        
        ═══════════════════════════════════════════════════════════════════════════
        HOW TO USE (Quick Start):
        ═══════════════════════════════════════════════════════════════════════════
        
        1️⃣  CONVERT TEXT TO BRAILLE:
            • Press Alt+1 to go to Converter page
            • Type or paste your text
            • Press Ctrl+Shift+S to hear the braille spoken
            • Press Ctrl+3 to copy the braille
        
        2️⃣  PRINT PHYSICAL BRAILLE:
            • Copy the braille (Ctrl+3)
            • Open your Braille embosser software
            • Paste the braille
            • Print it
            • → Creates tactile braille you can feel and read with your fingers!
        
        3️⃣  HEAR EVERYTHING SPOKEN:
            • Press Ctrl+Shift+S anytime to hear the output
            • Go to Audio page (Alt+3) for full text-to-speech
            • Adjust speed and volume
        
        
        ═══════════════════════════════════════════════════════════════════════════
        KEYBOARD SHORTCUTS (Essential for blind users):
        ═══════════════════════════════════════════════════════════════════════════
        
        PAGE NAVIGATION:
        Alt+1 ......... Converter (main tool)
        Alt+2 ......... OCR (image to braille)
        Alt+3 ......... Audio (text-to-speech)
        Alt+4 ......... Grades (learn contractions)
        Alt+5 ......... Math (equations & symbols)
        Alt+6 ......... Documents (PDF conversion)
        Alt+7 ......... Live Preview (real-time view)
        Alt+8 ......... Learning (interactive course)
        Alt+9 ......... History (your past conversions)
        Alt+0 ......... Audit (check accessibility)
        
        COMMON ACTIONS:
        Ctrl+Shift+S .. Speak current output
        Ctrl+3 ........ Copy output to clipboard
        Ctrl+Shift+H .. Go to History page
        Ctrl+Shift+F .. Add to Favorites
        F1 ........... Show this help
        
        NAVIGATION:
        Tab .......... Move to next control
        Shift+Tab .... Move to previous control
        Enter ........ Activate button
        Arrow Keys ... Adjust sliders
        
        
        ═══════════════════════════════════════════════════════════════════════════
        DETAILED WORKFLOW FOR EMBOSSING:
        ═══════════════════════════════════════════════════════════════════════════
        
        STEP 1: Type or paste your text
        ────────────────────────────────
        • Go to Converter (Alt+1)
        • Choose language: English, Hindi, or Marathi
        • Type your text or paste from clipboard
        • The conversion happens automatically
        
        STEP 2: Hear what you're converting
        ───────────────────────────────────
        • Press Ctrl+Shift+S to hear it spoken
        • This helps you verify the conversion is correct
        
        STEP 3: Copy to clipboard
        ─────────────────────────
        • Press Ctrl+3
        • The braille is now copied to your clipboard
        
        STEP 4: Send to embosser
        ─────────────────────────
        • Open your embosser software (e.g., JAWS Braille Embosser)
        • Paste the braille (Ctrl+V)
        • Set paper size and margins
        • Press Print/Emboss
        
        STEP 5: Touch & read the braille!
        ──────────────────────────────────
        • Your embosser prints physical, tactile braille
        • You can now feel and read it with your fingers
        • That's the whole purpose! 🎉
        
        
        ═══════════════════════════════════════════════════════════════════════════
        LEARNING BRAILLE:
        ═══════════════════════════════════════════════════════════════════════════
        
        Press Alt+8 to go to Learning page for:
        • Interactive Braille lessons
        • Flashcard practice
        • Quiz mode to test yourself
        • Progress tracking
        
        Start with Grade 1 (basic) and progress to Grade 2 (contractions).
        
        
        ═══════════════════════════════════════════════════════════════════════════
        AUDIO PAGE (All text spoken aloud):
        ═══════════════════════════════════════════════════════════════════════════
        
        Press Alt+3 to:
        • Type any text
        • Press Play to hear it spoken
        • Adjust speech speed (slow/fast)
        • Adjust volume (quiet/loud)
        • Supports English, Hindi, Marathi
        
        
        ═══════════════════════════════════════════════════════════════════════════
        ADVANCED BRAILLE GRADES:
        ═══════════════════════════════════════════════════════════════════════════
        
        Press Alt+4 for Grades page:
        
        GRADE 1: Full character mapping
        • Every letter = unique braille symbol
        • Slower to read, but easy to learn
        • Good for beginners
        
        GRADE 2: Contractions (recommended!)
        • Short words like "and" → 1 braille symbol
        • 3-4 times faster to read
        • Standard braille for books
        • Example: "and the cat" → fewer symbols
        
        GRADE 3: Maximum abbreviations
        • Experimental
        • For advanced readers only
        
        
        ═══════════════════════════════════════════════════════════════════════════
        HISTORY & FAVORITES:
        ═══════════════════════════════════════════════════════════════════════════
        
        Press Alt+9 for History page:
        • All your conversions are auto-saved
        • Search past conversions
        • Save favorites (Ctrl+Shift+F)
        • Never lose a conversion again!
        
        
        ═══════════════════════════════════════════════════════════════════════════
        ACCESSIBILITY FEATURES:
        ═══════════════════════════════════════════════════════════════════════════
        
        This app is fully keyboard accessible:
        • All functions work without mouse
        • Tab through all controls
        • Arrow keys adjust values
        • Screen reader compatible
        • Works with JAWS, NVDA, Narrator, etc.
        
        
        ═══════════════════════════════════════════════════════════════════════════
        TROUBLESHOOTING:
        ═══════════════════════════════════════════════════════════════════════════
        
        Q: I can't hear anything
        A: Go to Audio page (Alt+3) and click Play button
        
        Q: My embosser isn't printing
        A: Make sure you copied the braille (Ctrl+3) and pasted in embosser software
        
        Q: How do I know the conversion is correct?
        A: Press Ctrl+Shift+S to hear it spoken, or go to Audit page (Alt+0)
        
        Q: Can I use this offline?
        A: YES! This works completely offline. No internet needed.
        
        Q: What languages are supported?
        A: English, Hindi, and Marathi
        
        
        ═══════════════════════════════════════════════════════════════════════════
        TIPS FOR BEST EXPERIENCE:
        ═══════════════════════════════════════════════════════════════════════════
        
        ✓ Memorize Alt+1 to Alt+0 for quick page switching
        ✓ Always use Ctrl+Shift+S to verify conversions
        ✓ Use Grade 2 for actual reading (contractions)
        ✓ Learn from Lessons (Alt+8) to understand Braille better
        ✓ Check History (Alt+9) for past work
        ✓ Use Audit (Alt+0) to find conversion issues
        
        
        ═══════════════════════════════════════════════════════════════════════════
        CONTACT & SUPPORT:
        ═══════════════════════════════════════════════════════════════════════════
        
        This is an open-source educational project.
        GitHub: [Project repository]
        
        Made with accessibility in mind for blind & visually impaired users. ♿
        
        ═══════════════════════════════════════════════════════════════════════════
        """

        guide_label = QLabel(guide_text)
        guide_label.setTextFormat(Qt.TextFormat.PlainText)
        guide_label.setWordWrap(True)
        guide_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-family: 'Courier New', monospace;
                font-size: 12px;
                line-height: 1.4;
                background: transparent;
            }}
        """)
        guide_layout.addWidget(guide_label)
        guide_layout.addStretch()

        scroll.setWidget(guide_widget)
        layout.addWidget(scroll)

        # Print button
        print_btn = QPushButton("🖨️  Print This Guide")
        print_btn.setObjectName("primary")
        print_btn.clicked.connect(self._print_guide)
        layout.addWidget(print_btn)

    def _print_guide(self):
        guide_text = BlindUserHelper.get_quick_start_guide()
        QMessageBox.information(self, "Guide for Blind Users", guide_text)
        announce("Blind user guide opened")


class AudioPage(QWidget):
    """Audio Feedback & Text-to-Speech page with modern split console."""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        try:
            from audio_export import audio_exporter
            self.audio_exporter = audio_exporter
            self.export_available = True
        except ImportError:
            self.audio_exporter = None
            self.export_available = False
            
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # ── TITLE ────────────────────────────────────────────
        title = QLabel("Vocalizer Studio")
        title.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:20px; font-weight:bold;")
        layout.addWidget(title)

        # ── MAIN COLUMNS CONTAINER ──────────────────────────
        main_cols = QWidget()
        cols_layout = QHBoxLayout(main_cols)
        cols_layout.setContentsMargins(0, 0, 0, 0)
        cols_layout.setSpacing(25)
        layout.addWidget(main_cols, 1)

        # ── LEFT COLUMN: Text Editor ────────────────────────
        left_col = QWidget()
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        inp_label = QLabel("TEXT INPUT")
        inp_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        left_layout.addWidget(inp_label)
        
        self.audio_input = QTextEdit()
        self.audio_input.setPlaceholderText("Enter text here to play aloud or export as an audio file...")
        self.audio_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: #0c0f14;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 15px;
                font-size: 13px;
            }}
            QTextEdit:focus {{
                border: 1px solid {ACCENT_GREEN};
            }}
        """)
        left_layout.addWidget(self.audio_input, 1)
        
        # Link both so existing code references work correctly
        self.export_input = self.audio_input
        cols_layout.addWidget(left_col, 1)

        # ── RIGHT COLUMN: Controls Panel ────────────────────
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        ctrl_label = QLabel("AUDIO CONTROLS")
        ctrl_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        right_layout.addWidget(ctrl_label)

        # Mode Pill Buttons Switcher
        pills_widget = QWidget()
        pills_layout = QHBoxLayout(pills_widget)
        pills_layout.setContentsMargins(0, 0, 0, 0)
        pills_layout.setSpacing(8)
        
        self.btn_play_mode = QPushButton("Play Live")
        self.btn_play_mode.setCheckable(True)
        self.btn_play_mode.setChecked(True)
        self.btn_play_mode.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_play_mode.setStyleSheet(self._get_pill_style(True))
        
        self.btn_export_mode = QPushButton("Export File")
        self.btn_export_mode.setCheckable(True)
        self.btn_export_mode.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export_mode.setStyleSheet(self._get_pill_style(False))
        
        self.btn_play_mode.clicked.connect(lambda: self._set_mode(0))
        self.btn_export_mode.clicked.connect(lambda: self._set_mode(1))
        
        pills_layout.addWidget(self.btn_play_mode)
        pills_layout.addWidget(self.btn_export_mode)
        pills_layout.addStretch()
        right_layout.addWidget(pills_widget)

        # Control Panel Stack
        self.mode_stack = QStackedWidget()
        self.mode_stack.setStyleSheet("background: transparent;")

        # ── Mode 1: Play Live Controls ──
        play_ctrl = QWidget()
        play_lay = QVBoxLayout(play_ctrl)
        play_lay.setContentsMargins(0, 0, 0, 0)
        play_lay.setSpacing(15)
        
        play_panel = QFrame()
        play_panel.setStyleSheet(f"background: #141b25; border: 1px solid {BORDER_COL}; border-radius: 8px; padding: 15px;")
        pp_lay = QVBoxLayout(play_panel)
        pp_lay.setSpacing(12)
        
        # Language
        lang_row = QHBoxLayout()
        lang_lbl = QLabel("Language:")
        lang_row.addWidget(lang_lbl)
        self.audio_lang = QComboBox()
        self.audio_lang.addItems(["English", "Hindi", "Marathi", "Tamil", "Telugu", "Kannada", "French", "Spanish"])
        lang_row.addWidget(self.audio_lang)
        pp_lay.addLayout(lang_row)
        
        # Speed
        speed_row = QVBoxLayout()
        speed_header = QHBoxLayout()
        speed_header.addWidget(QLabel("Playback Speed:"))
        self.speed_label = QLabel("150 wpm")
        self.speed_label.setStyleSheet(f"color: {ACCENT_GREEN}; font-weight: bold;")
        speed_header.addWidget(self.speed_label)
        speed_row.addLayout(speed_header)
        
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 300)
        self.speed_slider.setValue(150)
        self.speed_slider.valueChanged.connect(self._update_speed_label)
        speed_row.addWidget(self.speed_slider)
        pp_lay.addLayout(speed_row)
        
        # Volume
        vol_row = QVBoxLayout()
        vol_header = QHBoxLayout()
        vol_header.addWidget(QLabel("Volume Level:"))
        self.vol_label = QLabel("90%")
        self.vol_label.setStyleSheet(f"color: {ACCENT_GREEN}; font-weight: bold;")
        vol_header.addWidget(self.vol_label)
        vol_row.addLayout(vol_header)
        
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(90)
        self.vol_slider.valueChanged.connect(self._update_vol_label)
        vol_row.addWidget(self.vol_slider)
        pp_lay.addLayout(vol_row)
        
        play_lay.addWidget(play_panel)
        
        # Play/Stop Action buttons
        play_btn_lay = QHBoxLayout()
        play_btn_lay.setSpacing(12)
        
        self.play_btn = QPushButton("▶️ Play Audio")
        self.play_btn.setMinimumHeight(42)
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_GREEN}; color: #1a1b26; border: none; border-radius: 6px; font-weight: bold; font-size: 12px;
            }}
            QPushButton:hover {{ background: #00e896; }}
        """)
        self.play_btn.clicked.connect(self._play_audio)
        
        self.stop_btn = QPushButton("⏹️ Stop Audio")
        self.stop_btn.setMinimumHeight(42)
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-weight: bold; font-size: 12px;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        self.stop_btn.clicked.connect(self._stop_audio)
        
        play_btn_lay.addWidget(self.play_btn, 1)
        play_btn_lay.addWidget(self.stop_btn, 1)
        play_lay.addLayout(play_btn_lay)
        play_lay.addStretch()
        
        self.mode_stack.addWidget(play_ctrl)

        # ── Mode 2: Export Controls ──
        export_ctrl = QWidget()
        exp_lay = QVBoxLayout(export_ctrl)
        exp_lay.setContentsMargins(0, 0, 0, 0)
        exp_lay.setSpacing(15)
        
        if not self.export_available:
            status_msg = QLabel("❌ Export features are not available.\nInstall pyttsx3 to enable file generation.")
            status_msg.setStyleSheet(f"color:#ff6b6b; padding:15px; background:#141b25; border: 1px solid {BORDER_COL}; border-radius:8px; font-size:12px;")
            exp_lay.addWidget(status_msg)
            exp_lay.addStretch()
        else:
            # Settings Grid
            export_panel = QFrame()
            export_panel.setStyleSheet(f"background: #141b25; border: 1px solid {BORDER_COL}; border-radius: 8px; padding: 15px;")
            ep_lay = QGridLayout(export_panel)
            ep_lay.setSpacing(12)
            
            ep_lay.addWidget(QLabel("Language:"), 0, 0)
            self.export_lang = QComboBox()
            self.export_lang.addItems(["English", "Hindi", "Marathi", "Tamil", "Telugu", "Kannada", "French", "Spanish"])
            ep_lay.addWidget(self.export_lang, 0, 1)
            
            ep_lay.addWidget(QLabel("Format:"), 0, 2)
            self.export_format = QComboBox()
            self.export_format.addItems(["WAV", "MP3", "OGG", "FLAC"])
            ep_lay.addWidget(self.export_format, 0, 3)
            
            ep_lay.addWidget(QLabel("Speed:"), 1, 0)
            self.export_speed = QSpinBox()
            self.export_speed.setRange(50, 300)
            self.export_speed.setValue(150)
            self.export_speed.setSuffix(" wpm")
            ep_lay.addWidget(self.export_speed, 1, 1)
            
            ep_lay.addWidget(QLabel("Volume:"), 1, 2)
            self.export_volume = QSpinBox()
            self.export_volume.setRange(0, 100)
            self.export_volume.setValue(90)
            self.export_volume.setSuffix("%")
            ep_lay.addWidget(self.export_volume, 1, 3)
            
            exp_lay.addWidget(export_panel)
            
            # File destination path selector
            path_panel = QFrame()
            path_panel.setStyleSheet(f"background: #141b25; border: 1px solid {BORDER_COL}; border-radius: 8px; padding: 12px;")
            path_lay = QVBoxLayout(path_panel)
            path_lay.setSpacing(6)
            
            path_label = QLabel("OUTPUT FILE PATH")
            path_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px; font-weight: bold;")
            path_lay.addWidget(path_label)
            
            path_row = QHBoxLayout()
            self.export_path = QLineEdit()
            self.export_path.setPlaceholderText("Select file path...")
            self.export_path.setReadOnly(True)
            self.export_path.setStyleSheet(f"""
                QLineEdit {{
                    background-color: #0c0f14;
                    color: {TEXT_PRIMARY};
                    border: 1px solid {BORDER_COL};
                    border-radius: 6px;
                    padding: 8px;
                }}
            """)
            path_row.addWidget(self.export_path, 1)
            
            browse_btn = QPushButton("📁 Browse")
            browse_btn.setMinimumHeight(35)
            browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            browse_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-size: 11px; font-weight: bold; padding: 0px 15px;
                }}
                QPushButton:hover {{ background: {BORDER_COL}; }}
            """)
            browse_btn.clicked.connect(self._browse_export_path)
            path_row.addWidget(browse_btn)
            path_lay.addLayout(path_row)
            exp_lay.addWidget(path_panel)
            
            # Export Action Button
            self.export_btn = QPushButton("💾 Export to File")
            self.export_btn.setMinimumHeight(42)
            self.export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.export_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {ACCENT_GREEN}; color: #1a1b26; border: none; border-radius: 6px; font-weight: bold; font-size: 12px;
                }}
                QPushButton:hover {{ background: #00e896; }}
            """)
            self.export_btn.clicked.connect(self._export_to_file)
            exp_lay.addWidget(self.export_btn)
            exp_lay.addStretch()
            
        self.mode_stack.addWidget(export_ctrl)
        right_layout.addWidget(self.mode_stack, 1)

        # Status Footer
        self.audio_status = QLabel("Ready")
        self.audio_status.setStyleSheet(f"color:{TEXT_MUTED}; font-size:11px;")
        right_layout.addWidget(self.audio_status)
        
        self.export_status = self.audio_status
        cols_layout.addWidget(right_col, 1)

    def _get_pill_style(self, active):
        if active:
            return f"""
                QPushButton {{
                    background-color: {ACCENT_GREEN};
                    color: #1a1b26;
                    border: none;
                    border-radius: 15px;
                    padding: 6px 16px;
                    font-weight: bold;
                    font-size: 11px;
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {TEXT_MUTED};
                    border: 1px solid {BORDER_COL};
                    border-radius: 15px;
                    padding: 6px 16px;
                    font-weight: bold;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    color: {TEXT_PRIMARY};
                    border-color: {TEXT_MUTED};
                }}
            """

    def _set_mode(self, mode_idx):
        self.mode_stack.setCurrentIndex(mode_idx)
        self.btn_play_mode.setChecked(mode_idx == 0)
        self.btn_export_mode.setChecked(mode_idx == 1)
        
        self.btn_play_mode.setStyleSheet(self._get_pill_style(mode_idx == 0))
        self.btn_export_mode.setStyleSheet(self._get_pill_style(mode_idx == 1))

    def _update_speed_label(self, val):
        self.speed_label.setText(f"{val} wpm")
        try:
            audio_engine.set_rate(val)
        except:
            pass

    def _update_vol_label(self, val):
        self.vol_label.setText(f"{val}%")
        try:
            audio_engine.set_volume(val / 100.0)
        except:
            pass

    def _play_audio(self):
        text = self.audio_input.toPlainText()
        if not text:
            self.audio_status.setText("❌ Enter text first")
            return
        lang = 'hi' if self.audio_lang.currentText() != 'English' else 'en'
        try:
            audio_engine.speak(text, language=lang)
            self.audio_status.setText("▶️ Playing...")
        except Exception as e:
            self.audio_status.setText(f"❌ Error: {str(e)}")

    def _stop_audio(self):
        try:
            audio_engine.stop()
            self.audio_status.setText("⏹️ Stopped")
        except:
            pass

    def _browse_export_path(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Audio File As",
            "",
            f"Audio Files (*.wav *.mp3 *.ogg *.flac)"
        )
        if file_path:
            self.export_path.setText(file_path)

    def _export_to_file(self):
        if not self.export_available:
            self.export_status.setText("❌ Export not available")
            return

        text = self.export_input.toPlainText()
        if not text:
            self.export_status.setText("❌ Enter text first")
            return

        file_path = self.export_path.text()
        if not file_path:
            from pathlib import Path
            export_dir = Path.home() / "Music" / "BrailleExports"
            export_dir.mkdir(parents=True, exist_ok=True)
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            format_ext = self.export_format.currentText().lower()
            file_path = str(export_dir / f"audio_{timestamp}.{format_ext}")
            self.export_path.setText(file_path)

        try:
            success, message = self.audio_exporter.text_to_audio_file(
                text,
                file_path,
                format=self.export_format.currentText(),
                speed=self.export_speed.value(),
                volume=self.export_volume.value() / 100.0,
                language=self.export_lang.currentText()
            )
            self.export_status.setText(message)
            if success:
                self.export_status.setStyleSheet(f"color:{ACCENT_GREEN};")
            else:
                self.export_status.setStyleSheet("color:#ff6b6b;")
        except Exception as e:
            self.export_status.setText(f"❌ Error: {str(e)}")
            self.export_status.setStyleSheet("color:#ff6b6b;")




class SpeechPage(QWidget):
    """Speech-to-Braille page - Convert voice to Braille."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize speech converter first
        try:
            from speech_to_braille import speech_converter
            self.speech_converter = speech_converter
            self.speech_available = True
        except ImportError:
            self.speech_converter = None
            self.speech_available = False
        
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # ── TITLE ────────────────────────────────────────────
        title = QLabel("Voice Translation Studio")
        title.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:20px; font-weight:bold;")
        layout.addWidget(title)

        # ── MAIN COLUMNS CONTAINER ──────────────────────────
        main_cols = QWidget()
        cols_layout = QHBoxLayout(main_cols)
        cols_layout.setContentsMargins(0, 0, 0, 0)
        cols_layout.setSpacing(25)
        layout.addWidget(main_cols, 1)

        # ── LEFT COLUMN: Voice Capture & Settings ────────────
        left_col = QWidget()
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        pref_label = QLabel("TRANSLATION PREFERENCES")
        pref_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        left_layout.addWidget(pref_label)
        
        # Preferences Panel
        pref_panel = QFrame()
        pref_panel.setStyleSheet(f"background: #141b25; border: 1px solid {BORDER_COL}; border-radius: 8px; padding: 15px;")
        pp_lay = QVBoxLayout(pref_panel)
        pp_lay.setSpacing(10)
        
        # From Lang
        from_row = QHBoxLayout()
        from_lbl = QLabel("From Language:")
        from_row.addWidget(from_lbl)
        self.input_lang_combo = QComboBox()
        self.input_lang_combo.addItems(["English (US)", "English (UK)", "Hindi", "Marathi", "Spanish", "French"])
        from_row.addWidget(self.input_lang_combo)
        pp_lay.addLayout(from_row)
        
        # To Lang
        to_row = QHBoxLayout()
        to_lbl = QLabel("To Braille:")
        to_row.addWidget(to_lbl)
        self.output_lang_combo = QComboBox()
        self.output_lang_combo.addItems(["English", "Hindi", "Marathi"])
        self.output_lang_combo.setCurrentText("English")
        to_row.addWidget(self.output_lang_combo)
        pp_lay.addLayout(to_row)
        
        # Status Label
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 11px; font-weight: bold;")
        pp_lay.addWidget(self.status_label)
        self._update_status()
        
        left_layout.addWidget(pref_panel)
        
        # Input Method Label
        input_method_lbl = QLabel("INPUT METHOD")
        input_method_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        left_layout.addWidget(input_method_lbl)
        
        # Tab Widget
        self.input_tabs = QTabWidget()
        self.input_tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid {BORDER_COL}; background: #0c0f14; border-radius: 8px; }}
            QTabBar::tab {{ padding: 8px 12px; background: #0c0f14; color: {TEXT_MUTED}; border: 1px solid {BORDER_COL}; margin-right: 4px; border-top-left-radius: 4px; border-top-right-radius: 4px; font-size: 11px; }}
            QTabBar::tab:selected {{ background: #141b25; color: {ACCENT_GREEN}; font-weight: bold; border-bottom: 2px solid {ACCENT_GREEN}; }}
        """)
        
        # Tab 1: Microphone
        mic_widget = QWidget()
        mic_layout = QVBoxLayout(mic_widget)
        mic_layout.setContentsMargins(15, 15, 15, 15)
        mic_layout.setSpacing(10)
        
        timeout_row = QHBoxLayout()
        timeout_row.addWidget(QLabel("⏱️ Record Time:"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setValue(10)
        self.timeout_spin.setMaximumWidth(80)
        self.timeout_spin.setSuffix(" sec")
        timeout_row.addWidget(self.timeout_spin)
        timeout_row.addStretch()
        mic_layout.addLayout(timeout_row)
        
        mic_btns = QHBoxLayout()
        mic_btns.setSpacing(10)
        self.listen_btn = QPushButton("🎤 Start Recording")
        self.listen_btn.setMinimumHeight(35)
        self.listen_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.listen_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_GREEN}; color: #0b0d12; border: none; border-radius: 6px; font-size: 11px; font-weight: bold;
            }}
            QPushButton:hover {{ background: #3fa38d; }}
        """)
        self.listen_btn.clicked.connect(self._listen_microphone)
        mic_btns.addWidget(self.listen_btn, 1)
        
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.setMinimumHeight(35)
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-size: 11px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_listening)
        mic_btns.addWidget(self.stop_btn, 1)
        mic_layout.addLayout(mic_btns)
        
        mic_tip = QLabel("Speak clearly after clicking 'Start Recording'.")
        mic_tip.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px;")
        mic_layout.addWidget(mic_tip)
        mic_layout.addStretch()
        
        self.input_tabs.addTab(mic_widget, "🎤 Mic")
        
        # Tab 2: Audio File
        file_widget = QWidget()
        file_layout = QVBoxLayout(file_widget)
        file_layout.setContentsMargins(15, 15, 15, 15)
        file_layout.setSpacing(10)
        
        self.file_path_label = QLabel("📂 No file selected")
        self.file_path_label.setWordWrap(True)
        self.file_path_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        file_layout.addWidget(self.file_path_label)
        
        file_btns = QHBoxLayout()
        self.browse_btn = QPushButton("📂 Browse")
        self.browse_btn.setMinimumHeight(35)
        self.browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-size: 11px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        self.browse_btn.clicked.connect(self._browse_file)
        file_btns.addWidget(self.browse_btn, 1)
        
        self.convert_file_btn = QPushButton("🔄 Convert")
        self.convert_file_btn.setMinimumHeight(35)
        self.convert_file_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.convert_file_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_GREEN}; color: #0b0d12; border: none; border-radius: 6px; font-size: 11px; font-weight: bold;
            }}
            QPushButton:hover {{ background: #3fa38d; }}
        """)
        self.convert_file_btn.clicked.connect(self._convert_file)
        file_btns.addWidget(self.convert_file_btn, 1)
        file_layout.addLayout(file_btns)
        file_layout.addStretch()
        
        self.input_tabs.addTab(file_widget, "📁 File")
        
        # Tab 3: Manual Text
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(15, 15, 15, 15)
        text_layout.setSpacing(10)
        
        self.manual_input = QTextEdit()
        self.manual_input.setPlaceholderText("Or type text here directly...")
        self.manual_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: #0c0f14;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 6px;
                padding: 10px;
                font-size: 12px;
            }}
        """)
        text_layout.addWidget(self.manual_input, 1)
        
        self.convert_text_btn = QPushButton("🔄 Translate Text")
        self.convert_text_btn.setMinimumHeight(35)
        self.convert_text_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.convert_text_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_GREEN}; color: #0b0d12; border: none; border-radius: 6px; font-size: 11px; font-weight: bold;
            }}
            QPushButton:hover {{ background: #3fa38d; }}
        """)
        self.convert_text_btn.clicked.connect(self._convert_text)
        text_layout.addWidget(self.convert_text_btn)
        
        self.input_tabs.addTab(text_widget, "⌨️ Text")
        
        left_layout.addWidget(self.input_tabs, 1)
        cols_layout.addWidget(left_col, 1)

        # ── RIGHT COLUMN: Output & Speech feedback ───────────
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        out_lbl = QLabel("TRANSLATED BRAILLE")
        out_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        right_layout.addWidget(out_lbl)
        
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setPlaceholderText("Voice translation will appear here...")
        self.output_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: #0c0f14;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
            }}
        """)
        right_layout.addWidget(self.output_display, 1)
        
        # Buttons under output
        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(12)
        
        copy_btn = QPushButton("📋 Copy Result")
        copy_btn.setMinimumHeight(38)
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-size: 11px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        copy_btn.clicked.connect(self._copy_output)
        btn_lay.addWidget(copy_btn, 1)
        
        speak_btn = QPushButton("🔊 Speak Output")
        speak_btn.setMinimumHeight(38)
        speak_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        speak_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-size: 11px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        speak_btn.clicked.connect(self._speak_output)
        btn_lay.addWidget(speak_btn, 1)
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setMinimumHeight(38)
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-size: 11px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        clear_btn.clicked.connect(lambda: self.output_display.clear())
        btn_lay.addWidget(clear_btn, 1)
        right_layout.addLayout(btn_lay)
        
        cols_layout.addWidget(right_col, 1)
    
    def _update_status(self):
        if self.speech_available:
            self.status_label.setText("✅ Ready to convert speech to Braille")
        else:
            self.status_label.setText("⚠️ Install package: pip install SpeechRecognition | You can still type text manually")
    
    def _listen_microphone(self):
        if not self.speech_available:
            QMessageBox.warning(self, "Error", "Install package:\npip install SpeechRecognition")
            return
        
        self.listen_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        try:
            input_lang_map = {
                "English (US)": "en-US", "English (UK)": "en-GB",
                "Hindi": "hi-IN", "Marathi": "mr-IN",
                "Spanish": "es-ES", "French": "fr-FR"
            }
            
            lang_code = input_lang_map.get(self.input_lang_combo.currentText(), "en-US")
            timeout = self.timeout_spin.value()
            
            self.status_label.setText(f"🎤 Listening for {timeout}s...")
            
            text = self.speech_converter.recognize_from_microphone(
                language=lang_code,
                timeout=timeout
            )
            
            if text:
                self.manual_input.setText(text)
                self.status_label.setText(f"✅ Got: '{text}' — Converting...")
                self._convert_text()
            else:
                self.status_label.setText("❌ No speech recognized")
        
        except Exception as e:
            self.status_label.setText(f"❌ Error: {str(e)}")
        
        finally:
            self.listen_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
    
    def _stop_listening(self):
        self.listen_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("⏹️ Stopped")
    
    def _browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.wav *.flac);;All Files (*)"
        )
        if file_path:
            self.file_path = file_path
            filename = file_path.split('/')[-1]
            self.file_path_label.setText(f"✅ {filename}")
    
    def _convert_file(self):
        if not hasattr(self, 'file_path'):
            QMessageBox.warning(self, "Error", "Select an audio file first")
            return
        
        if not self.speech_available:
            QMessageBox.warning(self, "Error", "Install SpeechRecognition")
            return
        
        try:
            lang_code = {
                "English (US)": "en-US", "English (UK)": "en-GB",
                "Hindi": "hi-IN", "Marathi": "mr-IN",
                "Spanish": "es-ES", "French": "fr-FR"
            }.get(self.input_lang_combo.currentText(), "en-US")
            
            text = self.speech_converter.recognize_from_file(
                self.file_path,
                language=lang_code
            )
            
            if text:
                self.manual_input.setText(text)
                self._convert_text()
                self.status_label.setText(f"✅ Processed: '{text}'")
        
        except Exception as e:
            self.status_label.setText(f"❌ Error: {str(e)}")
    
    def _convert_text(self):
        text = self.manual_input.toPlainText()
        if not text:
            QMessageBox.warning(self, "Error", "Enter text first")
            return
        
        try:
            lang = self.output_lang_combo.currentText()
            braille = self.speech_converter.speech_to_braille(text, language_braille=lang)
            
            if braille:
                self.output_display.setText(braille)
                self.status_label.setText(f"✅ {lang} Braille ({len(braille)} chars)")
                announce(f"Converted. {len(braille)} characters")
            else:
                self.status_label.setText("❌ Conversion failed")
        
        except Exception as e:
            self.status_label.setText(f"❌ Error: {str(e)}")
    
    def _copy_output(self):
        braille = self.output_display.toPlainText()
        if braille:
            clipboard_manager.set_clipboard_text(braille)
            self.status_label.setText("✅ Copied!")
            announce("Copied to clipboard")
        else:
            QMessageBox.warning(self, "Error", "No output")
    
    def _speak_output(self):
        braille = self.output_display.toPlainText()
        if not braille:
            QMessageBox.warning(self, "Error", "No output")
            return
        
        try:
            audio_engine.speak(braille, language="English")
            announce("Speaking")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")


class AdvancedGradesPage(QWidget):
    """Advanced Braille Grades workspace console."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # ── TITLE ────────────────────────────────────────────
        title = QLabel("Braille Grades Studio")
        title.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:20px; font-weight:bold;")
        layout.addWidget(title)

        # ── MAIN COLUMNS CONTAINER ──────────────────────────
        main_cols = QWidget()
        cols_layout = QHBoxLayout(main_cols)
        cols_layout.setContentsMargins(0, 0, 0, 0)
        cols_layout.setSpacing(25)
        layout.addWidget(main_cols, 1)

        # ── LEFT COLUMN: Text Input ─────────────────────────
        left_col = QWidget()
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        inp_label = QLabel("TEXT INPUT")
        inp_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        left_layout.addWidget(inp_label)
        
        self.grade_input = QTextEdit()
        self.grade_input.setPlaceholderText("Enter regular text here to translate...")
        self.grade_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: #0c0f14;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 15px;
                font-size: 13px;
            }}
            QTextEdit:focus {{
                border: 1px solid {ACCENT_GREEN};
            }}
        """)
        self.grade_input.textChanged.connect(self._convert_grade)
        left_layout.addWidget(self.grade_input, 1)
        
        cols_layout.addWidget(left_col, 1)

        # ── RIGHT COLUMN: Preferences & Braille Output ──────
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        pref_label = QLabel("TRANSLATION PREFERENCES")
        pref_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        right_layout.addWidget(pref_label)
        
        # Preferences Panel
        pref_panel = QFrame()
        pref_panel.setStyleSheet(f"background: #141b25; border: 1px solid {BORDER_COL}; border-radius: 8px; padding: 15px;")
        pp_lay = QVBoxLayout(pref_panel)
        pp_lay.setSpacing(10)
        
        grade_row = QHBoxLayout()
        grade_lbl = QLabel("Target Grade:")
        grade_row.addWidget(grade_lbl)
        self.grade_combo = QComboBox()
        self.grade_combo.addItems(["Grade 1 (Full)", "Grade 2 (Contractions)", "Grade 3 (Abbreviated)"])
        self.grade_combo.currentIndexChanged.connect(self._convert_grade)
        grade_row.addWidget(self.grade_combo)
        pp_lay.addLayout(grade_row)
        
        self.grade_info = QLabel("Grade 1: Full character-by-character mapping")
        self.grade_info.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 11px; font-weight: bold;")
        self.grade_info.setWordWrap(True)
        pp_lay.addWidget(self.grade_info)
        
        right_layout.addWidget(pref_panel)
        
        # Braille Output
        out_lbl = QLabel("BRAILLE OUTPUT")
        out_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        right_layout.addWidget(out_lbl)
        
        self.grade_output = QTextEdit()
        self.grade_output.setReadOnly(True)
        self.grade_output.setPlaceholderText("Braille translation will appear here...")
        self.grade_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: #0c0f14;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
            }}
        """)
        right_layout.addWidget(self.grade_output, 1)
        
        # Buttons under output
        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(12)
        
        copy_btn = QPushButton("📋 Copy Result")
        copy_btn.setMinimumHeight(38)
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-size: 11px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        copy_btn.clicked.connect(self._copy_result)
        btn_lay.addWidget(copy_btn, 1)
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setMinimumHeight(38)
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-size: 11px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        clear_btn.clicked.connect(self._clear_fields)
        btn_lay.addWidget(clear_btn, 1)
        right_layout.addLayout(btn_lay)
        
        cols_layout.addWidget(right_col, 1)

    def _convert_grade(self):
        text = self.grade_input.toPlainText()
        if not text:
            self.grade_output.clear()
            return

        grade = self.grade_combo.currentIndex()
        if grade == 0:
            result = grade_converter.text_to_grade1(text)
            self.grade_info.setText("✓ Grade 1: Direct character-by-character mapping")
        elif grade == 1:
            result = grade_converter.text_to_grade2(text)
            self.grade_info.setText("✓ Grade 2: Contractions enabled (Standard/Faster)")
        else:
            result = grade_converter.text_to_grade3(text)
            self.grade_info.setText("✓ Grade 3: Highly abbreviated shorthand (Experimental)")

        self.grade_output.setPlainText(result)

    def _copy_result(self):
        text = self.grade_output.toPlainText()
        if text:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(text)
            announce("Copied to clipboard")

    def _clear_fields(self):
        self.grade_input.clear()
        self.grade_output.clear()


class MathPage(QWidget):
    """Mathematical & Scientific Notation workspace studio."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # ── TITLE ────────────────────────────────────────────
        title = QLabel("Math Notation Studio")
        title.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:20px; font-weight:bold;")
        layout.addWidget(title)

        # ── MAIN COLUMNS CONTAINER ──────────────────────────
        main_cols = QWidget()
        cols_layout = QHBoxLayout(main_cols)
        cols_layout.setContentsMargins(0, 0, 0, 0)
        cols_layout.setSpacing(25)
        layout.addWidget(main_cols, 1)

        # ── LEFT COLUMN: Math Input & Keyboard ───────────────
        left_col = QWidget()
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        inp_label = QLabel("MATH EXPRESSION")
        inp_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        left_layout.addWidget(inp_label)
        
        self.math_input = QTextEdit()
        self.math_input.setPlaceholderText("Type a mathematical expression here (e.g., x² + y² = z² or pi * r²)...")
        self.math_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: #0c0f14;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
            }}
            QTextEdit:focus {{
                border: 1px solid {ACCENT_GREEN};
            }}
        """)
        self.math_input.textChanged.connect(self._convert_math)
        left_layout.addWidget(self.math_input, 2)
        
        # Virtual Math Keyboard
        kbd_label = QLabel("QUICK INSERT KEYBOARD")
        kbd_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        left_layout.addWidget(kbd_label)
        
        kbd_panel = QFrame()
        kbd_panel.setStyleSheet(f"background: #141b25; border: 1px solid {BORDER_COL}; border-radius: 8px; padding: 12px;")
        kbd_grid = QGridLayout(kbd_panel)
        kbd_grid.setSpacing(8)
        kbd_grid.setContentsMargins(5, 5, 5, 5)
        
        symbols = [
            ("+", "+"), ("-", "-"), ("×", "×"), ("÷", "÷"), ("=", "="),
            ("x²", "²"), ("x³", "³"), ("x⁻¹", "⁻¹"), ("√x", "√"),
            ("π pi", "π"), ("± pm", "±"), ("∑ sum", "∑"), ("∞ inf", "∞"),
            ("H₂O", "H₂O"), ("CO₂", "CO₂")
        ]
        
        row, col = 0, 0
        for label, char in symbols:
            btn = QPushButton(label)
            btn.setMinimumHeight(30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: #1e2533; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 4px; font-size: 11px; font-weight: bold;
                }}
                QPushButton:hover {{ background: {BORDER_COL}; }}
            """)
            btn.clicked.connect(lambda checked, c=char: self.math_input.insertPlainText(c))
            kbd_grid.addWidget(btn, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1
                
        left_layout.addWidget(kbd_panel, 3)
        cols_layout.addWidget(left_col, 1)

        # ── RIGHT COLUMN: Output, Action, Cheat Sheet ────────
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        out_lbl = QLabel("MATHEMATICAL BRAILLE (NEMETH CODE)")
        out_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        right_layout.addWidget(out_lbl)
        
        self.math_output = QTextEdit()
        self.math_output.setReadOnly(True)
        self.math_output.setPlaceholderText("Mathematical Braille will appear here...")
        self.math_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: #0c0f14;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 15px;
                font-size: 18px;
            }}
        """)
        right_layout.addWidget(self.math_output, 2)
        
        # Action Row
        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(12)
        
        copy_btn = QPushButton("📋 Copy Braille")
        copy_btn.setMinimumHeight(38)
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-size: 11px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        copy_btn.clicked.connect(self._copy_result)
        btn_lay.addWidget(copy_btn, 1)
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setMinimumHeight(38)
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-size: 11px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        clear_btn.clicked.connect(self._clear_fields)
        btn_lay.addWidget(clear_btn, 1)
        right_layout.addLayout(btn_lay)
        
        # Cheat Sheet Card
        guide_card = QFrame()
        guide_card.setStyleSheet(f"background: #141b25; border: 1px solid {BORDER_COL}; border-radius: 8px; padding: 15px;")
        gc_lay = QVBoxLayout(guide_card)
        gc_lay.setSpacing(8)
        
        gc_title = QLabel("📚 Nemeth Braille Reference Guide")
        gc_title.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 11px; font-weight: bold;")
        gc_lay.addWidget(gc_title)
        
        gc_text = QLabel(
            "• Plus (+) = ⠬   • Minus (-) = ⠤   • Equal (=) = ⠨⠅\n"
            "• Times (×) = ⠈⠡   • Divide (÷) = ⠈⠢   • Power (^) = ⠘⠆\n"
            "• Pi (π) = ⠐⠏   • Sum (Σ) = ⠐⠎   • Root (√) = ⠜⠡⠗⠞"
        )
        gc_text.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 11px; line-height: 1.6;")
        gc_lay.addWidget(gc_text)
        
        right_layout.addWidget(guide_card, 3)
        cols_layout.addWidget(right_col, 1)

    def _convert_math(self):
        text = self.math_input.toPlainText()
        if not text:
            self.math_output.clear()
            return
        result = math_converter.convert_math_expression(text)
        self.math_output.setPlainText(result)

    def _copy_result(self):
        text = self.math_output.toPlainText()
        if text:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(text)
            announce("Copied to clipboard")

    def _clear_fields(self):
        self.math_input.clear()
        self.math_output.clear()


class DocumentPage(QWidget):
    """PDF & Document Processing workspace studio."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # ── TITLE ────────────────────────────────────────────
        title = QLabel("Document Reader Studio")
        title.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:20px; font-weight:bold;")
        layout.addWidget(title)

        # ── MAIN COLUMNS CONTAINER ──────────────────────────
        main_cols = QWidget()
        cols_layout = QHBoxLayout(main_cols)
        cols_layout.setContentsMargins(0, 0, 0, 0)
        cols_layout.setSpacing(25)
        layout.addWidget(main_cols, 1)

        # ── LEFT COLUMN: PDF / Single Document ───────────────
        left_col = QWidget()
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        pdf_label = QLabel("SINGLE DOCUMENT CONVERSION")
        pdf_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        left_layout.addWidget(pdf_label)
        
        # PDF Card
        pdf_panel = QFrame()
        pdf_panel.setStyleSheet(f"background: #141b25; border: 1px solid {BORDER_COL}; border-radius: 8px; padding: 20px;")
        pp_lay = QVBoxLayout(pdf_panel)
        pp_lay.setSpacing(12)
        
        upload_icon = QLabel("📄")
        upload_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_icon.setStyleSheet("font-size: 40px; background: transparent;")
        pp_lay.addWidget(upload_icon)
        
        self.pdf_status = QLabel("Select a PDF to begin conversion")
        self.pdf_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pdf_status.setWordWrap(True)
        self.pdf_status.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; font-weight: bold;")
        pp_lay.addWidget(self.pdf_status)
        
        self.pdf_btn = QPushButton("📂 Select PDF Document")
        self.pdf_btn.setMinimumHeight(40)
        self.pdf_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pdf_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_GREEN}; color: #0b0d12; border: none; border-radius: 6px; font-size: 12px; font-weight: bold;
            }}
            QPushButton:hover {{ background: #3fa38d; }}
        """)
        self.pdf_btn.clicked.connect(self._select_pdf)
        pp_lay.addWidget(self.pdf_btn)
        
        left_layout.addWidget(pdf_panel)
        
        # Embosser Options Panel
        opt_panel = QFrame()
        opt_panel.setStyleSheet(f"background: #141b25; border: 1px solid {BORDER_COL}; border-radius: 8px; padding: 15px;")
        op_lay = QVBoxLayout(opt_panel)
        op_lay.setSpacing(10)
        
        op_title = QLabel("⚙️ Export Options")
        op_title.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 11px; font-weight: bold;")
        op_lay.addWidget(op_title)
        
        self.embosser_check = QCheckBox("Format output for physical embosser (80 chars/line limit)")
        self.embosser_check.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 11px;")
        op_lay.addWidget(self.embosser_check)
        
        left_layout.addWidget(opt_panel)
        left_layout.addStretch()
        cols_layout.addWidget(left_col, 1)

        # ── RIGHT COLUMN: Batch Processing ───────────────────
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        batch_label = QLabel("BATCH FILE CONVERTER")
        batch_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        right_layout.addWidget(batch_label)
        
        batch_panel = QFrame()
        batch_panel.setStyleSheet(f"background: #141b25; border: 1px solid {BORDER_COL}; border-radius: 8px; padding: 20px;")
        bp_lay = QVBoxLayout(batch_panel)
        bp_lay.setSpacing(12)
        
        folder_icon = QLabel("📁")
        folder_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        folder_icon.setStyleSheet("font-size: 40px; background: transparent;")
        bp_lay.addWidget(folder_icon)
        
        self.batch_status = QLabel("Select a directory containing .txt documents to batch convert")
        self.batch_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.batch_status.setWordWrap(True)
        self.batch_status.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; font-weight: bold;")
        bp_lay.addWidget(self.batch_status)
        
        self.batch_btn = QPushButton("📁 Select Input Directory")
        self.batch_btn.setMinimumHeight(40)
        self.batch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.batch_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-size: 12px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        self.batch_btn.clicked.connect(self._select_batch_folder)
        bp_lay.addWidget(self.batch_btn)
        
        right_layout.addWidget(batch_panel)
        
        # Batch Log Box
        log_lbl = QLabel("CONVERSION CONSOLE")
        log_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        right_layout.addWidget(log_lbl)
        
        self.console_log = QTextEdit()
        self.console_log.setReadOnly(True)
        self.console_log.setPlaceholderText("Console logs will print here during conversion...")
        self.console_log.setStyleSheet(f"""
            QTextEdit {{
                background-color: #0c0f14;
                color: #5AA6FF;
                font-family: 'Consolas', 'Courier New', monospace;
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 10px;
                font-size: 11px;
            }}
        """)
        right_layout.addWidget(self.console_log, 1)
        
        cols_layout.addWidget(right_col, 1)

    def _select_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if path:
            name = os.path.basename(path)
            self.pdf_status.setText(f"⚙️ Processing: {name}...")
            output = path.replace('.pdf', '_braille.txt')
            
            # Read text first
            text, status = doc_processor.read_pdf_text(path)
            if not text:
                self.pdf_status.setText(f"❌ {status}")
                return
                
            # Perform translation
            braille_text = text_to_braille(text)
            
            # Formatting check
            if self.embosser_check.isChecked():
                success, msg = doc_processor.export_embosser_format(braille_text, output)
            else:
                success, msg = doc_processor.save_text_file(braille_text, output)
                
            if success:
                self.pdf_status.setText(f"✓ Converted successfully!\nSaved: {os.path.basename(output)}")
            else:
                self.pdf_status.setText(f"❌ Error: {msg}")

    def _select_batch_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with TXT files")
        if folder:
            base = os.path.basename(folder)
            output_folder = folder + "_braille_output"
            self.console_log.append(f">> Starting batch conversion in: {folder}")
            self.console_log.append(f">> Saving outputs to: {output_folder}")
            
            count, msg = doc_processor.batch_convert_files(folder, output_folder)
            self.batch_status.setText(f"✓ Converted folder: {base}")
            self.console_log.append(f">> {msg}")
            self.console_log.append(">> Batch conversion completed successfully!")



class LearningPage(QWidget):
    """Refined Interactive Braille Learning module."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_quiz = None
        self.active_lesson = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # ── TITLE ────────────────────────────────────────────
        title = QLabel("Learning Center")
        title.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:20px; font-weight:bold;")
        layout.addWidget(title)

        # ── MAIN COLUMNS CONTAINER ──────────────────────────
        main_cols = QWidget()
        cols_layout = QHBoxLayout(main_cols)
        cols_layout.setContentsMargins(0, 0, 0, 0)
        cols_layout.setSpacing(25)
        layout.addWidget(main_cols, 1)

        # ── LEFT COLUMN: Curriculum List & Progress ──────────
        left_col = QWidget()
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        curriculum_label = QLabel("YOUR CURRICULUM")
        curriculum_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        left_layout.addWidget(curriculum_label)
        
        # Progress card
        progress_card = QFrame()
        progress_card.setStyleSheet(f"background: #141b25; border: 1px solid {BORDER_COL}; border-radius: 8px; padding: 15px;")
        pc_layout = QVBoxLayout(progress_card)
        pc_layout.setSpacing(10)
        
        self.stats_lbl = QLabel("0/3 Lessons Completed")
        self.stats_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; font-weight: bold;")
        pc_layout.addWidget(self.stats_lbl)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #0c0f14;
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {ACCENT_GREEN};
                border-radius: 4px;
            }}
        """)
        pc_layout.addWidget(self.progress_bar)
        left_layout.addWidget(progress_card)
        
        # Lessons List Widget
        self.lessons_list = QListWidget()
        self.lessons_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.lessons_list.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
            }}
            QListWidget::item {{
                background: {CARD_BG};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                margin-bottom: 8px;
            }}
            QListWidget::item:selected {{
                background: #111520;
                border-color: {ACCENT_GREEN};
            }}
        """)
        self.lessons_list.itemSelectionChanged.connect(self._on_lesson_selected)
        left_layout.addWidget(self.lessons_list, 1)
        
        cols_layout.addWidget(left_col, 1)

        # Populate lessons
        self._populate_lessons()

        # ── RIGHT COLUMN: Interactive Workspace ──────────────
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        workspace_label = QLabel("STUDY WORKSPACE")
        workspace_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        right_layout.addWidget(workspace_label)

        self.workspace_stack = QStackedWidget()
        self.workspace_stack.setStyleSheet(f"""
            QStackedWidget {{
                background: #141b25;
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
            }}
        """)
        
        # 1. Default Welcome Page
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setContentsMargins(30, 40, 30, 40)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        welcome_icon = QLabel("📖")
        welcome_icon.setStyleSheet("font-size: 48px; margin-bottom: 10px; background: transparent;")
        welcome_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome_icon)
        
        welcome_title = QLabel("Start Your Braille Journey")
        welcome_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold; background: transparent;")
        welcome_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome_title)
        
        welcome_desc = QLabel("Select any lesson on the left to access study materials, flashcards, and interactive practice quizzes.")
        welcome_desc.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; line-height: 1.4; background: transparent;")
        welcome_desc.setWordWrap(True)
        welcome_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome_desc)
        
        self.workspace_stack.addWidget(welcome_widget)

        # 2. Lesson View Page
        self.lesson_widget = QWidget()
        lesson_layout = QVBoxLayout(self.lesson_widget)
        lesson_layout.setContentsMargins(25, 25, 25, 25)
        lesson_layout.setSpacing(15)
        
        self.lesson_title_lbl = QLabel("")
        self.lesson_title_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold; background: transparent;")
        lesson_layout.addWidget(self.lesson_title_lbl)
        
        self.lesson_text = QTextEdit()
        self.lesson_text.setReadOnly(True)
        self.lesson_text.setStyleSheet(f"""
            QTextEdit {{
                background: transparent;
                border: none;
                color: {TEXT_PRIMARY};
                font-size: 13px;
                line-height: 1.6;
            }}
        """)
        lesson_layout.addWidget(self.lesson_text)
        
        lesson_actions = QHBoxLayout()
        lesson_actions.addStretch()
        
        self.mark_complete_btn = QPushButton("Mark Completed & Start Quiz")
        self.mark_complete_btn.setMinimumSize(220, 38)
        self.mark_complete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mark_complete_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_GREEN}; color: #0b0d12; border: none; border-radius: 6px; font-weight: bold; font-size: 12px;
            }}
            QPushButton:hover {{ background: #3fa38d; }}
        """)
        self.mark_complete_btn.clicked.connect(self._mark_lesson_complete_action)
        lesson_actions.addWidget(self.mark_complete_btn)
        
        lesson_layout.addLayout(lesson_actions)
        self.workspace_stack.addWidget(self.lesson_widget)

        # 3. Quiz View Page
        self.quiz_widget = QWidget()
        quiz_layout = QVBoxLayout(self.quiz_widget)
        quiz_layout.setContentsMargins(25, 25, 25, 25)
        quiz_layout.setSpacing(15)
        
        self.quiz_header_lbl = QLabel("")
        self.quiz_header_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 11px; font-weight: bold; letter-spacing: 0.5px; background: transparent;")
        quiz_layout.addWidget(self.quiz_header_lbl)
        
        self.quiz_question_lbl = QLabel("")
        self.quiz_question_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold; margin-top: 5px; background: transparent;")
        self.quiz_question_lbl.setWordWrap(True)
        quiz_layout.addWidget(self.quiz_question_lbl)
        
        # Answer entry field
        self.quiz_input = QLineEdit()
        self.quiz_input.setPlaceholderText("Type your translation here...")
        self.quiz_input.setFixedHeight(38)
        self.quiz_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #0c0f14;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {ACCENT_GREEN};
            }}
        """)
        self.quiz_input.returnPressed.connect(self._submit_quiz_answer)
        quiz_layout.addWidget(self.quiz_input)
        
        # Feedback display label
        self.quiz_feedback_lbl = QLabel("")
        self.quiz_feedback_lbl.setWordWrap(True)
        self.quiz_feedback_lbl.setStyleSheet("font-size: 12px; font-weight: bold; padding: 4px; background: transparent;")
        quiz_layout.addWidget(self.quiz_feedback_lbl)
        
        # Action buttons
        quiz_buttons = QHBoxLayout()
        quiz_buttons.setSpacing(12)
        quiz_buttons.addStretch()
        
        self.quiz_quit_btn = QPushButton("Quit Quiz")
        self.quiz_quit_btn.setFixedHeight(34)
        self.quiz_quit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.quiz_quit_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-weight: bold; font-size: 11px; padding: 0 15px;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        self.quiz_quit_btn.clicked.connect(self._quit_quiz)
        quiz_buttons.addWidget(self.quiz_quit_btn)
        
        self.quiz_submit_btn = QPushButton("Submit Answer")
        self.quiz_submit_btn.setFixedHeight(34)
        self.quiz_submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.quiz_submit_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_GREEN}; color: #0b0d12; border: none; border-radius: 6px; font-weight: bold; font-size: 11px; padding: 0 20px;
            }}
            QPushButton:hover {{ background: #3fa38d; }}
        """)
        self.quiz_submit_btn.clicked.connect(self._submit_quiz_answer)
        quiz_buttons.addWidget(self.quiz_submit_btn)
        
        self.quiz_next_btn = QPushButton("Next Question →")
        self.quiz_next_btn.setFixedHeight(34)
        self.quiz_next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.quiz_next_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_BLUE}; color: #ffffff; border: none; border-radius: 6px; font-weight: bold; font-size: 11px; padding: 0 20px;
            }}
            QPushButton:hover {{ background: #4893ff; }}
        """)
        self.quiz_next_btn.clicked.connect(self._next_quiz_question)
        self.quiz_next_btn.hide()
        quiz_buttons.addWidget(self.quiz_next_btn)
        
        quiz_layout.addLayout(quiz_buttons)
        self.workspace_stack.addWidget(self.quiz_widget)

        # 4. Quiz Results Page
        self.results_widget = QWidget()
        results_layout = QVBoxLayout(self.results_widget)
        results_layout.setContentsMargins(30, 30, 30, 30)
        results_layout.setSpacing(15)
        results_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.results_score_badge = QLabel("")
        self.results_score_badge.setFixedSize(72, 72)
        self.results_score_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_score_badge.setStyleSheet(f"background: #1e3a31; color: {ACCENT_GREEN}; border-radius: 36px; font-weight: bold; font-size: 20px;")
        results_layout.addWidget(self.results_score_badge, 0, Qt.AlignmentFlag.AlignCenter)
        
        self.results_title = QLabel("Quiz Complete!")
        self.results_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold; margin-top: 10px; background: transparent;")
        self.results_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        results_layout.addWidget(self.results_title)
        
        self.results_desc = QLabel("")
        self.results_desc.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; margin-top: 5px; background: transparent;")
        self.results_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        results_layout.addWidget(self.results_desc)
        
        results_buttons = QHBoxLayout()
        results_buttons.setSpacing(12)
        results_buttons.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        retry_btn = QPushButton("Retry Quiz")
        retry_btn.setFixedHeight(34)
        retry_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        retry_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-weight: bold; font-size: 11px; padding: 0 20px;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        retry_btn.clicked.connect(self._retry_quiz)
        results_buttons.addWidget(retry_btn)
        
        back_to_lesson_btn = QPushButton("Review Material")
        back_to_lesson_btn.setFixedHeight(34)
        back_to_lesson_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_to_lesson_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_GREEN}; color: #0b0d12; border: none; border-radius: 6px; font-weight: bold; font-size: 11px; padding: 0 20px;
            }}
            QPushButton:hover {{ background: #3fa38d; }}
        """)
        back_to_lesson_btn.clicked.connect(self._back_to_lesson)
        results_buttons.addWidget(back_to_lesson_btn)
        
        results_layout.addLayout(results_buttons)
        self.workspace_stack.addWidget(self.results_widget)

        right_layout.addWidget(self.workspace_stack, 1)
        layout.addWidget(main_cols, 1)
        self._update_progress()

    def _populate_lessons(self):
        self.lessons_list.clear()
        lessons = LearningCurriculum.get_all_lessons()
        completed_set = learning_tracker.completed_lessons
        
        for lesson in lessons:
            item = QListWidgetItem()
            item.setSizeHint(QSize(200, 56))
            self.lessons_list.addItem(item)
            
            is_completed = lesson.id in completed_set
            card = QWidget()
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(15, 8, 15, 8)
            card_layout.setSpacing(15)
            
            badge = QLabel(f"{lesson.id:02d}")
            badge.setFixedSize(28, 28)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if is_completed:
                badge.setStyleSheet(f"background: #15332b; color: {ACCENT_GREEN}; border-radius: 14px; font-weight: bold; font-size: 11px;")
            else:
                badge.setStyleSheet("background: #1c2331; color: #8b92b6; border-radius: 14px; font-weight: bold; font-size: 11px;")
            card_layout.addWidget(badge)
            
            text_layout = QVBoxLayout()
            text_layout.setSpacing(2)
            
            title_lbl = QLabel(lesson.title)
            title_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: bold; background:transparent;")
            
            desc_lbl = QLabel(lesson.description)
            desc_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; background:transparent;")
            
            text_layout.addWidget(title_lbl)
            text_layout.addWidget(desc_lbl)
            card_layout.addLayout(text_layout, 1)
            
            status_lbl = QLabel("Completed" if is_completed else "Available")
            status_lbl.setStyleSheet(f"color: {ACCENT_GREEN if is_completed else '#8b92b6'}; font-size: 11px; font-weight: bold; background:transparent;")
            card_layout.addWidget(status_lbl)
            
            self.lessons_list.setItemWidget(item, card)

    def _on_lesson_selected(self):
        row = self.lessons_list.currentRow()
        if row < 0:
            return
        lesson = LearningCurriculum.get_lesson(row + 1)
        if not lesson:
            return
        self.active_lesson = lesson
        self.lesson_title_lbl.setText(f"Lesson {lesson.id}: {lesson.title}")
        
        chars_text = ", ".join([f"'{k}' = {v}" for k, v in lesson.braille_chars.items()])
        study_guide = (
            f"Description:\n{lesson.description}\n\n"
            f"Braille Characters Introduced:\n{chars_text}\n\n"
            f"Practice Directions:\n"
            f"Review the mappings above. Once you feel comfortable, click the button below to start the practice quiz!"
        )
        self.lesson_text.setText(study_guide)
        self.workspace_stack.setCurrentIndex(1)

    def _mark_lesson_complete_action(self):
        if self.active_lesson:
            learning_tracker.mark_lesson_complete(self.active_lesson.id)
            self._update_progress()
            self._populate_lessons()
            self._start_quiz()

    def _start_quiz(self):
        if not self.active_lesson:
            return
        self.current_quiz = BrailleQuiz(self.active_lesson, num_questions=5)
        self.workspace_stack.setCurrentIndex(2)
        self._show_question()

    def _show_question(self):
        if not self.current_quiz:
            return
        q = self.current_quiz.get_current_question()
        if not q:
            return
            
        self.quiz_header_lbl.setText(f"QUESTION {self.current_quiz.current_question + 1} OF {len(self.current_quiz.questions)}")
        self.quiz_question_lbl.setText(q['question'])
        self.quiz_input.clear()
        self.quiz_input.setFocus()
        self.quiz_feedback_lbl.setText("")
        self.quiz_feedback_lbl.setStyleSheet("color: transparent;")
        self.quiz_submit_btn.show()
        self.quiz_next_btn.hide()

    def _submit_quiz_answer(self):
        if not self.current_quiz or self.quiz_submit_btn.isHidden():
            return
        ans = self.quiz_input.text().strip()
        if not ans:
            return
            
        q = self.current_quiz.get_current_question()
        is_correct = self.current_quiz.check_answer(ans)
        
        if is_correct:
            self.quiz_feedback_lbl.setText("Correct Answer! 🎉")
            self.quiz_feedback_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-weight: bold; font-size: 13px;")
        else:
            self.quiz_feedback_lbl.setText(f"Wrong answer. The correct translation was: '{q['correct_answer']}'")
            self.quiz_feedback_lbl.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 13px;")
            
        self.quiz_submit_btn.hide()
        self.quiz_next_btn.show()
        self.quiz_next_btn.setFocus()

    def _next_quiz_question(self):
        if not self.current_quiz:
            return
        if self.current_quiz.is_complete():
            results = self.current_quiz.get_results()
            
            learning_tracker.record_quiz_score(self.active_lesson.id, results['score_percent'])
            self._update_progress()
            
            self.results_score_badge.setText(f"{int(results['score_percent'])}%")
            if results['passed']:
                self.results_title.setText("Practice Quiz Passed! 🎉")
                self.results_desc.setText(f"Fantastic! You got {results['correct_answers']} out of {results['total_questions']} correct.")
                self.results_score_badge.setStyleSheet(f"background: #15332b; color: {ACCENT_GREEN}; border-radius: 36px; font-weight: bold; font-size: 20px; text-align: center; line-height: 72px;")
            else:
                self.results_title.setText("Practice Quiz Failed")
                self.results_desc.setText(f"You got {results['correct_answers']} out of {results['total_questions']} correct. Review the lesson and try again.")
                self.results_score_badge.setStyleSheet("background: #3a1e1e; color: #ff6b6b; border-radius: 36px; font-weight: bold; font-size: 20px; text-align: center; line-height: 72px;")
                
            self.workspace_stack.setCurrentIndex(3)
        else:
            self._show_question()

    def _quit_quiz(self):
        self.current_quiz = None
        self.workspace_stack.setCurrentIndex(1)

    def _retry_quiz(self):
        self._start_quiz()

    def _back_to_lesson(self):
        self.workspace_stack.setCurrentIndex(1)

    def _update_progress(self):
        progress = learning_tracker.get_progress()
        self.progress_bar.setValue(int(progress['completion_percent']))
        self.stats_lbl.setText(f"{progress['lessons_completed']}/{progress['total_lessons']} Lessons Completed")


class HistoryPage(QWidget):
    """History & Favorites management."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_tab = "history"  # "history" or "favorites"
        self.current_items = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # ── TITLE & SUBTITLE ─────────────────────────────────
        title = QLabel("History & Favorites")
        title.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:20px; font-weight:bold;")
        layout.addWidget(title)

        # ── MAIN SPLIT CONTAINER ────────────────────────────
        main_cols = QWidget()
        cols_layout = QHBoxLayout(main_cols)
        cols_layout.setContentsMargins(0, 0, 0, 0)
        cols_layout.setSpacing(25)
        layout.addWidget(main_cols, 1)

        # ── LEFT PANEL: Navigation & List ────────────────────
        left_col = QWidget()
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        # Toggle buttons
        toggle_widget = QWidget()
        toggle_lay = QHBoxLayout(toggle_widget)
        toggle_lay.setContentsMargins(0, 0, 0, 0)
        toggle_lay.setSpacing(8)

        self.btn_history = QPushButton("📜 History")
        self.btn_history.setCheckable(True)
        self.btn_history.setChecked(True)
        self.btn_history.setFixedHeight(36)
        self.btn_history.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.btn_favorites = QPushButton("⭐ Favorites")
        self.btn_favorites.setCheckable(True)
        self.btn_favorites.setChecked(False)
        self.btn_favorites.setFixedHeight(36)
        self.btn_favorites.setCursor(Qt.CursorShape.PointingHandCursor)

        # Connect toggles
        self.btn_history.clicked.connect(self._show_history_tab)
        self.btn_favorites.clicked.connect(self._show_favorites_tab)

        toggle_lay.addWidget(self.btn_history, 1)
        toggle_lay.addWidget(self.btn_favorites, 1)
        left_layout.addWidget(toggle_widget)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search items...")
        self.search_input.setFixedHeight(36)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #141b25;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {ACCENT_GREEN};
            }}
        """)
        self.search_input.textChanged.connect(self._populate_list)
        left_layout.addWidget(self.search_input)

        # List Widget
        self.item_list = QListWidget()
        self.item_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.item_list.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
            }}
            QListWidget::item {{
                background: {CARD_BG};
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                margin-bottom: 8px;
            }}
            QListWidget::item:selected {{
                background: #111520;
                border-color: {ACCENT_GREEN};
            }}
        """)
        self.item_list.currentRowChanged.connect(self._on_item_selected)
        left_layout.addWidget(self.item_list, 1)

        # Bottom clear history button
        self.clear_btn = QPushButton("🗑️ Clear All History")
        self.clear_btn.setFixedHeight(34)
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: #2a1b1b; color: #ff6b6b; border: 1px solid #4a2b2b; border-radius: 6px; font-weight: bold; font-size: 11px;
            }}
            QPushButton:hover {{ background: #4a2b2b; }}
        """)
        self.clear_btn.clicked.connect(self._clear_all_history)
        left_layout.addWidget(self.clear_btn)

        cols_layout.addWidget(left_col, 2)

        # ── RIGHT PANEL: Details Inspector ──────────────────
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)

        self.inspector_stack = QStackedWidget()
        self.inspector_stack.setStyleSheet(f"""
            QStackedWidget {{
                background: #141b25;
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
            }}
        """)

        # 1. Placeholder widget
        placeholder_widget = QWidget()
        ph_layout = QVBoxLayout(placeholder_widget)
        ph_layout.setContentsMargins(30, 40, 30, 40)
        ph_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        ph_icon = QLabel("🔍")
        ph_icon.setStyleSheet("font-size: 48px; margin-bottom: 10px; background: transparent;")
        ph_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ph_layout.addWidget(ph_icon)
        
        ph_title = QLabel("Select an Item")
        ph_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold; background: transparent;")
        ph_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ph_layout.addWidget(ph_title)
        
        ph_desc = QLabel("Choose any conversion history or favorite on the left to inspect, copy, or reload.")
        ph_desc.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; line-height: 1.4; background: transparent;")
        ph_desc.setWordWrap(True)
        ph_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ph_layout.addWidget(ph_desc)
        
        self.inspector_stack.addWidget(placeholder_widget)

        # 2. Detail widget
        self.detail_widget = QWidget()
        detail_layout = QVBoxLayout(self.detail_widget)
        detail_layout.setContentsMargins(25, 25, 25, 25)
        detail_layout.setSpacing(15)

        # Metadata Header Card
        self.meta_card = QFrame()
        self.meta_card.setStyleSheet("background: #0c0f14; border: 1px solid #1c2331; border-radius: 6px; padding: 12px;")
        meta_lay = QVBoxLayout(self.meta_card)
        meta_lay.setSpacing(6)
        
        self.meta_title = QLabel("")
        self.meta_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 14px; font-weight: bold; background: transparent;")
        meta_lay.addWidget(self.meta_title)
        
        self.meta_sub = QLabel("")
        self.meta_sub.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; background: transparent;")
        meta_lay.addWidget(self.meta_sub)
        
        detail_layout.addWidget(self.meta_card)

        # Scrollable input & output grid
        io_split = QSplitter(Qt.Orientation.Vertical)
        
        # Input view
        in_container = QWidget()
        in_lay = QVBoxLayout(in_container)
        in_lay.setContentsMargins(0, 0, 0, 0)
        in_lay.setSpacing(5)
        in_lbl = QLabel("INPUT SOURCE")
        in_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px; background: transparent;")
        in_lay.addWidget(in_lbl)
        self.detail_input = QTextEdit()
        self.detail_input.setReadOnly(True)
        self.detail_input.setStyleSheet(f"background: #0c0f14; border: 1px solid {BORDER_COL}; border-radius: 6px; padding: 8px; font-size: 12px;")
        in_lay.addWidget(self.detail_input)
        io_split.addWidget(in_container)

        # Output view
        out_container = QWidget()
        out_lay = QVBoxLayout(out_container)
        out_lay.setContentsMargins(0, 0, 0, 0)
        out_lay.setSpacing(5)
        out_lbl = QLabel("TRANSLATED OUTPUT")
        out_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px; background: transparent;")
        out_lay.addWidget(out_lbl)
        self.detail_output = QTextEdit()
        self.detail_output.setReadOnly(True)
        self.detail_output.setStyleSheet(f"background: #0c0f14; border: 1px solid {BORDER_COL}; border-radius: 6px; padding: 8px; font-size: 12px;")
        out_lay.addWidget(self.detail_output)
        io_split.addWidget(out_container)
        
        io_split.setStretchFactor(0, 1)
        io_split.setStretchFactor(1, 1)
        detail_layout.addWidget(io_split, 1)

        # Action button row
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self.btn_load = QPushButton("⇄  Reload")
        self.btn_load.setFixedHeight(36)
        self.btn_load.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_load.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_GREEN}; color: #0b0d12; border: none; border-radius: 6px; font-weight: bold; font-size: 11px; padding: 0 15px;
            }}
            QPushButton:hover {{ background: #3fa38d; }}
        """)
        self.btn_load.clicked.connect(self._reload_item)
        action_row.addWidget(self.btn_load)

        self.btn_copy_in = QPushButton("📋 Copy Input")
        self.btn_copy_in.setFixedHeight(36)
        self.btn_copy_in.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_in.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-size: 11px; padding: 0 12px;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        self.btn_copy_in.clicked.connect(self._copy_input_text)
        action_row.addWidget(self.btn_copy_in)

        self.btn_copy_out = QPushButton("📋 Copy Braille")
        self.btn_copy_out.setFixedHeight(36)
        self.btn_copy_out.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_out.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-size: 11px; padding: 0 12px;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        self.btn_copy_out.clicked.connect(self._copy_output_text)
        action_row.addWidget(self.btn_copy_out)

        self.btn_favorite = QPushButton("⭐ Favorite")
        self.btn_favorite.setFixedHeight(36)
        self.btn_favorite.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_favorite.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-size: 11px; padding: 0 12px;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        self.btn_favorite.clicked.connect(self._favorite_item_toggle)
        action_row.addWidget(self.btn_favorite)

        self.btn_delete = QPushButton("🗑️ Delete")
        self.btn_delete.setFixedHeight(36)
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.setStyleSheet(f"""
            QPushButton {{
                background: #2a1b1b; color: #ff6b6b; border: 1px solid #4a2b2b; border-radius: 6px; font-weight: bold; font-size: 11px; padding: 0 15px;
            }}
            QPushButton:hover {{ background: #4a2b2b; }}
        """)
        self.btn_delete.clicked.connect(self._delete_item)
        action_row.addWidget(self.btn_delete)

        detail_layout.addLayout(action_row)
        self.inspector_stack.addWidget(self.detail_widget)

        right_layout.addWidget(self.inspector_stack, 1)
        cols_layout.addWidget(right_col, 3)

        self._style_tabs()
        self._populate_list()

    def _style_tabs(self):
        active_style = f"background: {ACCENT_GREEN}; color: #0b0d12; border: none; border-radius: 6px; font-weight: bold;"
        inactive_style = f"background: #141b25; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px;"
        
        if self.active_tab == "history":
            self.btn_history.setStyleSheet(active_style)
            self.btn_favorites.setStyleSheet(inactive_style)
            self.clear_btn.show()
        else:
            self.btn_history.setStyleSheet(inactive_style)
            self.btn_favorites.setStyleSheet(active_style)
            self.clear_btn.hide()

    def _show_history_tab(self, checked=False):
        self.active_tab = "history"
        self.btn_history.setChecked(True)
        self.btn_favorites.setChecked(False)
        self._style_tabs()
        self.search_input.clear()
        self._populate_list()

    def _show_favorites_tab(self, checked=False):
        self.active_tab = "favorites"
        self.btn_history.setChecked(False)
        self.btn_favorites.setChecked(True)
        self._style_tabs()
        self.search_input.clear()
        self._populate_list()

    def _populate_list(self, text=""):
        self.item_list.clear()
        self.current_items = []
        query = self.search_input.text().strip()
        
        if self.active_tab == "history":
            if query:
                history = history_manager.search_history(query)
            else:
                history = history_manager.get_history(limit=50)
                
            self.current_items = history
            for record in history:
                item = QListWidgetItem()
                item.setSizeHint(QSize(200, 58))
                self.item_list.addItem(item)
                
                # Card widget
                card = QWidget()
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(12, 8, 12, 8)
                card_layout.setSpacing(3)
                
                title_text = record.input_text.strip().replace('\n', ' ')
                if len(title_text) > 28:
                    title_text = title_text[:25] + "..."
                if not title_text:
                    title_text = "(Empty Input)"
                    
                title_lbl = QLabel(title_text)
                title_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: bold; background: transparent;")
                
                dir_label = "Text → Braille" if record.conversion_type == 'text_to_braille' else "Braille → Text"
                sub_text = f"{record.timestamp[:10]} • {record.language} • {dir_label}"
                sub_lbl = QLabel(sub_text)
                sub_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; background: transparent;")
                
                card_layout.addWidget(title_lbl)
                card_layout.addWidget(sub_lbl)
                self.item_list.setItemWidget(item, card)
        else:
            if query:
                favorites = favorites_manager.search_favorites(query)
            else:
                favorites = favorites_manager.get_all_favorites()
                
            self.current_items = favorites
            for name, data in favorites:
                item = QListWidgetItem()
                item.setSizeHint(QSize(200, 58))
                self.item_list.addItem(item)
                
                # Card widget
                card = QWidget()
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(12, 8, 12, 8)
                card_layout.setSpacing(3)
                
                title_lbl = QLabel(f"⭐  {name}")
                title_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: bold; background: transparent;")
                
                desc_text = data['text'].strip().replace('\n', ' ')
                if len(desc_text) > 32:
                    desc_text = desc_text[:29] + "..."
                sub_lbl = QLabel(desc_text)
                sub_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; background: transparent;")
                
                card_layout.addWidget(title_lbl)
                card_layout.addWidget(sub_lbl)
                self.item_list.setItemWidget(item, card)

        # Force clear inspector selection
        self.inspector_stack.setCurrentIndex(0)

    def _on_item_selected(self, row):
        if row < 0 or row >= len(self.current_items):
            self.inspector_stack.setCurrentIndex(0)
            return

        item = self.current_items[row]
        self.inspector_stack.setCurrentIndex(1)
        
        if self.active_tab == "history":
            # item is ConversionRecord
            self.meta_title.setText(f"History Record")
            dir_label = "Text → Braille" if item.conversion_type == 'text_to_braille' else "Braille → Text"
            self.meta_sub.setText(f"Timestamp: {item.timestamp.replace('T', ' ')[:19]}  •  Language: {item.language}  •  Type: {dir_label}")
            
            self.detail_input.setPlainText(item.input_text)
            self.detail_output.setPlainText(item.output_text)
            
            # Check if already favorited
            is_fav = False
            for name, fav_data in favorites_manager.get_all_favorites():
                if fav_data['text'] == item.input_text and fav_data['braille'] == item.output_text:
                    is_fav = True
                    break
            
            if is_fav:
                self.btn_favorite.setText("⭐ Favorited")
                self.btn_favorite.setStyleSheet(f"background: {ACCENT_GREEN}; color: #0b0d12; border: none; border-radius: 6px; font-size: 11px; padding: 0 12px;")
            else:
                self.btn_favorite.setText("⭐ Add Favorite")
                self.btn_favorite.setStyleSheet(f"background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-size: 11px; padding: 0 12px;")
                
            self.btn_favorite.setEnabled(True)
        else:
            # item is (name, data) tuple
            name, data = item
            self.meta_title.setText(f"Favorite: {name}")
            self.meta_sub.setText(f"Created: {data.get('created', '').replace('T', ' ')[:19]}")
            
            self.detail_input.setPlainText(data['text'])
            self.detail_output.setPlainText(data['braille'])
            
            self.btn_favorite.setText("⭐ Favorited")
            self.btn_favorite.setStyleSheet(f"background: {ACCENT_GREEN}; color: #0b0d12; border: none; border-radius: 6px; font-size: 11px; padding: 0 12px;")
            self.btn_favorite.setEnabled(False) # Already a favorite!

    def _reload_item(self, checked=False):
        row = self.item_list.currentRow()
        if row < 0 or row >= len(self.current_items):
            return
        
        item = self.current_items[row]
        if self.active_tab == "history":
            text = item.input_text
            mode_type = item.conversion_type
        else:
            name, data = item
            text = data['text']
            mode_type = 'text_to_braille' # default for saved favs
            
        main_win = self.window()
        if hasattr(main_win, 'converter_page'):
            main_win.converter_page.input_text.setPlainText(text)
            
            # Match the mode
            mode_combo = main_win.converter_page.mode_combo
            if mode_type == 'text_to_braille':
                for i in range(mode_combo.count()):
                    if '→ Braille' in mode_combo.itemText(i):
                        mode_combo.setCurrentIndex(i)
                        break
            else:
                for i in range(mode_combo.count()):
                    if '→ Text' in mode_combo.itemText(i):
                        mode_combo.setCurrentIndex(i)
                        break
                        
            # Switch to converter page which is index 1
            main_win.nav.setCurrentRow(1)
            announce("Loaded selection into Converter")

    def _copy_input_text(self, checked=False):
        text = self.detail_input.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            announce("Input text copied to clipboard")

    def _copy_output_text(self, checked=False):
        text = self.detail_output.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            announce("Braille output copied to clipboard")

    def _delete_item(self, checked=False):
        row = self.item_list.currentRow()
        if row < 0 or row >= len(self.current_items):
            return
            
        item = self.current_items[row]
        if self.active_tab == "history":
            record = item
            try:
                idx = history_manager.history.index(record)
                history_manager.delete_history_item(idx)
                announce("Deleted history record")
            except ValueError:
                pass
        else:
            name, data = item
            favorites_manager.delete_favorite(name)
            announce("Deleted favorite record")
            
        self._populate_list()

    def _favorite_item_toggle(self, checked=False):
        row = self.item_list.currentRow()
        if row < 0 or row >= len(self.current_items):
            return
            
        item = self.current_items[row]
        if self.active_tab == "history":
            is_fav = False
            fav_name = ""
            for name, fav_data in favorites_manager.get_all_favorites():
                if fav_data['text'] == item.input_text and fav_data['braille'] == item.output_text:
                    is_fav = True
                    fav_name = name
                    break
                    
            if is_fav:
                favorites_manager.delete_favorite(fav_name)
                announce("Removed from favorites")
            else:
                from PyQt6.QtWidgets import QInputDialog
                name, ok = QInputDialog.getText(self, "Add Favorite", "Enter a name for this favorite:")
                if ok and name.strip():
                    favorites_manager.add_favorite(name.strip(), item.input_text, item.output_text)
                    announce("Added to favorites")
            
            self._populate_list()
            self.item_list.setCurrentRow(row)

    def _clear_all_history(self, checked=False):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, 'Clear History', 'Are you sure you want to clear all conversion history?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            history_manager.clear_history()
            announce("Conversion history cleared")
            self._populate_list()


class AuditPage(QWidget):
    """Accessibility Audit Tool."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # ── TITLE & SUBTITLE ─────────────────────────────────
        title = QLabel("Accessibility Audit")
        title.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:20px; font-weight:bold;")
        layout.addWidget(title)

        subtitle = QLabel("Analyze your text and translation for accessibility compliance, formatting, and translation quality in real-time.")
        subtitle.setStyleSheet(f"color:{TEXT_MUTED}; font-size:12px;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # ── STATS CARDS ROW ──────────────────────────────────
        stats_row = QHBoxLayout()
        stats_row.setSpacing(20)

        # Card 1: Score
        self.score_card = QFrame()
        self.score_card.setStyleSheet(f"background: {CARD_BG}; border: 1px solid {BORDER_COL}; border-radius: 8px; padding: 15px;")
        score_layout = QVBoxLayout(self.score_card)
        score_layout.setSpacing(5)
        score_lbl_title = QLabel("ACCESSIBILITY SCORE")
        score_lbl_title.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px; background: transparent;")
        self.score_val = QLabel("100%")
        self.score_val.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 28px; font-weight: bold; background: transparent;")
        score_layout.addWidget(score_lbl_title)
        score_layout.addWidget(self.score_val)
        stats_row.addWidget(self.score_card, 1)

        # Card 2: Breakdown
        self.breakdown_card = QFrame()
        self.breakdown_card.setStyleSheet(f"background: {CARD_BG}; border: 1px solid {BORDER_COL}; border-radius: 8px; padding: 15px;")
        breakdown_layout = QVBoxLayout(self.breakdown_card)
        breakdown_layout.setSpacing(5)
        breakdown_lbl_title = QLabel("ISSUE BREAKDOWN")
        breakdown_lbl_title.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px; background: transparent;")
        self.breakdown_val = QLabel("0 Errors • 0 Warnings • 0 Info")
        self.breakdown_val.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 14px; font-weight: bold; background: transparent; padding-top: 10px;")
        breakdown_layout.addWidget(breakdown_lbl_title)
        breakdown_layout.addWidget(self.breakdown_val)
        stats_row.addWidget(self.breakdown_card, 1)

        # Card 3: Status
        self.status_card = QFrame()
        self.status_card.setStyleSheet(f"background: {CARD_BG}; border: 1px solid {BORDER_COL}; border-radius: 8px; padding: 15px;")
        status_layout = QVBoxLayout(self.status_card)
        status_layout.setSpacing(5)
        status_lbl_title = QLabel("AUDIT STATUS")
        status_lbl_title.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px; background: transparent;")
        self.status_val = QLabel("✅ Passed")
        self.status_val.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 18px; font-weight: bold; background: transparent; padding-top: 7px;")
        status_layout.addWidget(status_lbl_title)
        status_layout.addWidget(self.status_val)
        stats_row.addWidget(self.status_card, 1)

        layout.addLayout(stats_row)

        # ── MAIN SPLIT VIEW ──────────────────────────────────
        main_split = QSplitter(Qt.Orientation.Horizontal)

        # Left Column: Input Panel
        input_panel = QWidget()
        input_layout = QVBoxLayout(input_panel)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)

        in_lbl = QLabel("TEXT TO AUDIT")
        in_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        input_layout.addWidget(in_lbl)

        self.audit_input = QTextEdit()
        self.audit_input.setPlaceholderText("Type or paste your text here to begin the real-time accessibility audit...")
        self.audit_input.setStyleSheet(f"background: #141b25; border: 1px solid {BORDER_COL}; border-radius: 8px; padding: 12px; font-size: 13px; line-height: 1.4;")
        self.audit_input.textChanged.connect(self._run_live_audit)
        input_layout.addWidget(self.audit_input)

        btn_row = QHBoxLayout()
        self.clear_btn = QPushButton("🗑️  Clear Text")
        self.clear_btn.setFixedHeight(34)
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-size: 11px; padding: 0 15px;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        self.clear_btn.clicked.connect(self._clear_text)
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch()
        input_layout.addLayout(btn_row)

        # Right Column: Issues List Panel
        issues_panel = QWidget()
        issues_layout = QVBoxLayout(issues_panel)
        issues_layout.setContentsMargins(0, 0, 0, 0)
        issues_layout.setSpacing(10)

        out_lbl = QLabel("AUDIT LOG & SUGGESTIONS")
        out_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        issues_layout.addWidget(out_lbl)

        self.issues_list = QListWidget()
        self.issues_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.issues_list.setStyleSheet(f"""
            QListWidget {{
                background: #141b25;
                border: 1px solid {BORDER_COL};
                border-radius: 8px;
                padding: 10px;
            }}
            QListWidget::item {{
                background: transparent;
                margin-bottom: 8px;
            }}
        """)
        issues_layout.addWidget(self.issues_list)

        main_split.addWidget(input_panel)
        main_split.addWidget(issues_panel)
        main_split.setStretchFactor(0, 1)
        main_split.setStretchFactor(1, 1)
        layout.addWidget(main_split, 1)

        # Run initial run to set empty states
        self._run_live_audit()

    def _run_live_audit(self):
        text = self.audit_input.toPlainText().strip()
        self.issues_list.clear()

        if not text:
            # Empty state
            self.score_val.setText("100%")
            self.score_val.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 28px; font-weight: bold; background: transparent;")
            self.breakdown_val.setText("0 Errors • 0 Warnings • 0 Info")
            self.status_val.setText("✅ Passed")
            self.status_val.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 18px; font-weight: bold; background: transparent; padding-top: 7px;")
            
            # Placeholder list item
            item = QListWidgetItem()
            item.setSizeHint(QSize(200, 60))
            self.issues_list.addItem(item)
            
            card = QWidget()
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(15, 10, 15, 10)
            
            lbl = QLabel("Enter text on the left to run an accessibility audit.")
            lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; font-style: italic; background: transparent;")
            card_layout.addWidget(lbl)
            
            self.issues_list.setItemWidget(item, card)
            return

        # Run the audit using model
        result = auditor.audit_text(text)
        
        # 1. Update Score Card
        score = result['accessibility_score']
        self.score_val.setText(f"{score}%")
        if score >= 90:
            score_color = ACCENT_GREEN
        elif score >= 70:
            score_color = "#E5C07B" # Orange-yellow
        else:
            score_color = "#ff6b6b" # Red
        self.score_val.setStyleSheet(f"color: {score_color}; font-size: 28px; font-weight: bold; background: transparent;")

        # 2. Update Breakdown
        errors = result['by_severity'].get('ERROR', 0)
        warnings = result['by_severity'].get('WARNING', 0)
        info = result['by_severity'].get('INFO', 0)
        self.breakdown_val.setText(f"{errors} Errors • {warnings} Warnings • {info} Info")

        # 3. Update Status
        status = result['status']
        self.status_val.setText(status)
        if "Failed" in status or errors > 0:
            status_color = "#ff6b6b"
        elif "Warnings" in status or warnings > 0:
            status_color = "#E5C07B"
        else:
            status_color = ACCENT_GREEN
        self.status_val.setStyleSheet(f"color: {status_color}; font-size: 18px; font-weight: bold; background: transparent; padding-top: 7px;")

        # 4. Populate Issues List
        issues = result.get('issues', [])
        if not issues:
            # Green success card
            item = QListWidgetItem()
            item.setSizeHint(QSize(200, 70))
            self.issues_list.addItem(item)
            
            card = QFrame()
            card.setStyleSheet("background: #0f2c25; border: 1px solid #165243; border-radius: 6px; padding: 12px;")
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(10, 8, 10, 8)
            
            success_icon = QLabel("✓")
            success_icon.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 20px; font-weight: bold; background: transparent; max-width: 20px;")
            
            success_text_layout = QVBoxLayout()
            success_text_layout.setSpacing(3)
            success_title = QLabel("All checks passed!")
            success_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: bold; background: transparent;")
            success_desc = QLabel("Your text is 100% compliant with Braille standards and contains no readability blockers.")
            success_desc.setStyleSheet(f"color: #a1d2c6; font-size: 11px; background: transparent;")
            success_text_layout.addWidget(success_title)
            success_text_layout.addWidget(success_desc)
            
            card_layout.addWidget(success_icon)
            card_layout.addLayout(success_text_layout)
            
            self.issues_list.setItemWidget(item, card)
        else:
            for issue in issues:
                item = QListWidgetItem()
                item.setSizeHint(QSize(200, 75))
                self.issues_list.addItem(item)
                
                card = QFrame()
                
                # Determine colors based on severity
                if issue.severity.name == "ERROR":
                    border_color = "#ff6b6b"
                    bg_color = "#2a1515"
                    icon = "❌"
                elif issue.severity.name == "WARNING":
                    border_color = "#E5C07B"
                    bg_color = "#282015"
                    icon = "⚠️"
                else:
                    border_color = "#5AA6FF"
                    bg_color = "#15202e"
                    icon = "ℹ️"
                    
                card.setStyleSheet(f"background: {bg_color}; border: 1px solid {border_color}; border-radius: 6px; padding: 10px;")
                
                card_layout = QHBoxLayout(card)
                card_layout.setContentsMargins(10, 8, 10, 8)
                
                status_icon = QLabel(icon)
                status_icon.setStyleSheet("font-size: 16px; background: transparent; max-width: 20px;")
                
                text_lay = QVBoxLayout()
                text_lay.setSpacing(3)
                
                issue_title = QLabel(f"[{issue.category}] {issue.message}")
                issue_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; font-weight: bold; background: transparent;")
                
                issue_desc = QLabel(f"Suggestion: {issue.suggestion}")
                issue_desc.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; background: transparent;")
                
                text_lay.addWidget(issue_title)
                text_lay.addWidget(issue_desc)
                
                card_layout.addWidget(status_icon)
                card_layout.addLayout(text_lay)
                
                self.issues_list.setItemWidget(item, card)

    def _clear_text(self):
        self.audit_input.clear()
        self._run_live_audit()


class SettingsPage(QWidget):
    """Settings & Preferences page."""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        try:
            from settings_manager import settings_manager
            self.settings = settings_manager
        except ImportError:
            self.settings = None
        
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── LEFT SIDEBAR PANEL (FULL HEIGHT) ────────────────────────────
        left_panel = QFrame()
        left_panel.setObjectName("settingsLeftPanel")
        left_panel.setStyleSheet(f"""
            #settingsLeftPanel {{
                background-color: #07090e;
                border-right: 1px solid #141822;
            }}
        """)
        left_panel.setFixedWidth(240)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(6)
        left_layout.setContentsMargins(15, 20, 15, 20)
        
        # Title
        title = QLabel("SETTINGS")
        title.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 11px; font-weight: bold; padding-left: 8px; margin-bottom: 10px;")
        left_layout.addWidget(title)
        
        # Categories with descriptions (only functional sections)
        categories = [
            ("🔊", "Audio", "Speed, Volume, Language"),
            ("⠃", "Braille", "Grade, Language, Format"),
            ("📱", "Behavior", "Auto-save, Auto-convert"),
            ("✨", "Features", "Speech, Audio, OCR, AI"),
            ("♿", "Accessibility", "Screen reader, Keyboard"),
        ]
        
        self.category_buttons = {}
        for icon, name, desc in categories:
            btn = QPushButton(f"{icon}   {name}")
            btn.setMinimumHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(desc)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: #8b92b6;
                    border: none; border-radius: 6px;
                    padding: 8px 12px; text-align: left; font-weight: bold;
                    font-size: 12px;
                }}
                QPushButton:hover {{ background: #111520; color: #e6eef8; }}
            """)
            left_layout.addWidget(btn)
            self.category_buttons[name] = btn
        
        left_layout.addSpacing(15)
        
        # Divider
        divider = QFrame()
        divider.setStyleSheet(f"background-color: {BORDER_COL}; max-height: 1px;")
        left_layout.addWidget(divider)
        
        left_layout.addSpacing(10)
        
        # Settings Info
        info_label = QLabel("Customize app behavior, appearance, and features")
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"color:{TEXT_MUTED}; font-size:10px; line-height:1.4; padding: 0 8px;")
        left_layout.addWidget(info_label)
        
        left_layout.addSpacing(15)
        
        # Quick Actions
        save_btn = QPushButton("Save All")
        save_btn.setObjectName("primary")
        save_btn.setMinimumHeight(38)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_GREEN}; color: #1a1b26; border: none; border-radius: 6px; font-weight: bold; font-size: 12px;
            }}
            QPushButton:hover {{ background: #00e896; }}
        """)
        save_btn.clicked.connect(self._save_settings)
        left_layout.addWidget(save_btn)
        
        reset_btn = QPushButton("Reset")
        reset_btn.setMinimumHeight(38)
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e2230; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COL}; border-radius: 6px; font-weight: bold; font-size: 12px;
            }}
            QPushButton:hover {{ background: {BORDER_COL}; }}
        """)
        reset_btn.clicked.connect(self._reset_defaults)
        left_layout.addWidget(reset_btn)
        
        left_layout.addSpacing(10)
        
        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(f"color:{TEXT_MUTED}; font-size:10px; text-align:center; padding:8px;")
        left_layout.addWidget(self.status_label)
        
        layout.addWidget(left_panel)
        
        # ── RIGHT CONTENT AREA (scrollable) ──────────────────
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(40, 20, 40, 20)
        content_layout.setSpacing(25)

        # Wrap right content in a scroll area so we can scroll to sections
        self.content_scroll = QScrollArea()
        self.content_scroll.setWidgetResizable(True)
        self.content_scroll.setStyleSheet("background: transparent; border: none;")
        
        # Title
        content_title = QLabel("Settings & Preferences")
        content_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: bold;")
        content_layout.addWidget(content_title)
        
        if not self.settings:
            status = QLabel("⚠️ Settings manager not available")
            status.setStyleSheet(f"color:#ff6b6b;")
            content_layout.addWidget(status)
            content_layout.addStretch()
            layout.addWidget(self.content_scroll, 1)
            return

        self._section_frames = {}

        # ── AUDIO SETTINGS ──────────────────────────
        audio_section = self._create_settings_section("Audio Settings")
        audio_inner = audio_section.rows_layout
        
        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(50, 300)
        self.speed_spin.setValue(self.settings.get_setting("audio_speed", 150))
        self.speed_spin.setSuffix(" wpm")
        
        row1 = self._create_setting_row("Speech Speed", "Speech playback speed (words per minute)", self.speed_spin)
        audio_inner.addWidget(row1)

        self.volume_spin = QSpinBox()
        self.volume_spin.setRange(0, 100)
        self.volume_spin.setValue(int(self.settings.get_setting("audio_volume", 1.0) * 100))
        self.volume_spin.setSuffix("%")
        
        row2 = self._create_setting_row("Audio Volume", "Master volume for audio exports and text-to-speech feedback", self.volume_spin)
        audio_inner.addWidget(row2)

        self.audio_lang_combo = QComboBox()
        self.audio_lang_combo.addItems(["English", "Hindi", "Marathi", "Tamil", "Telugu", "Kannada", "French", "Spanish"])
        self.audio_lang_combo.setCurrentText(self.settings.get_setting("audio_language", "English"))
        
        row3 = self._create_setting_row("Audio Language", "Select language for audio speech outputs", self.audio_lang_combo)
        audio_inner.addWidget(row3)

        content_layout.addWidget(audio_section)
        self._section_frames['Audio'] = audio_section

        # ── BRAILLE SETTINGS ────────────────────────
        braille_section = self._create_settings_section("Braille Settings")
        braille_inner = braille_section.rows_layout

        self.grade_spin = QSpinBox()
        self.grade_spin.setRange(1, 3)
        self.grade_spin.setValue(self.settings.get_setting("braille_grade", 2))
        
        row4 = self._create_setting_row("Braille Grade", "Standard Braille Grade level (1 to 3)", self.grade_spin)
        braille_inner.addWidget(row4)

        self.braille_lang_combo = QComboBox()
        self.braille_lang_combo.addItems(["English", "Hindi", "Marathi", "Tamil", "Telugu", "Kannada", "French", "Spanish"])
        self.braille_lang_combo.setCurrentText(self.settings.get_setting("braille_language", "English"))
        
        row5 = self._create_setting_row("Braille Language", "Default language dictionary for Braille translations", self.braille_lang_combo)
        braille_inner.addWidget(row5)

        self.embosser_combo = QComboBox()
        self.embosser_combo.addItems(["Standard (80 chars)", "Compact (40 chars)"])
        chars = self.settings.get_setting("embosser_chars_per_line", 80)
        if chars == 40:
            self.embosser_combo.setCurrentText("Compact (40 chars)")
        else:
            self.embosser_combo.setCurrentText("Standard (80 chars)")
            
        row6 = self._create_setting_row("Embosser Format", "Embosser layout character limit per line", self.embosser_combo)
        braille_inner.addWidget(row6)

        content_layout.addWidget(braille_section)
        self._section_frames['Braille'] = braille_section

        # ── APP BEHAVIOR ────────────────────────────
        behavior_section = self._create_settings_section("App Behavior")
        behavior_inner = behavior_section.rows_layout

        self.autosave_check = QCheckBox()
        self.autosave_check.setChecked(self.settings.get_setting("auto_save_history", True))
        row7 = self._create_setting_row("Auto-save History", "Automatically save successful translations to history log", self.autosave_check)
        behavior_inner.addWidget(row7)

        self.autoconvert_check = QCheckBox()
        self.autoconvert_check.setChecked(self.settings.get_setting("auto_convert", True))
        row8 = self._create_setting_row("Auto-convert Text", "Translate text in real-time as you type", self.autoconvert_check)
        behavior_inner.addWidget(row8)

        content_layout.addWidget(behavior_section)
        self._section_frames['Behavior'] = behavior_section

        # ── FEATURES ────────────────────────────────
        features_section = self._create_settings_section("App Features")
        features_inner = features_section.rows_layout

        self.sr_check = QCheckBox()
        self.sr_check.setChecked(self.settings.get_setting("enable_speech_recognition", True))
        row9 = self._create_setting_row("Speech Recognition", "Enable voice-to-text translations on Speech page", self.sr_check)
        features_inner.addWidget(row9)

        self.export_check = QCheckBox()
        self.export_check.setChecked(self.settings.get_setting("enable_audio_export", True))
        row10 = self._create_setting_row("Audio Export", "Enable saving translated Braille as audio speech files", self.export_check)
        features_inner.addWidget(row10)

        self.ocr_check = QCheckBox()
        self.ocr_check.setChecked(self.settings.get_setting("enable_ocr", True))
        row11 = self._create_setting_row("OCR Scanner", "Enable image scanning and OCR reading features", self.ocr_check)
        features_inner.addWidget(row11)

        self.learning_check = QCheckBox()
        self.learning_check.setChecked(self.settings.get_setting("enable_learning", True))
        self.learning_check.toggled.connect(self._toggle_learning)
        row12 = self._create_setting_row("Learning Module", "Enable interactive courses in the navigation sidebar", self.learning_check)
        features_inner.addWidget(row12)

        content_layout.addWidget(features_section)
        self._section_frames['Features'] = features_section

        # ── ACCESSIBILITY ──────────────────────────
        accessibility_section = self._create_settings_section("Accessibility")
        accessibility_inner = accessibility_section.rows_layout

        self.sr_enabled_check = QCheckBox()
        self.sr_enabled_check.setChecked(self.settings.get_setting("screen_reader_enabled", True))
        row13 = self._create_setting_row("Screen Reader Mode", "Optimize interface and announce changes for screen readers", self.sr_enabled_check)
        accessibility_inner.addWidget(row13)

        self.keyboard_check = QCheckBox()
        self.keyboard_check.setChecked(self.settings.get_setting("keyboard_only_mode", False))
        row14 = self._create_setting_row("Keyboard-Only Mode", "Configure keyboard navigation shortcuts and focus highlights", self.keyboard_check)
        accessibility_inner.addWidget(row14)

        self.contrast_check = QCheckBox()
        self.contrast_check.setChecked(self.settings.get_setting("high_contrast", False))
        row15 = self._create_setting_row("High Contrast", "Use high-contrast color scheme for improved readability", self.contrast_check)
        accessibility_inner.addWidget(row15)

        content_layout.addWidget(accessibility_section)
        self._section_frames['Accessibility'] = accessibility_section

        content_layout.addStretch()
        self.content_scroll.setWidget(content_frame)
        layout.addWidget(self.content_scroll, 1)

        # Connect category buttons
        for name, btn in self.category_buttons.items():
            btn.clicked.connect(lambda _, n=name: self._on_category_clicked(n))

    def _on_category_clicked(self, name: str):
        """Scroll to the given settings section and highlight the category."""
        key = name
        frame = self._section_frames.get(key)
        if not frame:
            return
        try:
            self.content_scroll.ensureWidgetVisible(frame)
        except Exception:
            y = frame.pos().y()
            self.content_scroll.verticalScrollBar().setValue(y)
        for n, btn in self.category_buttons.items():
            if n == name:
                btn.setProperty('selected', True)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #1a2230;
                        color: {ACCENT_GREEN};
                        border-left: 3px solid {ACCENT_GREEN};
                        border-radius: 0px 6px 6px 0px;
                        padding: 8px 12px;
                        text-align: left;
                        font-weight: bold;
                        font-size: 12px;
                    }}
                """)
            else:
                btn.setProperty('selected', False)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent; color: #8b92b6;
                        border: none; border-radius: 6px;
                        padding: 8px 12px; text-align: left; font-weight: bold;
                        font-size: 12px;
                    }}
                    QPushButton:hover {{ background: #111520; color: #e6eef8; }}
                """)

    def _create_settings_section(self, section_title):
        """Creates a clean section with a bold header title and divider line."""
        section_widget = QWidget()
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 15, 0, 10)
        section_layout.setSpacing(10)
        
        # Title Label
        title_lbl = QLabel(section_title)
        title_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 14px; font-weight: bold; text-transform: uppercase;")
        section_layout.addWidget(title_lbl)
        
        # Underline divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        divider.setStyleSheet(f"background-color: {BORDER_COL}; max-height: 1px;")
        section_layout.addWidget(divider)
        
        # Container for rows
        rows_container = QWidget()
        rows_layout = QVBoxLayout(rows_container)
        rows_layout.setContentsMargins(10, 0, 10, 0)
        rows_layout.setSpacing(15)
        section_layout.addWidget(rows_container)
        
        section_widget.rows_layout = rows_layout
        return section_widget

    def _create_setting_row(self, title_text, desc_text, control_widget):
        """Creates a clean, flat settings row with title/description on left, control on right."""
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 10, 0, 10)
        
        # Left side: Text labels
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_lbl = QLabel(title_text)
        title_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: bold;")
        
        desc_lbl = QLabel(desc_text)
        desc_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        desc_lbl.setWordWrap(True)
        
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(desc_lbl)
        
        row_layout.addLayout(text_layout, 1)
        row_layout.addSpacing(20)
        
        # Right side: Control widget
        control_widget.setStyleSheet(f"""
            QSpinBox, QComboBox, QLineEdit {{
                background-color: #141b25;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                border-radius: 6px;
                padding: 6px 12px;
                min-width: 150px;
                font-size: 12px;
            }}
            QSpinBox:hover, QComboBox:hover, QLineEdit:hover {{
                border-color: {ACCENT_GREEN};
            }}
            QSpinBox::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 18px;
                border-left: 1px solid {BORDER_COL};
                border-top-right-radius: 6px;
                background: #1c2331;
            }}
            QSpinBox::up-button:hover {{
                background: #242c3e;
            }}
            QSpinBox::up-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 4px solid {ACCENT_GREEN};
                width: 0;
                height: 0;
            }}
            QSpinBox::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 18px;
                border-left: 1px solid {BORDER_COL};
                border-bottom-right-radius: 6px;
                background: #1c2331;
            }}
            QSpinBox::down-button:hover {{
                background: #242c3e;
            }}
            QSpinBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {ACCENT_GREEN};
                width: 0;
                height: 0;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {BORDER_COL};
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                background: #1c2331;
            }}
            QComboBox::drop-down:hover {{
                background: #242c3e;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {ACCENT_GREEN};
                width: 0;
                height: 0;
            }}
            QComboBox QAbstractItemView {{
                background-color: #141b25;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COL};
                selection-background-color: #1a2230;
                selection-color: {ACCENT_GREEN};
                outline: none;
            }}
            QCheckBox {{
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid {BORDER_COL};
                border-radius: 4px;
                background-color: #141b25;
            }}
            QCheckBox::indicator:checked {{
                background-color: {ACCENT_GREEN};
                border-color: {ACCENT_GREEN};
            }}
        """)
        row_layout.addWidget(control_widget, 0, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        
        return row_widget

    def _save_settings(self):
        """Save all settings."""
        self.settings.set_setting("audio_speed", self.speed_spin.value())
        self.settings.set_setting("audio_volume", self.volume_spin.value() / 100.0)
        self.settings.set_setting("audio_language", self.audio_lang_combo.currentText())
        self.settings.set_setting("braille_grade", self.grade_spin.value())
        self.settings.set_setting("braille_language", self.braille_lang_combo.currentText())
        self.settings.set_setting("auto_save_history", self.autosave_check.isChecked())
        self.settings.set_setting("auto_convert", self.autoconvert_check.isChecked())
        self.settings.set_setting("enable_speech_recognition", self.sr_check.isChecked())
        self.settings.set_setting("enable_audio_export", self.export_check.isChecked())
        self.settings.set_setting("enable_ocr", self.ocr_check.isChecked())

        # Learning setting persisted
        self.settings.set_setting("enable_learning", self.learning_check.isChecked())
        self.settings.set_setting("screen_reader_enabled", self.sr_enabled_check.isChecked())
        self.settings.set_setting("keyboard_only_mode", self.keyboard_check.isChecked())
        self.settings.set_setting("high_contrast", self.contrast_check.isChecked())
        
        self.status_label.setText("✅ Settings saved successfully!")
        self.status_label.setStyleSheet(f"color:{ACCENT_GREEN};")

    def _toggle_learning(self, enabled: bool):
        """Show or hide the Learning page dynamically."""
        # Persist setting
        try:
            self.settings.set_setting("enable_learning", enabled)
        except:
            pass

        # Attempt to update main window navigation and pages
        main_win = self.window()
        if not main_win or not hasattr(main_win, 'nav') or not hasattr(main_win, 'pages'):
            return

        nav: QListWidget = main_win.nav
        pages: QStackedWidget = main_win.pages

        learning_label = "Learning"
        history_label = "History"

        # Find existing nav item index for Learning
        found_idx = None
        for i in range(nav.count()):
            if learning_label in nav.item(i).text():
                found_idx = i
                break

        if not enabled and found_idx is not None:
            nav.takeItem(found_idx)
        elif enabled and found_idx is None:
            # insert before History if possible
            hist_idx = None
            for i in range(nav.count()):
                if history_label in nav.item(i).text():
                    hist_idx = i
                    break
            item = QListWidgetItem("📖   Learning Center")
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            item.setToolTip("Interactive Course")
            item.setSizeHint(QSize(200, 42))
            insert_at = hist_idx if hist_idx is not None else nav.count()
            nav.insertItem(insert_at, item)

        # Pages: add/remove LearningPage instance
        hist_page = getattr(main_win, 'history_page', None)
        hist_idx = pages.indexOf(hist_page) if hist_page else -1

        learning_page_obj = getattr(main_win, 'learning_page', None)
        lp_idx = pages.indexOf(learning_page_obj) if learning_page_obj else -1

        if not enabled and lp_idx != -1:
            widget = pages.widget(lp_idx)
            pages.removeWidget(widget)
            try:
                widget.deleteLater()
            except:
                pass
            if hasattr(main_win, 'learning_page'):
                delattr(main_win, 'learning_page')
        elif enabled and lp_idx == -1:
            new_lp = LearningPage()
            insert_pos = hist_idx if hist_idx != -1 else pages.count()
            try:
                pages.insertWidget(insert_pos, new_lp)
            except Exception:
                # fallback to addWidget
                pages.addWidget(new_lp)
            main_win.learning_page = new_lp

        # If the removed page was currently visible, switch to Home
        if pages.currentIndex() >= pages.count():
            pages.setCurrentIndex(0)

        toast_message = "Learning enabled — reloading view" if enabled else "Learning disabled — reloading view"
        if hasattr(main_win, "show_toast"):
            main_win.show_toast(toast_message)
        else:
            self.status_label.setText(toast_message)

    def _reset_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(self, "Confirm", "Reset all settings to defaults?")
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.reset_to_defaults()
            self.status_label.setText("✅ Settings reset to defaults!")
            self.status_label.setStyleSheet(f"color:{ACCENT_GREEN};")





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⠃ LipiSync — The Intelligent Braille Workspace")
        self.setMinimumSize(1400, 750)
        self.setStyleSheet(STYLESHEET)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 20, 0, 10)
        sb_layout.setSpacing(0)

        # App Title
        app_title = QLabel("LipiSync")
        app_title.setStyleSheet(f"font-size:18px; font-weight:bold; color:{ACCENT_GREEN}; padding: 0 20px 2px 20px;")
        sb_layout.addWidget(app_title)

        # Tagline
        tagline = QLabel("Intelligent Braille Workspace")
        tagline.setStyleSheet(f"font-size:9px; color:{TEXT_MUTED}; padding: 0 20px 10px 20px;")
        sb_layout.addWidget(tagline)



        # Section Header: Navigation
        nav_header = QLabel("NAVIGATION")
        nav_header.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {TEXT_MUTED}; padding: 5px 20px;")
        sb_layout.addWidget(nav_header)

        self.nav = QListWidget()
        self.nav.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.nav.setSpacing(2)  # Tight spacing between items
        
        # Respect feature flags from settings
        learning_enabled = settings_manager.get_setting("enable_learning", True)

        items = [
            ("⌂   Home",                  "Welcome"),
            ("⇄   Converter",             "Text ↔ Braille"),
            ("📷   OCR Reader",            "Image → Braille"),
            ("🔊   Vocalizer Studio",       "Text-to-Speech"),
            ("🎙   Voice Translation",     "Voice → Braille"),
            ("🎓   Braille Grades",        "Advanced Grades"),
            ("∑   Math Notation",         "Math Notation"),
            ("📄   Document Reader",       "PDF Processing"),
        ]

        if learning_enabled:
            items.append(("📖   Learning Center", "Interactive Course"))

        items += [
            ("⏳   History",               "History & Favorites"),
            ("📋   Activity Logs",         "Activity Logs"),
            ("✓   Accessibility Audit",   "Accessibility Check"),
            ("⚙   Settings",              "User Preferences"),
            ("ℹ   About Product",         "Project Info"),
        ]
        
        for label, sub in items:
            item = QListWidgetItem(label)
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            item.setToolTip(sub)
            item.setSizeHint(QSize(200, 42))  # Taller items to fill space with padding
            self.nav.addItem(item)

        self.nav.setCurrentRow(0)
        self.nav.currentRowChanged.connect(self._switch_page)
        sb_layout.addWidget(self.nav, 1)  # Make nav expand and fill available space
        
        # Bottom Divider and Version
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        divider.setStyleSheet(f"background-color: {BORDER_COL}; max-height: 1px; margin: 10px 15px;")
        sb_layout.addWidget(divider)
        
        ver_lbl = QLabel("LipiSync v2.0")
        ver_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; padding: 5px 20px 15px 20px;")
        sb_layout.addWidget(ver_lbl)
        
        root.addWidget(sidebar)

        # ── Pages ────────────────────────────────────────────
        self.pages = QStackedWidget()
        
        # Add all pages in order
        # Instantiate pages (learning is optional)
        self.home_page = HomePage()
        self.converter_page = ConverterPage()
        self.ocr_page = OCRPage()
        self.audio_page = AudioPage()
        self.speech_page = SpeechPage()
        self.grades_page = AdvancedGradesPage()
        self.math_page = MathPage()
        self.document_page = DocumentPage()
        self.history_page = HistoryPage()
        self.logs_page = LogsPage()
        self.audit_page = AuditPage()
        self.settings_page = SettingsPage()

        self.about_page = AboutPage()

        # Build ordered list of pages matching the nav items
        pages_to_add = [
            self.home_page,
            self.converter_page,
            self.ocr_page,
            self.audio_page,
            self.speech_page,
            self.grades_page,
            self.math_page,
            self.document_page,
        ]

        if settings_manager.get_setting("enable_learning", True):
            self.learning_page = LearningPage()
            pages_to_add.append(self.learning_page)

        pages_to_add += [
            self.history_page,
            self.logs_page,
            self.audit_page,
            self.settings_page,
            self.about_page,
        ]

        for p in pages_to_add:
            self.pages.addWidget(p)

        self.page_names = [
            "Home",
            "Converter",
            "OCR",
            "Audio",
            "Speech",
            "Grades",
            "Math",
            "Documents",
        ]

        if settings_manager.get_setting("enable_learning", True):
            self.page_names.append("Learning")

        self.page_names += [
            "History",
            "Logs",
            "Audit",
            "Settings",
            "About",
        ]
        
        root.addWidget(self.pages)
        
        # Auto-record conversions in history
        self.converter_page.input_text.textChanged.connect(self._on_conversion)

    def _switch_page(self, idx):
        previous_widget = self.pages.currentWidget()
        self.pages.setCurrentIndex(idx)
        current_widget = self.pages.currentWidget()

        if previous_widget and hasattr(previous_widget, 'deactivate_auto_refresh'):
            try:
                previous_widget.deactivate_auto_refresh()
            except Exception:
                pass

        if current_widget and hasattr(current_widget, 'activate_auto_refresh'):
            try:
                current_widget.activate_auto_refresh()
            except Exception:
                pass

        if idx < len(self.page_names):
            announce(f"Switched to {self.page_names[idx]} page")
    
    def navigate_to_page(self, page_name):
        for idx in range(self.nav.count()):
            item = self.nav.item(idx)
            text = item.text().lower()
            if page_name in text:
                self.nav.setCurrentRow(idx)
                break

    def _on_conversion(self):
        """Auto-record conversions in history."""
        try:
            input_text = self.converter_page.input_text.toPlainText()
            output_text = self.converter_page.output_text.toPlainText()
            if input_text and output_text and len(input_text) > 2:
                lang = self.converter_page.lang_combo.currentText()
                mode = self.converter_page.mode_combo.currentText()
                conv_type = 'text_to_braille' if '→ Braille' in mode else 'braille_to_text'
                history_manager.add_conversion(input_text, output_text, lang, conv_type)
        except:
            pass
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for accessibility."""
        key = event.key()
        modifiers = event.modifiers()
        
        # Alt+1 to Alt+0: Switch pages
        if modifiers == Qt.KeyboardModifier.AltModifier:
            page_map = {
                Qt.Key.Key_1: 0,   # Home
                Qt.Key.Key_2: 1,   # Converter
                Qt.Key.Key_3: 2,   # OCR
                Qt.Key.Key_4: 3,   # Audio
                Qt.Key.Key_5: 4,   # Speech
                Qt.Key.Key_6: 5,   # Grades
                Qt.Key.Key_7: 6,   # Math
                Qt.Key.Key_8: 7,   # Documents
                Qt.Key.Key_9: 8,   # Learning/History
                Qt.Key.Key_0: 9,   # History/Logs
            }
            if key in page_map:
                self.nav.setCurrentRow(page_map[key])
                return
        
        # Ctrl+Shift+S: Speak output
        if key == Qt.Key.Key_S and modifiers == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            try:
                output = self.converter_page.output_text.toPlainText()
                if output:
                    audio_engine.speak(output, language='en')
                    announce("Speaking braille output")
            except:
                pass
            return
        
        # Ctrl+3: Copy output
        if key == Qt.Key.Key_3 and modifiers == Qt.KeyboardModifier.ControlModifier:
            try:
                from clipboard_manager import clipboard_manager
                text = self.converter_page.output_text.toPlainText()
                if text:
                    clipboard_manager.set_clipboard_text(text)
                    announce("Output copied to clipboard")
            except:
                pass
            return
        
        # F1: Show help
        if key == Qt.Key.Key_F1:
            help_text = BlindUserHelper.get_quick_start_guide()
            shortcuts = KeyboardShortcutManager.get_shortcut_help()
            QMessageBox.information(
                self,
                "Help & Keyboard Shortcuts",
                help_text + "\n\n" + shortcuts
            )
            announce("Help window opened")
            return
        
        # Ctrl+Shift+H: Show history
        if key == Qt.Key.Key_H and modifiers == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            for i in range(self.nav.count()):
                if "History" in self.nav.item(i).text():
                    self.nav.setCurrentRow(i)
                    break
            return
        
        # Ctrl+Shift+F: Add to favorites
        if key == Qt.Key.Key_F and modifiers == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            try:
                input_text = self.converter_page.input_text.toPlainText()
                output_text = self.converter_page.output_text.toPlainText()
                if input_text and output_text:
                    # Simple naming
                    name = f"Conversion {len(favorites_manager.favorites) + 1}"
                    favorites_manager.add_favorite(
                        name, input_text, output_text, 
                        tags=['quick_save']
                    )
                    announce(f"Added to favorites: {name}")
            except:
                pass
            return
        
        super().keyPressEvent(event)
    


    def show_toast(self, message: str, duration_ms: int = 2200):
        """Show a lightweight in-app confirmation toast."""
        toast = QLabel(message, self)
        toast.setObjectName("toast")
        toast.setStyleSheet(
            f"""
            QLabel#toast {{
                background: rgba(36, 37, 58, 235);
                color: {TEXT_PRIMARY};
                border: 1px solid {ACCENT_GREEN};
                border-radius: 10px;
                padding: 10px 14px;
                font-weight: bold;
            }}
            """
        )
        toast.adjustSize()

        x = max(20, self.width() - toast.width() - 28)
        toast.move(x, 20)
        toast.show()
        toast.raise_()
        QTimer.singleShot(duration_ms, toast.deleteLater)