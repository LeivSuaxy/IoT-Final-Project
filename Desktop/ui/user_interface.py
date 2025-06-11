from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QWidget, 
                             QFrame, QLabel, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction

from core.auth_models import UserData
from .components import PersonCard
from .styles import GROUP_STYLE
from .base_interface import BaseInterface
from utils.constants import WINDOW_TITLE


class UserInterface(BaseInterface):
    """Interfaz simplificada para usuarios no administradores"""
    
    def __init__(self, user_data: UserData):
        super().__init__(user_data)
        self.setWindowTitle(f"🏷️ Monitor RFID - {user_data.username}")
        self.resize(600, 500)
        self._init_ui()
        
    def _init_ui(self):
        """Inicializa la interfaz de usuario"""
        self._setup_window()
        self._setup_menu_bar()
        self._setup_central_widget()
    
    def _setup_window(self):
        """Configura la ventana principal"""
        self.setWindowTitle(f"{WINDOW_TITLE} - Usuario: {self.user_data.username}")
        self.setGeometry(100, 100, 700, 500)
        self.setMinimumSize(600, 700)
        self.setMaximumSize(800, 700)
    
    def _setup_menu_bar(self):
        """Configura la barra de menús simplificada"""
        self.menuBar().setNativeMenuBar(False)
        menubar = self.menuBar()
        
        # Solo menú de sesión
        session_menu = menubar.addMenu(f"👤 {self.user_data.username}")
        
        # Acción para cerrar sesión
        logout_action = QAction("🚪 Cerrar Sesión", self)
        logout_action.triggered.connect(self._logout)
        session_menu.addAction(logout_action)
        
        session_menu.addSeparator()
        
        # Acción para salir
        exit_action = QAction("❌ Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        session_menu.addAction(exit_action)
        
        # Aplicar estilos
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #262626;
                border: none;
                font-weight: bold;
                padding: 4px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
                border-radius: 6px;
                margin: 2px;
                color: #e5e7eb;
            }
            QMenuBar::item:selected {
                background-color: #374151;
                color: #60a5fa;
            }
            QMenu {
                background-color: #262626;
                color: #e5e7eb;
                border: 1px solid #484848;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
                margin: 1px;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: #3b82f6;
                color: white;
            }
        """)
    
    def _setup_central_widget(self):
        """Configura el widget central"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Elementos de la interfaz
        main_layout.addWidget(self._create_header())
        main_layout.addWidget(self._create_connection_section())  # Heredado de BaseInterface
        
        # El grupo de tarjeta actual se expande para ocupar el espacio restante
        current_info_group = self._create_current_info_group()
        main_layout.addWidget(current_info_group, 1)
    
    def _create_header(self):
        """Crea el header de la aplicación"""
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("""
            QFrame {
                background: #343434;
                border-radius: 10px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 10, 20, 10)
        
        title = QLabel("🏷️ Monitor RFID")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        
        # Mostrar email solo si existe
        email_text = f" | 📧 {self.user_data.email}" if self.user_data.email else ""
        user_info = QLabel(f"👤 {self.user_data.username}{email_text}")
        user_info.setFont(QFont("Arial", 10))
        user_info.setStyleSheet("color: #d1fae5;")
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(user_info)
        
        return header
    
    def _create_current_info_group(self):
        """Crea el grupo de información actual"""
        group = QGroupBox("👤 Tarjeta Actual")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        group.setStyleSheet(GROUP_STYLE)
        
        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        
        # Container para la tarjeta de persona
        self.person_card_container = QFrame()
        self.person_card_container.setMinimumHeight(200)
        self.person_card_container.setStyleSheet("""
            QFrame {
                background-color: #232323;
            }
        """)
        
        container_layout = QVBoxLayout(self.person_card_container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        
        # Estado de espera
        self.waiting_label = QLabel("⏳ Esperando escaneo de tarjeta...")
        self.waiting_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.waiting_label.setFont(QFont("Arial", 14, QFont.Weight.Normal))
        self.waiting_label.setStyleSheet("""
            color: #9ca3af; 
            padding: 40px;
            background: transparent;
            border: none;
        """)
        
        container_layout.addWidget(self.waiting_label)
        layout.addWidget(self.person_card_container, 1)
        
        # Status indicator
        self.status_label = QLabel("🔌 Desconectado del sistema RFID")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: #ef4444; padding: 5px;")
        layout.addWidget(self.status_label)
        
        return group
    
    # Implementación de métodos abstractos de BaseInterface
    def _show_person_card(self, data):
        """Muestra la tarjeta de persona"""
        # Limpiar container
        for i in reversed(range(self.person_card_container.layout().count())):
            widget = self.person_card_container.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Crear nueva tarjeta
        self.current_person_card = PersonCard(
            data['card_id'], 
            data['name'], 
            data['info']
        )
        self.person_card_container.layout().addWidget(self.current_person_card)
    
    # Callbacks de BaseInterface
    def _on_connecting(self, host, port):
        """Cuando se inicia conexión"""
        self.status_label.setText("🔄 Conectando al sistema RFID...")
        self.status_label.setStyleSheet("color: #f59e0b; padding: 5px;")
    
    def _on_connected(self, message):
        """Cuando se conecta exitosamente"""
        self.status_label.setText("🟢 Conectado - Listo para escanear tarjetas")
        self.status_label.setStyleSheet("color: #10b981; padding: 5px;")
    
    def _on_disconnected(self):
        """Cuando se desconecta"""
        self.status_label.setText("🔌 Desconectado del sistema RFID")
        self.status_label.setStyleSheet("color: #ef4444; padding: 5px;")
        self._clear_current_card()
    
    def _on_connection_lost(self, message):
        """Cuando se pierde la conexión"""
        self.status_label.setText("🔌 Conexión perdida")
        self.status_label.setStyleSheet("color: #ef4444; padding: 5px;")
        self._clear_current_card()
    
    def _on_raw_data_received(self, raw_message):
        """Muestra datos crudos para debugging"""
        print(f"[DEBUG] Mensaje crudo recibido: {raw_message}")
        
        # Opcional: mostrar en la interfaz para debugging
        if hasattr(self, 'debug_mode') and self.debug_mode:
            self.status_label.setText(f"DEBUG: {raw_message}")
    
    def _on_rfid_data_received(self, data):
        """Cuando se reciben datos RFID procesados"""
        card_id = data.get('card_id', 'Unknown')
        name = data.get('name', 'Usuario')
        message_type = data.get('message_type', 'OK')
        auth_verified = data.get('auth_verified', False)
        
        # Mostrar información más detallada
        auth_status = "🔒 Verificado" if auth_verified else "🔓 Sin auth"
        status_text = f"✅ {message_type}: {card_id} - {name} | {auth_status}"
        
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet("color: #10b981; padding: 5px;")
    
    def _on_rfid_error(self, error_message):
        """Cuando hay error en datos RFID"""
        self.status_label.setText(f"❌ Error: {error_message}")
        self.status_label.setStyleSheet("color: #ef4444; padding: 5px;")
    
    def _clear_current_card(self):
        """Limpia la tarjeta actual y muestra mensaje de espera"""
        for i in reversed(range(self.person_card_container.layout().count())):
            widget = self.person_card_container.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        self.person_card_container.layout().addWidget(self.waiting_label)
        self.current_person_card = None
    
    def _logout(self):
        """Cierra sesión del usuario"""
        reply = QMessageBox.question(
            self, 
            "Cerrar Sesión", 
            "¿Estás seguro de que deseas cerrar sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
    
    def _create_connection_section(self):
        """Crea la sección de conexión (sobrescribe el método de BaseInterface)"""
        group = QGroupBox("🔌 Conexión RFID")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        group.setStyleSheet(GROUP_STYLE)
        
        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        
        # Aquí puedes personalizar los elementos de la sección de conexión
        self.info_label = QLabel("⏳ Esperando tarjeta...")
        self.info_label.setFont(QFont("Arial", 14))
        self.info_label.setStyleSheet("""
            color: #e5e7eb; 
            background: #1f2937; 
            padding: 40px; 
            border-radius: 8px; 
            border: 2px solid #374151;
        """)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
        
        return group
    
    def update_person_info(self, data: dict):
        """Actualiza información simple"""
        name = data.get('name', 'Desconocido')
        auth_verified = data.get('auth_verified', False)
        access_granted = data.get('access_granted', False)
        
        if auth_verified:
            if access_granted:
                text = f"✅ {name}\n🚪 ACCESO PERMITIDO"
                color = "#10b981"
            else:
                text = f"❌ {name}\n🚪 ACCESO DENEGADO"
                color = "#ef4444"
        else:
            text = f"⚠️ {name}\n🚪 NO REGISTRADO"
            color = "#f59e0b"
        
        self.info_label.setText(text)
        self.info_label.setStyleSheet(f"""
            color: {color}; 
            background: #1f2937; 
            padding: 40px; 
            border-radius: 8px; 
            border: 2px solid #374151;
            font-size: 16px;
            font-weight: bold;
        """)