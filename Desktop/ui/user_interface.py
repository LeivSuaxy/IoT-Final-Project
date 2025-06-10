from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QFrame, QLabel, QGroupBox, QPushButton,
                             QTextEdit, QMenuBar, QMessageBox)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QAction
from datetime import datetime

from core import SocketWorker, RFIDDataHandler
from core.auth_models import UserData
from .components import PersonCard, ConnectionPanel
from .styles import GROUP_STYLE, CONNECTION_GROUP_STYLE
from utils.constants import WINDOW_TITLE, WINDOW_SIZE, MIN_WINDOW_SIZE


class UserInterface(QMainWindow):
    """Interfaz simplificada para usuarios no administradores"""
    
    def __init__(self, user_data: UserData):
        super().__init__()
        self.user_data = user_data
        self.socket_worker = None
        self.current_person_card = None
        self.data_handler = RFIDDataHandler()
        self._init_ui()
        
    def _init_ui(self):
        """Inicializa la interfaz de usuario"""
        self._setup_window()
        self._setup_menu_bar()
        self._setup_central_widget()
        self._setup_timer()
    
    def _setup_window(self):
        """Configura la ventana principal"""
        self.setWindowTitle(f"{WINDOW_TITLE} - Usuario: {self.user_data.username}")
        self.setGeometry(100, 100, 900, 600)  # Ventana más pequeña
        self.setMinimumSize(700, 500)
    
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

        main_layout.addWidget(self._create_header())
        main_layout.addWidget(self._create_connection_section())
        main_layout.addWidget(self._create_current_info_group())
        main_layout.addWidget(self._create_log_group())
    
    def _create_header(self):
        """Crea el header de la aplicación"""
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #059669,
                    stop: 1 #047857
                );
                border-radius: 10px;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        title = QLabel("🏷️ Monitor RFID")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: white; padding: 10px;")
        
        user_info = QLabel(f"👤 {self.user_data.username} | 📧 {self.user_data.email}")
        user_info.setFont(QFont("Arial", 11))
        user_info.setStyleSheet("color: #d1fae5; padding: 10px;")
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(user_info)
        
        return header
    
    def _create_connection_section(self):
        """Crea la sección de conexión"""
        self.connection_panel = ConnectionPanel()
        self.connection_panel.setStyleSheet(CONNECTION_GROUP_STYLE)
        self.connection_panel.connection_btn.clicked.connect(self._toggle_connection)
        
        return self.connection_panel
    
    def _create_current_info_group(self):
        """Crea el grupo de información actual"""
        group = QGroupBox("👤 Tarjeta Actual")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        group.setStyleSheet(GROUP_STYLE)
        
        layout = QVBoxLayout(group)
        
        self.person_card_container = QFrame()
        self.person_card_container.setMinimumHeight(250)
        self.person_card_container.setStyleSheet("""
            QFrame {
                background-color: #232323;
                border: 0
            }
        """)
        
        container_layout = QVBoxLayout(self.person_card_container)
        
        self.waiting_label = QLabel("⏳ Esperando escaneo de tarjeta...")
        self.waiting_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.waiting_label.setFont(QFont("Arial", 14))
        self.waiting_label.setStyleSheet("color: #9ca3af; padding: 50px;")
        
        container_layout.addWidget(self.waiting_label)
        layout.addWidget(self.person_card_container)
        
        return group
    
    def _create_log_group(self):
        """Crea el grupo de log simplificado"""
        group = QGroupBox("📝 Actividad Reciente")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        group.setStyleSheet(GROUP_STYLE)
        
        layout = QVBoxLayout(group)
        
        self.log_text = QTextEdit()
        self.log_text.setStyleSheet("background: #232323; border: 0;")
        self.log_text.setMaximumHeight(150)  # Más pequeño que la versión admin
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        
        layout.addWidget(self.log_text)
        
        return group
    
    def _setup_timer(self):
        """Configura el timer de actualización"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
    
    def _toggle_connection(self):
        """Alterna el estado de conexión"""
        if self.socket_worker is None or not self.socket_worker.isRunning():
            self._connect_to_server()
        else:
            self._disconnect()
    
    def _connect_to_server(self):
        """Conecta al servidor"""
        host, port = self.connection_panel.get_connection_data()
        
        self.socket_worker = SocketWorker(host, port)
        self.socket_worker.data_received.connect(self._handle_rfid_data)
        self.socket_worker.connection_status.connect(self._update_connection_status)
        self.socket_worker.start()
        
        self.connection_panel.set_connecting_state()
        self._log_message(f"🔄 Conectando a {host}:{port}...")
    
    def _disconnect(self):
        """Desconecta del servidor"""
        if self.socket_worker:
            self.socket_worker.close_connection()
            self.socket_worker.wait()
    
    def _handle_rfid_data(self, data):
        """Maneja los datos RFID recibidos"""
        try:
            processed_data = self.data_handler.process_rfid_data(data)
            
            self._show_person_card(processed_data)
            self._log_message(f"✅ Tarjeta: {processed_data['card_id']} - {processed_data['name']}")
            
        except Exception as e:
            self._log_message(f"❌ Error: {str(e)}")
    
    def _show_person_card(self, data):
        """Muestra la tarjeta de persona"""
        # Limpiar container
        for i in reversed(range(self.person_card_container.layout().count())):
            self.person_card_container.layout().itemAt(i).widget().setParent(None)
        
        # Crear nueva tarjeta
        self.current_person_card = PersonCard(
            data['card_id'], 
            data['name'], 
            data['info']
        )
        self.person_card_container.layout().addWidget(self.current_person_card)
    
    def _update_connection_status(self, connected, message):
        """Actualiza el estado de conexión"""
        if connected:
            self.connection_panel.set_connected_state()
        else:
            self.connection_panel.set_disconnected_state()
            
        self._log_message(f"🔌 {message}")
    
    def _log_message(self, message):
        """Agrega mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)
        
        # Mantener solo las últimas 20 líneas
        document = self.log_text.document()
        if document.blockCount() > 20:
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
        
        # Auto-scroll al final
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def _update_display(self):
        """Actualiza la interfaz periódicamente"""
        pass
    
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
    
    def closeEvent(self, event):
        """Maneja el cierre de la aplicación"""
        if self.socket_worker and self.socket_worker.isRunning():
            self.socket_worker.close_connection()
            self.socket_worker.wait()
        event.accept()