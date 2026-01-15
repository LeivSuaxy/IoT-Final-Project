
# Modern Color Palette
COLORS = {
    'background': '#121212',
    'surface': '#1E1E1E',
    'surface_hover': '#252525',
    'border': '#333333',
    'primary': '#8b5cf6', # Violet
    'primary_hover': '#7c3aed',
    'success': '#10b981', # Emerald
    'error': '#ef4444',   # Red
    'warning': '#f59e0b', # Amber
    'text_primary': '#e0e0e0',
    'text_secondary': '#a0a0a0',
    'text_tertiary': '#666666'
}

DARK_THEME = """
    QMainWindow {
        background-color: #121212;
    }
    QWidget {
        font-family: 'Segoe UI', system-ui, sans-serif;
        color: #e0e0e0;
    }
    
    QGroupBox {
        border: 1px solid #333333;
        border-radius: 8px;
        margin-top: 24px;
        padding-top: 15px;
        background-color: #1E1E1E;
        font-weight: 600;
        font-size: 13px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 12px;
        padding: 0 4px;
        color: #8b5cf6; 
        background-color: #1E1E1E;
    }
    
    QScrollArea {
        border: none;
        background-color: transparent;
    }
    
    QScrollBar:vertical {
        background-color: #1E1E1E;
        width: 8px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical {
        background-color: #4b5563;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #6b7280;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QTextEdit {
        background-color: #1a1a1a;
        border: 1px solid #333333;
        color: #d4d4d4;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 12px;
        border-radius: 6px;
        padding: 8px;
    }

    QLabel {
        color: #e0e0e0;
    }

    QMenuBar {
        background-color: #121212;
        border-bottom: 1px solid #333333;
    }
    QMenuBar::item {
        background: transparent;
        padding: 8px 12px;
        color: #a0a0a0;
    }
    QMenuBar::item:selected {
        background: #1E1E1E;
        color: #ffffff;
    }
    
    QMenu {
        background-color: #1E1E1E;
        border: 1px solid #333333;
        border-radius: 6px;
        padding: 4px;
    }
    
    QMenu::item {
        padding: 6px 24px 6px 12px;
        color: #e0e0e0;
        border-radius: 4px;
    }
    
    QMenu::item:selected {
        background-color: #8b5cf6;
        color: #ffffff;
    }
"""

CARD_STYLE = """
    QFrame#Card {
        background-color: #1E1E1E;
        border: 1px solid #333333;
        border-radius: 12px;
    }
    QLabel {
        border: none;
        background: transparent;
    }
"""

STATUS_CHIP_STYLE = {
    'default': """
        QFrame { background: #262626; border: 1px solid #404040; border-radius: 14px; }
        QLabel { color: #a0a0a0; font-weight: 600; font-size: 11px; }
    """,
    'success': """
        QFrame { background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 14px; }
        QLabel { color: #10b981; font-weight: 600; font-size: 11px; }
    """,
    'error': """
        QFrame { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 14px; }
        QLabel { color: #ef4444; font-weight: 600; font-size: 11px; }
    """,
    'warning': """
        QFrame { background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 14px; }
        QLabel { color: #f59e0b; font-weight: 600; font-size: 11px; }
    """,
    'info': """
        QFrame { background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 14px; }
        QLabel { color: #3b82f6; font-weight: 600; font-size: 11px; }
    """
}

# --- Connection Panel Styles ---
CONNECTION_PANEL_STYLE = """
    QGroupBox {
        background: #1E1E1E;
        border: 1px solid #333333;
        border-radius: 10px;
        font-weight: 600;
        margin-top: 24px;
        padding-top: 15px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        padding: 3px 8px;
        color: #8b5cf6;
        background-color: #1E1E1E;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
    }
    QLineEdit {
        background: #252525;
        color: #ffffff;
        border: 1px solid #404040;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
    }
    QLineEdit:focus {
        border: 1px solid #8b5cf6;
        background: #2d2d2d;
    }
    QLineEdit::placeholder {
        color: #666666;
    }
"""

PRIMARY_BTN_STYLE = """
    QPushButton {
        background: #3b82f6;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
        font-family: 'Segoe UI';
        font-size: 12px;
    }
    QPushButton:hover {
        background: #2563eb;
    }
    QPushButton:pressed {
        background: #1d4ed8;
    }
    QPushButton:disabled {
        background: #333333;
        color: #666666;
    }
"""

ARDUINO_BTN_READY_STYLE = """
    QPushButton {
        background: #ef4444;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 6px 12px;
        font-weight: 600;
        font-family: 'Segoe UI';
        font-size: 12px;
    }
    QPushButton:hover {
        background: #dc2626;
    }
    QPushButton:pressed {
        background: #b91c1c;
    }
"""

ARDUINO_BTN_IDLE_STYLE = """
    QPushButton {
        background: #10b981;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 6px 12px;
        font-weight: 600;
        font-family: 'Segoe UI';
        font-size: 12px;
    }
    QPushButton:hover {
        background: #059669;
    }
    QPushButton:pressed {
        background: #047857;
    }
    QPushButton:disabled {
        background: #333333;
        color: #666666;
    }
"""

# --- Auth Dialog Styles (Preserved) ---
AUTH_DIALOG_STYLE = """
    QDialog {
        background-color: #121212;
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    QLabel {
        color: #e0e0e0;
    }
    QLabel#Title {
        font-size: 26px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 5px;
    }
    QLabel#Subtitle {
        font-size: 14px;
        color: #a0a0a0;
        margin-bottom: 20px;
    }
"""

AUTH_INPUT_STYLE = """
    QLineEdit {
        background-color: #1e1e1e;
        color: #ffffff;
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 14px;
        selection-background-color: #6d28d9;
    }
    QLineEdit:focus {
        border: 1px solid #8b5cf6;
        background-color: #252525;
    }
    QLineEdit::placeholder {
        color: #666666;
    }
"""

AUTH_PRIMARY_BTN_STYLE = """
    QPushButton {
        background: qlineargradient(
            x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 #7c3aed,
            stop: 1 #6d28d9
        );
        color: white;
        border: none;
        border-radius: 8px;
        padding: 14px;
        font-size: 15px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    QPushButton:hover {
        background: qlineargradient(
            x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 #8b5cf6,
            stop: 1 #7c3aed
        );
    }
    QPushButton:pressed {
        background: #5b21b6;
        padding: 15px 14px 13px 14px;
    }
    QPushButton:disabled {
        background: #333333;
        color: #666666;
    }
"""

AUTH_TAB_STYLE = """
    QTabWidget::pane {
        border: 1px solid #333333;
        background: #181818;
        border-radius: 8px;
        margin-top: -1px; 
    }
    QTabBar::tab {
        background: #121212;
        color: #808080;
        padding: 12px 24px;
        border-bottom: 2px solid transparent;
        font-weight: 600;
        font-size: 14px;
    }
    QTabBar::tab:selected {
        color: #ffffff;
        border-bottom: 2px solid #8b5cf6;
    }
    QTabBar::tab:hover:!selected {
        color: #b0b0b0;
    }
"""
