from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QScrollArea, QFrame, QLabel, QGroupBox, QPushButton,
                             QListWidget, QListWidgetItem, QTextEdit)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
from datetime import datetime

from core import SocketWorker, RFIDDataHandler
from .components import PersonCard, ConnectionPanel
from .styles import GROUP_STYLE, CONNECTION_GROUP_STYLE
from utils.constants import WINDOW_TITLE, WINDOW_SIZE, MIN_WINDOW_SIZE, MAX_HISTORY_ITEMS


class RFIDInterface(QMainWindow):
    """Ventana principal de la interfaz RFID"""
    
    def __init__(self):
        super().__init__()
        self.socket_worker = None
        self.current_person_card = None
        self.data_handler = RFIDDataHandler()
        self._init_ui()
        
    def _init_ui(self):
        """Inicializa la interfaz de usuario"""
        self._setup_window()
        self._setup_central_widget()
        self._setup_timer()
    
    def _setup_window(self):
        """Configura la ventana principal"""
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, *WINDOW_SIZE)
        self.setMinimumSize(*MIN_WINDOW_SIZE)
    
    def _setup_central_widget(self):
        """Configura el widget central"""
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setCentralWidget(scroll_area)

        main_layout = QVBoxLayout(scroll_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        main_layout.addWidget(self._create_header())
        main_layout.addWidget(self._create_connection_section())
        main_layout.addLayout(self._create_content_layout())
    
    def _create_header(self):
        """Crea el header de la aplicación"""
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background: #232323;
                border-radius: 10px;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        title = QLabel("🏷️ Sistema de Control RFID")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white; padding: 10px;")
        
        system_info = QLabel("Monitoreo en Tiempo Real")
        system_info.setFont(QFont("Arial", 12))
        system_info.setStyleSheet("color: #bfdbfe; padding: 10px;")
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(system_info)
        
        return header
    
    def _create_connection_section(self):
        """Crea la sección de conexión"""
        self.connection_panel = ConnectionPanel()
        self.connection_panel.setStyleSheet(CONNECTION_GROUP_STYLE)
        self.connection_panel.connection_btn.clicked.connect(self._toggle_connection)
        return self.connection_panel
    
    def _create_content_layout(self):
        """Crea el layout de contenido principal"""
        content_layout = QHBoxLayout()

        left_column = QVBoxLayout()
        left_column.addWidget(self._create_current_info_group())
        left_column.addWidget(self._create_log_group())

        right_column = QVBoxLayout()
        right_column.addWidget(self._create_history_group())
        
        content_layout.addLayout(left_column, 3)
        content_layout.addLayout(right_column, 2)
        
        return content_layout
    
    def _create_current_info_group(self):
        """Crea el grupo de información actual"""
        group = QGroupBox("👤 Última Tarjeta Escaneada")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        group.setStyleSheet(GROUP_STYLE)
        
        layout = QVBoxLayout(group)
        
        self.person_card_container = QFrame()
        self.person_card_container.setMinimumHeight(200)
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
    
    def _create_history_group(self):
        """Crea el grupo de historial"""
        group = QGroupBox("📋 Historial de Escaneos")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        group.setStyleSheet(GROUP_STYLE)
        
        layout = QVBoxLayout(group)
        
        self.scan_history = QListWidget()
        self.scan_history.setStyleSheet("background: #232323; border: 0;")
        self.scan_history.setAlternatingRowColors(True)
        
        self.clear_history_btn = QPushButton("🗑️ Limpiar Historial")
        self.clear_history_btn.setMinimumHeight(35)
        self.clear_history_btn.clicked.connect(self._clear_history)
        
        layout.addWidget(self.scan_history)
        layout.addWidget(self.clear_history_btn)
        
        return group
    
    def _create_log_group(self):
        """Crea el grupo de log"""
        group = QGroupBox("📝 Log de Eventos")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        group.setStyleSheet(GROUP_STYLE)
        
        layout = QVBoxLayout(group)
        
        self.log_text = QTextEdit()
        self.log_text.setStyleSheet("background: #232323; border: 0;")
        self.log_text.setMaximumHeight(250)
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
        self._log_message(f"🔄 Intentando conectar a {host}:{port}...")
    
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
            self._add_to_history(processed_data)
            self._log_message(f"✅ Tarjeta escaneada: {processed_data['card_id']} - {processed_data['name']}")
            
        except Exception as e:
            self._log_message(f"❌ Error al procesar datos RFID: {str(e)}")
    
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
    
    def _add_to_history(self, data):
        """Agrega elemento al historial"""
        history_item = self.data_handler.format_history_item(
            data['card_id'], 
            data['name'], 
            data['timestamp']
        )
        
        list_item = QListWidgetItem(history_item)
        list_item.setToolTip(self.data_handler.format_tooltip(
            data['card_id'], 
            data['name'], 
            data['timestamp']
        ))
        
        self.scan_history.insertItem(0, list_item)
        
        # Limitar historial
        if self.scan_history.count() > MAX_HISTORY_ITEMS:
            self.scan_history.takeItem(self.scan_history.count() - 1)
    
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
        
        # Auto-scroll al final
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def _clear_history(self):
        """Limpia el historial"""
        self.scan_history.clear()
        self._log_message("🗑️ Historial limpiado")
    
    def _update_display(self):
        """Actualiza la interfaz periódicamente"""
        pass
    
    def closeEvent(self, event):
        """Maneja el cierre de la aplicación"""
        if self.socket_worker and self.socket_worker.isRunning():
            self.socket_worker.close_connection()
            self.socket_worker.wait()
        event.accept()