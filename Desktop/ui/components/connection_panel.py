from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtGui import QFont
from .status_indicator import StatusIndicator
from utils.constants import DEFAULT_HOST, DEFAULT_PORT


class ConnectionPanel(QGroupBox):
    """Panel para configurar y controlar la conexión"""
    
    def __init__(self, parent=None):
        super().__init__("🔌 Configuración de Conexión", parent)
        self.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self._setup_ui()
    
    def _create_host_input(self):
        """Crea el campo de entrada para host"""
        host_input = QLineEdit(str(DEFAULT_HOST))
        host_input.setStyleSheet("background: #333333; border: 1px solid #3f3f3f")
        host_input.setPlaceholderText("🌐 Dirección IP")
        host_input.setMinimumHeight(35)
        return host_input
    
    def _create_port_input(self):
        """Crea el campo de entrada para puerto"""
        port_input = QLineEdit(str(DEFAULT_PORT))
        port_input.setStyleSheet("background: #333333; border: 1px solid #3f3f3f")
        port_input.setPlaceholderText("🔌 Puerto")
        port_input.setMinimumHeight(35)
        return port_input
    
    def _create_connection_button(self):
        """Crea el botón de conexión"""
        button = QPushButton("🔗 Conectar")
        button.setMinimumHeight(35)
        return button
    
    def _create_status_label(self):
        """Crea la etiqueta de estado"""
        label = QLabel("Desconectado")
        label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        label.setStyleSheet("color: #ef4444; font-weight: bold;")
        return label
    
    def _setup_ui(self):
        """Configura la interfaz del panel"""
        layout = QHBoxLayout(self)

        self.host_input = self._create_host_input()
        self.port_input = self._create_port_input()

        self.connection_btn = self._create_connection_button()

        self.status_indicator = StatusIndicator()
        self.status_label = self._create_status_label()

        self.status_indicator.set_status(False)

        layout.addWidget(QLabel("Host:"))
        layout.addWidget(self.host_input)
        layout.addWidget(QLabel("Puerto:"))
        layout.addWidget(self.port_input)
        layout.addWidget(self.connection_btn)
        
        layout.addWidget(self.status_indicator)
        layout.addWidget(self.status_label)
    
    def get_connection_data(self):
        """Obtiene los datos de conexión"""
        host = self.host_input.text().strip()
        try:
            port = int(self.port_input.text().strip()) if self.port_input.text().strip().isdigit() else DEFAULT_PORT
        except ValueError:
            port = DEFAULT_PORT
        return host, port
    
    def set_connecting_state(self):
        """Establece el estado de conectando"""
        self.connection_btn.setText("⏳ Conectando...")
        self.connection_btn.setEnabled(False)
    
    def set_connected_state(self):
        """Establece el estado de conectado"""
        self.connection_btn.setText("❌ Desconectar")
        self.connection_btn.setEnabled(True)
        self.host_input.setEnabled(False)
        self.port_input.setEnabled(False)
        self.status_label.setText("Conectado")
        self.status_label.setStyleSheet("color: #22c55e; font-weight: bold;")
        self.status_indicator.set_status(True)
    
    def set_disconnected_state(self):
        """Establece el estado de desconectado"""
        self.connection_btn.setText("🔗 Conectar")
        self.connection_btn.setEnabled(True)
        self.host_input.setEnabled(True)
        self.port_input.setEnabled(True)
        self.status_label.setText("Desconectado")
        self.status_label.setStyleSheet("color: #ef4444; font-weight: bold;")
        self.status_indicator.set_status(False)