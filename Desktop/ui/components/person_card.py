from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QWidget
from PyQt6.QtGui import QFont, QPainter, QColor, QPen
from PyQt6.QtCore import Qt
from datetime import datetime
from utils.constants import INFO_ICONS


class PersonCard(QFrame):
    """Tarjeta modernizada que muestra información de una persona"""
    
    def __init__(self, card_id="", name="", info=None, parent=None):
        super().__init__(parent)
        self.card_id = card_id
        self.name = name
        self.info = info or {}
        self._setup_style()
        self._setup_ui()
    
    def _setup_style(self):
        """Configura el estilo modernizado de la tarjeta"""
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setMinimumHeight(250)
        self.setStyleSheet("""
            PersonCard {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #1e293b,
                    stop: 0.5 #334155,
                    stop: 1 #475569
                );
                border: 2px solid qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #3b82f6,
                    stop: 1 #6366f1
                );
                border-radius: 20px;
                margin: 10px;
            }
        """)
    
    def _setup_ui(self):
        """Configura la interfaz modernizada de la tarjeta"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 20, 25, 20)

        # Header con diseño mejorado
        header_widget = self._create_modern_header()
        main_layout.addWidget(header_widget)

        # Separador visual
        separator = self._create_separator()
        main_layout.addWidget(separator)

        # Sección de nombre
        name_widget = self._create_modern_name_section()
        main_layout.addWidget(name_widget)

        # Información adicional si existe
        if self.info:
            info_widget = self._create_modern_info_section()
            main_layout.addWidget(info_widget)
        
        main_layout.addStretch()
    
    def _create_modern_header(self):
        """Crea el header modernizado"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: rgba(59, 130, 246, 0.1);
                border: 1px solid #3b82f6;
                border-radius: 12px;
                padding: 5px;
            }
        """)
        
        layout = QHBoxLayout(header_frame)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Icono de tarjeta con mejor diseño
        card_icon_container = QFrame()
        card_icon_container.setFixedSize(50, 50)
        card_icon_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #3b82f6,
                    stop: 1 #6366f1
                );
                border-radius: 25px;
            }
        """)
        
        icon_layout = QVBoxLayout(card_icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        card_icon = QLabel("🏷️")
        card_icon.setFont(QFont("Segoe UI", 20))
        card_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(card_icon)
        
        # Información de la tarjeta
        info_section = QVBoxLayout()
        
        card_label = QLabel(f"Tarjeta RFID")
        card_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        card_label.setStyleSheet("color: #94a3b8;")
        
        card_id_label = QLabel(f"ID: {self.card_id}")
        card_id_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        card_id_label.setStyleSheet("color: #e2e8f0;")
        
        info_section.addWidget(card_label)
        info_section.addWidget(card_id_label)
        
        # Timestamp
        timestamp_container = QVBoxLayout()
        timestamp_container.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        time_label = QLabel("Escaneado")
        time_label.setFont(QFont("Segoe UI", 9))
        time_label.setStyleSheet("color: #94a3b8;")
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        timestamp_label = QLabel(datetime.now().strftime("%H:%M:%S"))
        timestamp_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        timestamp_label.setStyleSheet("color: #60a5fa;")
        timestamp_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        timestamp_container.addWidget(time_label)
        timestamp_container.addWidget(timestamp_label)
        
        layout.addWidget(card_icon_container)
        layout.addLayout(info_section, 2)
        layout.addStretch()
        layout.addLayout(timestamp_container)
        
        return header_frame
    
    def _create_separator(self):
        """Crea un separador visual"""
        separator = QFrame()
        separator.setFixedHeight(2)
        separator.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 transparent,
                    stop: 0.2 #3b82f6,
                    stop: 0.8 #6366f1,
                    stop: 1 transparent
                );
                border: none;
                border-radius: 1px;
            }
        """)
        return separator
    
    def _create_modern_name_section(self):
        """Crea la sección modernizada del nombre"""
        name_frame = QFrame()
        layout = QHBoxLayout(name_frame)
        layout.setContentsMargins(10, 15, 10, 15)
        
        # Avatar placeholder
        avatar = QFrame()
        avatar.setFixedSize(45, 45)
        avatar.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #10b981,
                    stop: 1 #059669
                );
                border-radius: 22px;
            }
        """)
        
        avatar_layout = QVBoxLayout(avatar)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        
        person_icon = QLabel("👤")
        person_icon.setFont(QFont("Segoe UI", 18))
        person_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_layout.addWidget(person_icon)
        
        # Información del usuario
        user_info = QVBoxLayout()
        
        welcome_label = QLabel("Usuario Identificado")
        welcome_label.setFont(QFont("Segoe UI", 10))
        welcome_label.setStyleSheet("color: #94a3b8;")
        
        name_label = QLabel(self.name)
        name_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        name_label.setStyleSheet("""
            color: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #ffffff,
                stop: 1 #e2e8f0
            );
        """)
        
        user_info.addWidget(welcome_label)
        user_info.addWidget(name_label)
        
        layout.addWidget(avatar)
        layout.addLayout(user_info, 1)
        layout.addStretch()
        
        return name_frame
    
    def _create_modern_info_section(self):
        """Crea la sección modernizada de información adicional"""
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: rgba(16, 185, 129, 0.05);
                border: 1px solid rgba(16, 185, 129, 0.2);
                border-radius: 12px;
                padding: 5px;
            }
        """)
        
        main_layout = QVBoxLayout(info_frame)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Título de la sección
        title_label = QLabel("📊 Información Adicional")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #10b981; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Grid de información
        info_grid = QGridLayout()
        info_grid.setSpacing(10)
        
        for row, (key, value) in enumerate(self.info.items()):
            # Icono
            icon = QLabel(INFO_ICONS.get(key.lower(), INFO_ICONS['default']))
            icon.setFont(QFont("Segoe UI", 14))
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon.setFixedSize(30, 30)
            icon.setStyleSheet("""
                QLabel {
                    background: rgba(16, 185, 129, 0.1);
                    border-radius: 15px;
                    padding: 3px;
                }
            """)
            
            # Clave
            key_label = QLabel(f"{key.replace('_', ' ').title()}:")
            key_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
            key_label.setStyleSheet("color: #cbd5e0;")
            
            # Valor
            value_label = QLabel(str(value))
            value_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            value_label.setStyleSheet("color: #e2e8f0;")
            
            info_grid.addWidget(icon, row, 0)
            info_grid.addWidget(key_label, row, 1)
            info_grid.addWidget(value_label, row, 2)
        
        main_layout.addLayout(info_grid)
        
        return info_frame