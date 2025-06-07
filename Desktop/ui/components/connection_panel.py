from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QGridLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from .status_indicator import StatusIndicator
from utils.constants import DEFAULT_HOST, DEFAULT_PORT


class ConnectionPanel(QGroupBox):
    """Panel modernizado para configurar y controlar la conexión"""
    
    def __init__(self, parent=None):
        super().__init__("🔌 Configuración de Conexión", parent)
        self.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Configura la interfaz del panel en una sola fila compacta"""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 25, 20, 20)
        
        # Host input
        host_container = self._create_compact_input("Host", "127.0.0.1", str(DEFAULT_HOST))
        self.host_input = host_container.findChild(QLineEdit)
        
        # Port input
        port_container = self._create_compact_input("Puerto", "8080", str(DEFAULT_PORT))
        self.port_input = port_container.findChild(QLineEdit)
        
        # Botón de conexión
        button_container, self.connection_btn = self._create_connection_button()
        
        # Estado de conexión (punto + texto)
        status_container = self._create_minimal_status()
        
        # Distribución: Host (40%), Puerto (20%), Botón (25%), Estado (15%)
        main_layout.addWidget(host_container, 2)
        main_layout.addWidget(port_container, 1)
        main_layout.addWidget(button_container)
        main_layout.addWidget(status_container, 1)
    
    def _create_compact_input(self, label_text, placeholder, default_value):
        """Crea un campo de entrada compacto"""
        container = QFrame()
        layout = QVBoxLayout(container)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        label.setStyleSheet("color: #9ca3af;")
        
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setText(default_value)
        input_field.setMinimumHeight(32)
        input_field.setFont(QFont("Segoe UI", 10))
        
        layout.addWidget(label)
        layout.addWidget(input_field)
        
        return container
    
    def _create_connection_button(self):
        """Crea el botón de conexión alineado con los inputs"""
        container = QFrame()
        layout = QVBoxLayout(container)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label invisible para mantener alineación
        button_label = QLabel("Acción")
        button_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        button_label.setStyleSheet("color: #9ca3af;")
        
        button = QPushButton("🔗 Conectar")
        button.setMinimumHeight(32)
        button.setMinimumWidth(120)
        button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3b82f6,
                    stop: 1 #2563eb
                );
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2563eb,
                    stop: 1 #1d4ed8
                );
            }
            QPushButton:pressed {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #1d4ed8,
                    stop: 1 #1e3a8a
                );
            }
            QPushButton:disabled {
                background: #4b5563;
                color: #9ca3af;
            }
        """)
        
        layout.addWidget(button_label)
        layout.addWidget(button)
        
        return container, button
    
    def _create_minimal_status(self):
        """Crea un indicador de estado como chip elegante"""
        container = QFrame()
        layout = QVBoxLayout(container)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Label superior
        status_header = QLabel("Estado")
        status_header.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        status_header.setStyleSheet("color: #9ca3af;")
        status_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Chip de estado - más ancho para texto completo
        self.status_chip = QFrame()
        self.status_chip.setMinimumHeight(32)
        self.status_chip.setMinimumWidth(110)  # Más ancho para el texto completo
        self.status_chip.setMaximumWidth(130)
        self.status_chip.setStyleSheet("""
            QFrame {
                background: rgba(239, 68, 68, 0.2);
                border: 1px solid #ef4444;
                border-radius: 16px;
            }
        """)
        
        chip_layout = QHBoxLayout(self.status_chip)
        chip_layout.setContentsMargins(10, 4, 10, 4)  # Más padding horizontal
        chip_layout.setSpacing(6)
        chip_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Texto del estado
        self.status_text = QLabel("Desconectado")
        self.status_text.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.status_text.setStyleSheet("color: #dfdfdf; border: none; background: transparent;")

        chip_layout.addWidget(self.status_text)
        
        layout.addWidget(status_header)
        layout.addWidget(self.status_chip)
        
        return container
    
    def _apply_styles(self):
        """Aplica estilos modernos y compactos"""
        self.setStyleSheet("""
            QGroupBox {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2d3748,
                    stop: 1 #1a202c
                );
                border: 1px solid #4299e1;
                border-radius: 10px;
                font-weight: 600;
                padding-top: 18px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 3px 12px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #4299e1,
                    stop: 1 #3182ce
                );
                color: white;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 600;
            }
            QLineEdit {
                background: #374151;
                color: #ffffff;
                border: 1px solid #4b5563;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 10px;
            }
            QLineEdit:focus {
                border: 2px solid #4299e1;
                background: #2d3748;
            }
            QLineEdit::placeholder {
                color: #9ca3af;
                font-style: italic;
            }
        """)
    
    def set_connecting_state(self):
        """Establece el estado de conectando"""
        self.connection_btn.setText("⏳ Conectando...")
        self.connection_btn.setEnabled(False)
        
        # Chip amarillo para conectando
        self.status_chip.setStyleSheet("""
            QFrame {
                background: rgba(245, 158, 11, 0.2);
                border: 1px solid #f59e0b;
                border-radius: 16px;
            }
        """)
        self.status_text.setText("Conectando")
        self.status_text.setStyleSheet("color: #f59e0b; border: none; background: transparent;")
    
    def set_connected_state(self):
        """Establece el estado de conectado"""
        self.connection_btn.setText("❌ Desconectar")
        self.connection_btn.setEnabled(True)
        self.host_input.setEnabled(False)
        self.port_input.setEnabled(False)
        
        # Chip verde para conectado
        self.status_chip.setStyleSheet("""
            QFrame {
                background: rgba(34, 197, 94, 0.2);
                border: 1px solid #22c55e;
                border-radius: 16px;
            }
        """)
        self.status_text.setText("Conectado")
        self.status_text.setStyleSheet("color: #22c55e; border: none; background: transparent;")
    
    def set_disconnected_state(self):
        """Establece el estado de desconectado"""
        self.connection_btn.setText("🔗 Conectar")
        self.connection_btn.setEnabled(True)
        self.host_input.setEnabled(True)
        self.port_input.setEnabled(True)
        
        # Chip rojo para desconectado
        self.status_chip.setStyleSheet("""
            QFrame {
                background: rgba(239, 68, 68, 0.2);
                border: 1px solid #ef4444;
                border-radius: 16px;
            }
        """)
        self.status_text.setText("Desconectado")
        self.status_text.setStyleSheet("color: #ef4444; border: none; background: transparent;")
    
    def get_connection_data(self):
        """Obtiene los datos de conexión"""
        host = self.host_input.text().strip()
        try:
            port = int(self.port_input.text().strip()) if self.port_input.text().strip().isdigit() else DEFAULT_PORT
        except ValueError:
            port = DEFAULT_PORT
        return host, port