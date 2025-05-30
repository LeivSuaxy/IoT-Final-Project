from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PyQt6.QtGui import QFont
from datetime import datetime
from utils.constants import INFO_ICONS


class PersonCard(QFrame):
    """Tarjeta que muestra información de una persona"""
    
    def __init__(self, card_id="", name="", info=None, parent=None):
        super().__init__(parent)
        self.info = info or {}
        self._setup_style()
        self._setup_ui(card_id, name)
    
    def _setup_style(self):
        """Configura el estilo de la tarjeta"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            PersonCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2d3748, stop:1 #4a5568);
                border: 2px solid #4299e1;
                border-radius: 15px;
                margin: 10px;
                padding: 15px;
            }
        """)
    
    def _setup_ui(self, card_id, name):
        """Configura la interfaz de la tarjeta"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        layout.addLayout(self._create_header(card_id))

        layout.addLayout(self._create_name_section(name))

        if self.info:
            layout.addLayout(self._create_info_section())
    
    def _create_header(self, card_id):
        """Crea el header con ID y timestamp"""
        header_layout = QHBoxLayout()
        
        card_icon = QLabel("🏷️")
        card_icon.setFont(QFont("Arial", 20))
        
        card_label = QLabel(f"ID: {card_id}")
        card_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        card_label.setStyleSheet("color: #4299e1;")
        
        timestamp_label = QLabel(datetime.now().strftime("%H:%M:%S"))
        timestamp_label.setFont(QFont("Arial", 10))
        timestamp_label.setStyleSheet("color: #a0aec0;")
        
        header_layout.addWidget(card_icon)
        header_layout.addWidget(card_label)
        header_layout.addStretch()
        header_layout.addWidget(timestamp_label)
        
        return header_layout
    
    def _create_name_section(self, name):
        """Crea la sección del nombre"""
        name_layout = QHBoxLayout()
        
        person_icon = QLabel("👤")
        person_icon.setFont(QFont("Arial", 18))
        
        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #e2e8f0;")
        
        name_layout.addWidget(person_icon)
        name_layout.addWidget(name_label)
        name_layout.addStretch()
        
        return name_layout
    
    def _create_info_section(self):
        """Crea la sección de información adicional"""
        info_layout = QGridLayout()
        
        for row, (key, value) in enumerate(self.info.items()):
            icon = QLabel(INFO_ICONS.get(key.lower(), INFO_ICONS['default']))
            icon.setFont(QFont("Arial", 12))
            
            key_label = QLabel(f"{key.replace('_', ' ').title()}:")
            key_label.setFont(QFont("Arial", 11))
            key_label.setStyleSheet("color: #cbd5e0;")
            
            value_label = QLabel(str(value))
            value_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            value_label.setStyleSheet("color: #e2e8f0;")
            
            info_layout.addWidget(icon, row, 0)
            info_layout.addWidget(key_label, row, 1)
            info_layout.addWidget(value_label, row, 2)
        
        return info_layout