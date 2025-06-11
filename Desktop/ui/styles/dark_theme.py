DARK_THEME = """
    QMainWindow {
        background-color: #262626;
    }
    
    QGroupBox {
        font-weight: bold;
        border-radius: 8px;
        margin-top: 1ex;
        padding-top: 15px;
        color: #ffffff;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 15px;
        padding: 0 8px 0 8px;
        color: #60a5fa;
    }
    
    QPushButton {
        background: #2563eb;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 11px;
    }
    
    QPushButton:hover {
        background: #3b82f6;
    }
    
    QPushButton:pressed {
        background: #1e40af;
    }
    
    QPushButton:disabled {
        background-color: #6b7280;
        color: #9ca3af;
    }
    
    QLineEdit {
        background-color: #4b5563;
        color: #f9fafb;
        border: 2px solid #6b7280;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 11px;
    }
    
    QLineEdit:focus {
        border-color: #3b82f6;
    }
    
    QTextEdit {
        background-color: #374151;
        color: #e5e7eb;
        border: 2px solid #4b5563;
        border-radius: 6px;
        padding: 8px;
        font-family: 'Consolas', monospace;
    }
    
    QListWidget {
        background-color: #374151;
        color: #e5e7eb;
        border: 2px solid #4b5563;
        border-radius: 6px;
        alternate-background-color: #4b5563;
        outline: none;
    }
    
    QListWidget::item {
        padding: 8px;
        border-bottom: 1px solid #4b5563;
    }
    
    QListWidget::item:selected {
        background-color: #3b82f6;
        color: white;
    }
    
    QListWidget::item:hover {
        background-color: #4b5563;
    }
    
    QLabel {
        color: #e5e7eb;
    }
    
    QScrollArea {
        border: none;
        background-color: #262626;
    }
    
    QScrollBar:vertical {
        background-color: #374151;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #6b7280;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #9ca3af;
    }
"""

GROUP_STYLE = """
    QGroupBox {
        background: #232323;
        border: 1px solid #3f3f3f;
    }
"""

CONNECTION_GROUP_STYLE = GROUP_STYLE + """
    QGroupBox QPushButton {
        background: #2563eb;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 11px;
    }
    
    QGroupBox QPushButton:hover {
        background: #3b82f6;
    }
    
    QGroupBox QPushButton:disabled {
        background-color: #6b7280;
        color: #9ca3af;
    }
"""