from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QGridLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from .status_indicator import StatusIndicator
from utils.constants import DEFAULT_HOST, DEFAULT_PORT
from ..styles import (
    CONNECTION_PANEL_STYLE, 
    PRIMARY_BTN_STYLE, 
    ARDUINO_BTN_READY_STYLE, 
    ARDUINO_BTN_IDLE_STYLE,
    STATUS_CHIP_STYLE
)


class ConnectionPanel(QGroupBox):
    """Panel modernizado para configurar y controlar la conexión"""
    
    def __init__(self, parent=None):
        super().__init__("🔌 Configuración de Conexión", parent)
        self.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self._is_connected = False
        self._is_arduino_ready = False  # 🔥 NUEVO ESTADO PARA ARDUINO
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Configura la interfaz del panel con botón de activación Arduino"""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)  # Menos espacio para acomodar el nuevo botón
        main_layout.setContentsMargins(20, 25, 20, 20)
        
        # Host input
        host_container = self._create_compact_input("Host", "127.0.0.1", str(DEFAULT_HOST))
        self.host_input = host_container.findChild(QLineEdit)
        
        # Port input
        port_container = self._create_compact_input("Puerto", "8080", str(DEFAULT_PORT))
        self.port_input = port_container.findChild(QLineEdit)
        
        # Botón de conexión
        button_container, self.connection_btn = self._create_connection_button()
        
        # 🔥 NUEVO: Botón de activación Arduino
        arduino_container, self.arduino_btn = self._create_arduino_button()
        
        # Estado de conexión
        status_container = self._create_minimal_status()
        
        # Distribución: Host (30%), Puerto (15%), Conexión (20%), Arduino (20%), Estado (15%)
        main_layout.addWidget(host_container, 2)
        main_layout.addWidget(port_container, 1)
        main_layout.addWidget(button_container)
        main_layout.addWidget(arduino_container)  # 🔥 NUEVO BOTÓN
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
        button.setStyleSheet(PRIMARY_BTN_STYLE)
        
        layout.addWidget(button_label)
        layout.addWidget(button)
        
        return container, button
    
    def _create_arduino_button(self):
        """Crea el botón de activación del Arduino"""
        container = QFrame()
        layout = QVBoxLayout(container)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label para alineación
        button_label = QLabel("Arduino")
        button_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        button_label.setStyleSheet("color: #9ca3af;")
        
        button = QPushButton("🔓 Activar")
        button.setMinimumHeight(32)
        button.setMinimumWidth(100)
        button.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        button.setEnabled(False)  # Inicialmente deshabilitado
        button.setStyleSheet(ARDUINO_BTN_IDLE_STYLE)
        
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
        self.status_chip.setMinimumWidth(110)
        self.status_chip.setMaximumWidth(130)
        self.status_chip.setStyleSheet("""
            QFrame {
                background: rgba(239, 68, 68, 0.2);
                border: 1px solid #ef4444;
                border-radius: 16px;
            }
        """)
        
        chip_layout = QHBoxLayout(self.status_chip)
        chip_layout.setContentsMargins(10, 4, 10, 4)
        chip_layout.setSpacing(6)
        chip_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Texto del estado
        self.status_text = QLabel("Desconectado")
        self.status_text.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.status_text.setStyleSheet("color: #ef4444; border: none; background: transparent;")

        chip_layout.addWidget(self.status_text)
        
        layout.addWidget(status_header)
        layout.addWidget(self.status_chip)
        
        return container
    
    def _apply_styles(self):
        """Aplica estilos modernos y compactos"""
        self.setStyleSheet(CONNECTION_PANEL_STYLE)
    
    def set_connecting_state(self):
        """Establece el estado de conectando"""
        self._is_connected = False
        self.connection_btn.setText("⏳ Conectando...")
        self.connection_btn.setEnabled(False)
        self.host_input.setEnabled(False)
        self.port_input.setEnabled(False)
        
        # 🔥 DESHABILITAR BOTÓN ARDUINO MIENTRAS CONECTA
        self.arduino_btn.setEnabled(False)
        
        # Chip amarillo para conectando
        self.status_chip.setStyleSheet(STATUS_CHIP_STYLE['warning'])
        self.status_text.setText("Conectando")
        self.status_text.setStyleSheet("color: #f59e0b; border: none; background: transparent;")
    
    def set_connected_state(self):
        """Establece el estado de conectado"""
        self._is_connected = True
        self.connection_btn.setText("❌ Desconectar")
        self.connection_btn.setEnabled(True)
        self.host_input.setEnabled(False)
        self.port_input.setEnabled(False)
        
        # 🔥 HABILITAR BOTÓN ARDUINO CUANDO ESTÉ CONECTADO
        self.arduino_btn.setEnabled(True)
        
        # Chip verde para conectado
        self.status_chip.setStyleSheet(STATUS_CHIP_STYLE['success'])
        self.status_text.setText("Conectado")
        self.status_text.setStyleSheet("color: #10b981; border: none; background: transparent;")
    
    def set_disconnected_state(self):
        """Establece el estado de desconectado"""
        self._is_connected = False
        self.connection_btn.setText("🔗 Conectar")
        self.connection_btn.setEnabled(True)
        self.host_input.setEnabled(True)
        self.port_input.setEnabled(True)
        
        # 🔥 DESHABILITAR BOTÓN ARDUINO CUANDO ESTÉ DESCONECTADO
        self.arduino_btn.setEnabled(False)
        self.set_arduino_idle_state()  # Resetear estado Arduino
        
        # Chip rojo para desconectado
        self.status_chip.setStyleSheet(STATUS_CHIP_STYLE['error'])
        self.status_text.setText("Desconectado")
        self.status_text.setStyleSheet("color: #ef4444; border: none; background: transparent;")
    
    def set_connection_failed_state(self):
        """Establece el estado de conexión fallida"""
        self._is_connected = False
        self.connection_btn.setText("🔗 Conectar")
        self.connection_btn.setEnabled(True)
        self.host_input.setEnabled(True)
        self.port_input.setEnabled(True)
        
        # Chip rojo para error
        self.status_chip.setStyleSheet(STATUS_CHIP_STYLE['error'])
        self.status_text.setText("Error")
        self.status_text.setStyleSheet("color: #ef4444; border: none; background: transparent;")
    
    def set_arduino_ready_state(self):
        """Establece el Arduino en modo espera (listo para recibir tarjetas)"""
        self._is_arduino_ready = True
        self.arduino_btn.setEnabled(True)  # 🔥 ASEGURAR QUE ESTÉ HABILITADO
        self.arduino_btn.setText("🔒 Desactivar")
        self.arduino_btn.setStyleSheet(ARDUINO_BTN_READY_STYLE)
        print(f"[DEBUG] 🔓 Arduino button set to READY state")
    
    def set_arduino_idle_state(self):
        """Establece el Arduino en modo inactivo (no acepta tarjetas)"""
        self._is_arduino_ready = False
        self.arduino_btn.setEnabled(True)  # 🔥 ASEGURAR QUE ESTÉ HABILITADO
        self.arduino_btn.setText("🔓 Activar")
        self.arduino_btn.setStyleSheet(ARDUINO_BTN_IDLE_STYLE)
        print(f"[DEBUG] 🔒 Arduino button set to IDLE state")
    
    def is_connected(self):
        """Retorna si está conectado"""
        return self._is_connected
    
    def is_arduino_ready(self):
        """Retorna si el Arduino está en modo espera"""
        return self._is_arduino_ready
    
    def get_connection_data(self):
        """Obtiene los datos de conexión"""
        host = self.host_input.text().strip()
        try:
            port = int(self.port_input.text().strip()) if self.port_input.text().strip().isdigit() else DEFAULT_PORT
        except ValueError:
            port = DEFAULT_PORT
        return host, port
    
    def get_arduino_command(self):
        """Obtiene el comando a enviar al Arduino según el protocolo"""
        if self._is_arduino_ready:
            # Arduino está activo, enviamos comando para desactivar
            return {
                "action": "deactivate_reader", 
                "command": "DISABLE"  # 🔥 CAMBIAR A DISABLE
            }
        else:
            # Arduino está inactivo, enviamos comando para activar
            return {
                "action": "activate_reader", 
                "command": "ENABLE"   # 🔥 CAMBIAR A ENABLE
            }
    
    def auto_disable_arduino(self):
        """Desactiva automáticamente el Arduino (llamado cuando se procesa una tarjeta)"""
        if self._is_arduino_ready:
            print("[DEBUG] 🔄 Auto-desactivando Arduino tras escaneo de tarjeta")
            self.set_arduino_idle_state()
            return True
        return False
    
    def reset_arduino_state(self):
        """Resetea el estado del Arduino a idle"""
        self.set_arduino_idle_state()