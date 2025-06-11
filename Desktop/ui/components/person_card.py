from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QWidget
from PyQt6.QtGui import QFont, QPainter, QColor, QPen
from PyQt6.QtCore import Qt
from datetime import datetime
from utils.constants import INFO_ICONS


class PersonCard(QFrame):
    """Tarjeta para mostrar información de una persona"""
    
    def __init__(self, card_id, name, info):
        super().__init__()
        
        # Convertir todos los parámetros a string para evitar errores
        self.card_id = str(card_id) if card_id is not None else "Unknown"
        self.name = str(name) if name is not None else "Usuario Desconocido"
        self.info = str(info) if info is not None else "Sin información"
        
        self.setMinimumHeight(200)
        self.setMaximumHeight(300)
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Configura la interfaz de la tarjeta"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        # Header con ID
        header_layout = QHBoxLayout()
        
        id_label = QLabel(f"🆔 {self.card_id}")
        id_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        id_label.setStyleSheet("color: #60a5fa;")
        
        timestamp_label = QLabel(datetime.now().strftime("%H:%M:%S"))
        timestamp_label.setFont(QFont("Arial", 10))
        timestamp_label.setStyleSheet("color: #9ca3af;")
        
        header_layout.addWidget(id_label)
        header_layout.addStretch()
        header_layout.addWidget(timestamp_label)
        
        # Nombre
        name_label = QLabel(self.name)
        name_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #ffffff; padding: 5px 0;")
        name_label.setWordWrap(True)
        
        # Información adicional
        info_label = QLabel(self.info)
        info_label.setFont(QFont("Arial", 12))
        info_label.setStyleSheet("color: #d1d5db; padding: 5px 0;")
        info_label.setWordWrap(True)
        
        # Añadir widgets al layout
        layout.addLayout(header_layout)
        layout.addWidget(name_label)
        layout.addWidget(info_label)
        layout.addStretch()
    
    def _apply_styles(self):
        """Aplica los estilos CSS a la tarjeta"""
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #374151,
                    stop: 1 #1f2937
                );
                border: 1px solid #4b5563;
                border-radius: 12px;
                margin: 5px;
            }
        """)