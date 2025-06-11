from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QWidget, 
                             QFrame, QLabel, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QAction, QPixmap, QPainter, QPainterPath, QPen, QBrush, QFont as QGuiFont
import requests

from core.auth_models import UserData
from .components import PersonCard
from .styles import GROUP_STYLE
from .base_interface import BaseInterface
from utils.constants import WINDOW_TITLE
from datetime import datetime


class ImageLoaderWorker(QThread):
    """Worker para cargar imágenes desde el backend"""
    
    image_loaded = pyqtSignal(QPixmap, str)
    image_failed = pyqtSignal(str, str)
    
    def __init__(self, image_url: str, name: str):
        super().__init__()
        self.image_url = image_url
        self.name = name
    
    def run(self):
        """Descarga la imagen desde el backend"""
        try:
            from core.api_client import api_client
            headers = {}
            if hasattr(api_client, 'token') and api_client.token:
                headers['Authorization'] = f'Bearer {api_client.token}'
            
            response = requests.get(
                self.image_url,
                headers=headers,
                timeout=10,
                stream=True
            )
            
            if response.status_code == 200:
                pixmap = QPixmap()
                if pixmap.loadFromData(response.content):
                    self.image_loaded.emit(pixmap, self.name)
                else:
                    self.image_failed.emit("No se pudo procesar la imagen", self.name)
            else:
                self.image_failed.emit(f"HTTP {response.status_code}", self.name)
                
        except Exception as e:
            self.image_failed.emit(str(e), self.name)


class UserInterface(BaseInterface):
    """Interfaz simplificada para usuarios no administradores"""
    
    def __init__(self, user_data: UserData):
        super().__init__(user_data)
        self.setWindowTitle(f"🏷️ Monitor RFID - {user_data.username}")
        self.resize(700, 500)  # Tamaño ajustado
        
        # 🔥 NO HAY TIMER DE LIMPIEZA
        
        self._init_ui()
    
    def _init_ui(self):
        """Inicializa la interfaz de usuario"""
        self._setup_window()
        self._setup_menu_bar()
        self._setup_central_widget()
    
    def _setup_window(self):
        """Configura la ventana principal"""
        self.setWindowTitle(f"{WINDOW_TITLE} - Usuario: {self.user_data.username}")
        self.setGeometry(100, 100, 800, 600)  # 🔥 VENTANA MÁS GRANDE
        self.setMinimumSize(700, 550)  # 🔥 TAMAÑO MÍNIMO AJUSTADO
        self.setMaximumSize(1000, 800)  # 🔥 TAMAÑO MÁXIMO AJUSTADO
    
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
        
        # 🔥 USAR EL PANEL DE CONEXIÓN HEREDADO DE BaseInterface
        main_layout.addWidget(self._create_connection_section())
        
        # El grupo de información actual se expande para ocupar el espacio restante
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
        """Crea el grupo de información actual simplificado"""
        group = QGroupBox("👤 Información de Tarjeta RFID")
        group.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3f3f3f;
                border-radius: 12px;
                margin: 10px 0px;
                padding-top: 15px;
                background-color: #232323;
                color: #e5e7eb;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #10b981;
                background-color: #232323;
                font-size: 16px;
            }
        """)
        
        main_layout = QVBoxLayout(group)
        main_layout.setContentsMargins(30, 35, 30, 25)
        main_layout.setSpacing(0)
        
        # 🔥 CONTENEDOR PRINCIPAL HORIZONTAL (SIN BORDES EXTRA)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(40)  # Más espacio entre imagen e info
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # 🔥 IMAGEN DE LA PERSONA (ALINEADA ARRIBA)
        image_container = QWidget()
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Alinear arriba
        
        self.person_image = QLabel()
        self.person_image.setFixedSize(120, 120)  # Tamaño intermedio
        self.person_image.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
            }
        """)
        self.person_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.person_image.setText("👤")
        
        image_layout.addWidget(self.person_image)
        image_layout.addStretch()  # Push hacia arriba
        content_layout.addWidget(image_container)
        
        # 🔥 INFORMACIÓN DETALLADA (SIN CONTENEDOR EXTRA)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(15)  # Más espacio entre elementos
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Alinear arriba
        
        # Nombre de la persona
        self.person_name_label = QLabel("⏳ Esperando tarjeta...")
        self.person_name_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.person_name_label.setStyleSheet("color: #e5e7eb; margin: 0px;")
        self.person_name_label.setWordWrap(True)
        info_layout.addWidget(self.person_name_label)
        
        # Información de acceso
        self.access_status_label = QLabel("🚪 ---")
        self.access_status_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.access_status_label.setStyleSheet("color: #9ca3af; margin: 0px;")
        info_layout.addWidget(self.access_status_label)
        
        # Hora del escaneo
        self.timestamp_label = QLabel("🕒 ---")
        self.timestamp_label.setFont(QFont("Arial", 13))
        self.timestamp_label.setStyleSheet("color: #6b7280; margin: 0px;")
        info_layout.addWidget(self.timestamp_label)
        
        # Información adicional
        self.additional_info_label = QLabel("📄 ---")
        self.additional_info_label.setFont(QFont("Arial", 11))
        self.additional_info_label.setStyleSheet("color: #9ca3af; margin: 0px;")
        self.additional_info_label.setWordWrap(True)
        info_layout.addWidget(self.additional_info_label)
        
        # 🔥 ELIMINAR STRETCH PARA QUE NO SE EXPANDA DEMASIADO
        content_layout.addLayout(info_layout, 1)
        
        # Agregar el layout principal
        main_layout.addLayout(content_layout)
        
        # 🔥 STATUS BAR SIMPLE
        self.status_label = QLabel("🔌 Desconectado del sistema RFID")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("""
            color: #ef4444; 
            background: transparent; 
            margin-top: 20px;
            padding: 8px;
            text-align: center;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(self.status_label)
        
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
    
    def _toggle_connection(self):
        """Alterna el estado de conexión - heredado de BaseInterface"""
        super()._toggle_connection()
    
    def _add_connection_event(self, event: str):
        """Agrega evento de conexión al log - versión simple para usuarios"""
        print(f"[CONNECTION] {event}")
        
        # 🔥 OPCIONAL: MOSTRAR EVENTOS DE CONEXIÓN EN EL STATUS LABEL
        current_time = datetime.now().strftime("%H:%M:%S")
        
        if "CONECTADO AL SERVIDOR" in event:
            if hasattr(self, 'status_label'):
                self.status_label.setText("🟢 Conectado - Listo para escanear tarjetas")
                self.status_label.setStyleSheet("color: #10b981; padding: 5px;")
        elif "DESCONECTADO DEL SERVIDOR" in event:
            if hasattr(self, 'status_label'):
                self.status_label.setText("🔌 Desconectado del sistema RFID")
                self.status_label.setStyleSheet("color: #ef4444; padding: 5px;")
        elif "CONECTANDO" in event:
            if hasattr(self, 'status_label'):
                self.status_label.setText("🔄 Conectando al sistema RFID...")
                self.status_label.setStyleSheet("color: #f59e0b; padding: 5px;")
    
    def update_person_info(self, data: dict):
        """Actualiza información completa para usuarios - SIN LIMPIEZA AUTOMÁTICA"""
        name = data.get('name', 'Desconocido')
        info = data.get('info', 'Sin información')
        timestamp = data.get('timestamp', 'Sin timestamp')
        auth_verified = data.get('auth_verified', False)
        access_granted = data.get('access_granted', False)
        
        print(f"[DEBUG] UserInterface.update_person_info: {data}")
        
        # 🔥 ACTUALIZAR NOMBRE
        self.person_name_label.setText(f"👤 {name}")
        self.person_name_label.setStyleSheet(
            f"color: {'#10b981' if auth_verified else '#ef4444'}; "
            f"font-size: 20px; font-weight: bold; margin: 0px;"
        )
        
        # 🔥 ACTUALIZAR ESTADO DE ACCESO
        if auth_verified:
            if access_granted:
                access_text = "🚪 ✅ ACCESO PERMITIDO"
                access_color = "#10b981"
            else:
                access_text = "🚪 ❌ ACCESO DENEGADO"
                access_color = "#ef4444"
        else:
            access_text = "🚪 ⚠️ NO REGISTRADO"
            access_color = "#f59e0b"
        
        self.access_status_label.setText(access_text)
        self.access_status_label.setStyleSheet(
            f"color: {access_color}; font-size: 16px; font-weight: bold; margin: 0px;"
        )
        
        # 🔥 ACTUALIZAR TIMESTAMP
        self.timestamp_label.setText(f"🕒 {timestamp}")
        self.timestamp_label.setStyleSheet("color: #9ca3af; font-size: 13px; margin: 0px;")
        
        # 🔥 ACTUALIZAR INFORMACIÓN ADICIONAL (SIMPLE)
        card_id = data.get('card_hash', data.get('card_id', 'N/A'))
        if len(card_id) > 20:
            card_display = f"{card_id[:20]}..."
        else:
            card_display = card_id
        
        self.additional_info_label.setText(f"📄 ID: {card_display}")
        self.additional_info_label.setStyleSheet("color: #9ca3af; font-size: 11px; margin: 0px;")
        
        # 🔥 ACTUALIZAR IMAGEN
        self._update_person_image(data)
        
        # 🔥 NO HAY TIMER DE LIMPIEZA - LA INFORMACIÓN PERMANECE
        
        print(f"[DEBUG] ✅ Información actualizada (sin limpieza automática)")
    
    def _update_person_image(self, data: dict):
        """Actualiza la imagen de la persona - versión simplificada"""
        name = data.get('name', 'Usuario')
        
        # Verificar si hay datos de BD con imagen
        db_data = data.get('db_data', {})
        image_path = db_data.get('image_path')
        
        if image_path:
            # Cargar imagen del backend
            self._load_image_from_backend(image_path, name)
        else:
            # Usar iniciales como fallback
            self._show_person_initials(name)
    
    def _load_image_from_backend(self, image_path: str, name: str):
        """Carga imagen desde el backend"""
        try:
            from core.api_client import api_client
            
            # Construir URL completa
            base_url = api_client.base_url.rstrip('/')
            if image_path.startswith('/'):
                image_url = f"{base_url}{image_path}"
            else:
                image_url = f"{base_url}/{image_path}"
            
            print(f"[DEBUG] Cargando imagen: {image_url}")
            
            # Crear worker para cargar imagen
            self.image_worker = ImageLoaderWorker(image_url, name)
            self.image_worker.image_loaded.connect(self._on_image_loaded)
            self.image_worker.image_failed.connect(self._on_image_failed)
            self.image_worker.start()
            
        except Exception as e:
            print(f"[ERROR] Error cargando imagen: {e}")
            self._show_person_initials(name)
    
    def _on_image_loaded(self, pixmap: QPixmap, name: str):
        """Callback cuando la imagen se carga exitosamente"""
        try:
            size = 120  # 🔥 TAMAÑO AJUSTADO
            full_size = size + 4
            
            # Crear imagen circular completa
            full_image = QPixmap(full_size, full_size)
            full_image.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(full_image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Dibujar borde
            border_pen = QPen(Qt.GlobalColor.green)
            border_pen.setWidth(2)  # Borde más fino
            painter.setPen(border_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(1, 1, full_size - 2, full_size - 2)
            
            # Crear path circular para la imagen
            image_circle = QPainterPath()
            margin = 2
            image_circle.addEllipse(margin, margin, size, size)
            painter.setClipPath(image_circle)
            
            # Escalar imagen
            scaled_pixmap = pixmap.scaled(
                size, size,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Centrar imagen
            x = (scaled_pixmap.width() - size) // 2 if scaled_pixmap.width() > size else 0
            y = (scaled_pixmap.height() - size) // 2 if scaled_pixmap.height() > size else 0
            
            # Dibujar imagen
            painter.drawPixmap(margin, margin, scaled_pixmap, x, y, size, size)
            painter.end()
            
            # Aplicar imagen
            self.person_image.setPixmap(full_image)
            self.person_image.setFixedSize(full_size, full_size)
            
            print(f"[DEBUG] ✅ Imagen cargada para {name}")
            
        except Exception as e:
            print(f"[ERROR] Error aplicando imagen: {e}")
            self._show_person_initials(name)
    
    def _on_image_failed(self, error_msg: str, name: str):
        """Callback cuando falla la carga de imagen"""
        print(f"[WARNING] Error cargando imagen: {error_msg}")
        self._show_person_initials(name)
    
    def _show_person_initials(self, name: str):
        """Muestra las iniciales de la persona"""
        try:
            size = 120
            full_size = size + 4
            
            # Crear imagen circular para iniciales
            full_image = QPixmap(full_size, full_size)
            full_image.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(full_image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Fondo circular
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(Qt.GlobalColor.darkGray))
            painter.drawEllipse(2, 2, size, size)
            
            # Borde
            border_pen = QPen(Qt.GlobalColor.green)
            border_pen.setWidth(2)
            painter.setPen(border_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(1, 1, full_size - 2, full_size - 2)
            
            # Iniciales
            painter.setPen(QPen(Qt.GlobalColor.green))
            font = QGuiFont("Arial", 28, QGuiFont.Weight.Bold)
            painter.setFont(font)
            
            initials = ''.join([word[0].upper() for word in name.split()[:2]])
            if not initials:
                initials = "?"
            
            from PyQt6.QtCore import QRect
            text_rect = QRect(2, 2, size, size)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, initials)
            painter.end()
            
            # Aplicar imagen
            self.person_image.setPixmap(full_image)
            self.person_image.setFixedSize(full_size, full_size)
            
        except Exception as e:
            print(f"[ERROR] Error creando iniciales: {e}")
            # Fallback simple
            self.person_image.setText("👤")
            self.person_image.setStyleSheet("font-size: 40px; color: #6b7280;")
    
    def closeEvent(self, event):
        """Limpia recursos al cerrar"""
        # 🔥 LIMPIAR WORKER DE IMAGEN
        if hasattr(self, 'image_worker') and self.image_worker:
            if self.image_worker.isRunning():
                self.image_worker.quit()
                self.image_worker.wait(2000)
            self.image_worker.deleteLater()
        
        super().closeEvent(event)