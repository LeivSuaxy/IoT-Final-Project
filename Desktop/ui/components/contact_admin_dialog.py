"""Dialog para usuarios no admin cuando encuentran tarjeta no registrada"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QTextEdit)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt


class ContactAdminDialog(QDialog):
    """Dialog que aparece cuando un usuario no admin encuentra una tarjeta no registrada"""
    
    def __init__(self, rfid_id: str, parent=None):
        super().__init__(parent)
        self.rfid_id = rfid_id
        
        self.setWindowTitle("Tarjeta No Registrada")
        self.setFixedSize(800, 800)
        self.setModal(True)
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Configura la interfaz del dialog"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Icono y título
        header_layout = self._create_header()
        layout.addLayout(header_layout)
        
        # Información de la tarjeta
        card_info_layout = self._create_card_info()
        layout.addLayout(card_info_layout)
        
        # Mensaje de instrucciones
        message_layout = self._create_message()
        layout.addLayout(message_layout)
        
        # Botón de cerrar
        button_layout = self._create_button()
        layout.addLayout(button_layout)
    
    def _create_header(self):
        """Crea el header con icono y título"""
        header_layout = QVBoxLayout()
        
        # Icono de advertencia
        icon_label = QLabel("⚠️")
        icon_label.setFont(QFont("Arial", 48))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("color: #f59e0b; margin-bottom: 10px;")
        
        # Título
        title = QLabel("Tarjeta No Registrada")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #ef4444; margin-bottom: 5px;")
        
        # Subtítulo
        subtitle = QLabel("Esta tarjeta no está en el sistema")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #9ca3af;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        return header_layout
    
    def _create_card_info(self):
        """Crea la información de la tarjeta"""
        card_layout = QVBoxLayout()
        
        # Frame para la información de la tarjeta
        card_frame = QFrame()
        card_frame.setStyleSheet("""
            QFrame {
                background: #374151;
                border: 1px solid #4b5563;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        frame_layout = QVBoxLayout(card_frame)
        
        card_title = QLabel("📋 Detalles de la Tarjeta")
        card_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        card_title.setStyleSheet("color: #60a5fa; margin-bottom: 8px;")
        
        card_id = QLabel(f"🆔 ID: {self.rfid_id}")
        card_id.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        card_id.setStyleSheet("color: #e5e7eb; background: #1f2937; padding: 8px; border-radius: 4px;")
        
        scan_time = QLabel(f"🕒 Escaneada: {self._get_current_time()}")
        scan_time.setFont(QFont("Arial", 10))
        scan_time.setStyleSheet("color: #9ca3af; margin-top: 5px;")
        
        frame_layout.addWidget(card_title)
        frame_layout.addWidget(card_id)
        frame_layout.addWidget(scan_time)
        
        card_layout.addWidget(card_frame)
        
        return card_layout
    
    def _create_message(self):
        """Crea el mensaje de instrucciones"""
        message_layout = QVBoxLayout()
        
        message_title = QLabel("📞 ¿Qué hacer ahora?")
        message_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        message_title.setStyleSheet("color: #60a5fa; margin-bottom: 10px;")
        
        # Lista de instrucciones
        instructions = [
            "1. Contacta a un administrador del sistema",
            "2. Proporciona el ID de la tarjeta mostrado arriba",
            "3. El administrador registrará la tarjeta en el sistema",
            "4. Una vez registrada, podrás usarla normalmente"
        ]
        
        for instruction in instructions:
            instruction_label = QLabel(instruction)
            instruction_label.setFont(QFont("Arial", 11))
            instruction_label.setStyleSheet("""
                color: #e5e7eb; 
                padding: 5px 0; 
                margin-left: 10px;
            """)
            instruction_label.setWordWrap(True)
            message_layout.addWidget(instruction_label)
        
        # Mensaje adicional
        contact_frame = QFrame()
        contact_frame.setStyleSheet("""
            QFrame {
                background: #1e40af;
                border: 1px solid #3b82f6;
                border-radius: 6px;
                padding: 12px;
                margin-top: 10px;
            }
        """)
        
        contact_layout = QVBoxLayout(contact_frame)
        
        contact_title = QLabel("💡 Información Importante")
        contact_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        contact_title.setStyleSheet("color: #93c5fd;")
        
        contact_text = QLabel("Solo los administradores pueden registrar nuevas tarjetas en el sistema por motivos de seguridad.")
        contact_text.setFont(QFont("Arial", 10))
        contact_text.setStyleSheet("color: #dbeafe;")
        contact_text.setWordWrap(True)
        
        contact_layout.addWidget(contact_title)
        contact_layout.addWidget(contact_text)
        
        message_layout.addWidget(message_title)
        for instruction in instructions:
            instruction_label = QLabel(instruction)
            instruction_label.setFont(QFont("Arial", 11))
            instruction_label.setStyleSheet("""
                color: #e5e7eb; 
                padding: 5px 0; 
                margin-left: 10px;
            """)
            instruction_label.setWordWrap(True)
            message_layout.addWidget(instruction_label)
        
        message_layout.addWidget(contact_frame)
        
        return message_layout
    
    def _create_button(self):
        """Crea el botón de cerrar"""
        button_layout = QHBoxLayout()
        
        close_btn = QPushButton("✅ Entendido")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        
        return button_layout
    
    def _get_current_time(self):
        """Obtiene la hora actual formateada"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def _apply_styles(self):
        """Aplica estilos al dialog"""
        self.setStyleSheet("""
            QDialog {
                background: #1f2937;
                color: #e5e7eb;
            }
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: #059669;
            }
            QPushButton:pressed {
                background: #047857;
            }
        """)