from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
                             QFrame, QScrollArea, QTextEdit, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from datetime import datetime
import requests


from core import api_client
from .base_interface import BaseInterface
from .styles import CONNECTION_GROUP_STYLE


class ImageLoaderWorker(QThread):
    """Worker para cargar imágenes desde el backend"""
    
    image_loaded = pyqtSignal(QPixmap, str)  # pixmap, name
    image_failed = pyqtSignal(str, str)      # error_msg, name
    
    def __init__(self, image_url: str, name: str):
        super().__init__()
        self.image_url = image_url
        self.name = name
    
    def run(self):
        """Descarga la imagen desde el backend"""
        try:
            print(f"[DEBUG] Descargando imagen: {self.image_url}")
            
            # 🔥 OBTENER TOKEN DE AUTENTICACIÓN
            from core.api_client import api_client
            headers = {}
            if hasattr(api_client, 'token') and api_client.token:
                headers['Authorization'] = f'Bearer {api_client.token}'
            
            # 🔥 DESCARGAR IMAGEN
            response = requests.get(
                self.image_url,
                headers=headers,
                timeout=10,  # Timeout de 10 segundos
                stream=True
            )
            
            if response.status_code == 200:
                # 🔥 CREAR PIXMAP DESDE LOS DATOS
                pixmap = QPixmap()
                if pixmap.loadFromData(response.content):
                    print(f"[DEBUG] ✅ Imagen descargada exitosamente")
                    self.image_loaded.emit(pixmap, self.name)
                else:
                    print(f"[ERROR] No se pudo crear pixmap desde los datos")
                    self.image_failed.emit("No se pudo procesar la imagen", self.name)
            else:
                error_msg = f"HTTP {response.status_code}: {response.reason}"
                print(f"[ERROR] Error descargando imagen: {error_msg}")
                self.image_failed.emit(error_msg, self.name)
                
        except requests.exceptions.Timeout:
            self.image_failed.emit("Timeout descargando imagen", self.name)
        except requests.exceptions.RequestException as e:
            self.image_failed.emit(f"Error de red: {str(e)}", self.name)
        except Exception as e:
            self.image_failed.emit(f"Error inesperado: {str(e)}", self.name)


class RFIDInterface(BaseInterface):
    """Interfaz RFID completa para administradores"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏷️ Sistema RFID - Control de Acceso")
        self.resize(1200, 800)
        
        # Lista para almacenar eventos
        self.events_log = []
        self.access_history = []
        
        self._init_ui()
        self._start_time_update()
        
        # 🔥 AGREGAR EVENTO INICIAL
        current_time = datetime.now().strftime("%H:%M:%S")
        self._add_to_events_log(f"[{current_time}] 🚀 SISTEMA INICIADO")
    
    def _init_ui(self):
        """Inicializa la interfaz completa"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Panel izquierdo (información actual + conexión)
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Panel derecho (logs e historial)
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel, 1)
    
    def _create_left_panel(self):
        """Crea el panel izquierdo con información actual"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Título principal
        title = QLabel("📡 Sistema RFID - Control de Acceso")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #10b981; text-align: center; margin: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Panel de conexión
        connection_panel = self._create_connection_section()
        layout.addWidget(connection_panel)
        
        # Información actual de la tarjeta
        current_info = self._create_current_info_widget()
        layout.addWidget(current_info)
        
        # Estado del sistema
        system_status = self._create_system_status_widget()
        layout.addWidget(system_status)
        
        layout.addStretch()
        return panel
    
    def _create_current_info_widget(self):
        """Crea el widget de información actual"""
        group = QGroupBox("👤 Información Actual")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        group.setStyleSheet(CONNECTION_GROUP_STYLE)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # Contenedor para imagen y datos
        content_layout = QHBoxLayout()
        
        # Imagen de la persona (placeholder)
        self.person_image = QLabel()
        self.person_image.setFixedSize(120, 120)
        self.person_image.setStyleSheet("""
            QLabel {
                border: 2px solid #374151;
                border-radius: 60px;
                background-color: #1f2937;
                color: #9ca3af;
            }
        """)
        self.person_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.person_image.setText("👤\nSin\nImagen")
        content_layout.addWidget(self.person_image)
        
        # Información de la persona
        info_layout = QVBoxLayout()
        
        self.person_name_label = QLabel("👤 Esperando tarjeta...")
        self.person_name_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.person_name_label.setStyleSheet("color: #e5e7eb; margin: 5px;")
        
        self.person_info_label = QLabel("ℹ️ ---")
        self.person_info_label.setFont(QFont("Arial", 12))
        self.person_info_label.setStyleSheet("color: #9ca3af; margin: 3px;")
        
        self.person_timestamp_label = QLabel("🕒 ---")
        self.person_timestamp_label.setFont(QFont("Arial", 10))
        self.person_timestamp_label.setStyleSheet("color: #6b7280; margin: 3px;")
        
        self.person_access_label = QLabel("🚪 Estado: Esperando...")
        self.person_access_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.person_access_label.setStyleSheet("color: #f59e0b; margin: 8px;")
        
        info_layout.addWidget(self.person_name_label)
        info_layout.addWidget(self.person_info_label)
        info_layout.addWidget(self.person_timestamp_label)
        info_layout.addWidget(self.person_access_label)
        info_layout.addStretch()
        
        content_layout.addLayout(info_layout)
        layout.addLayout(content_layout)
        
        return group
    
    def _create_system_status_widget(self):
        """Crea el widget de estado del sistema"""
        group = QGroupBox("⚙️ Estado del Sistema")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        group.setStyleSheet(CONNECTION_GROUP_STYLE)
        
        layout = QGridLayout(group)
        
        # Etiquetas de estado
        layout.addWidget(QLabel("🕒 Hora actual:"), 0, 0)
        self.current_time_label = QLabel("--:--:--")
        self.current_time_label.setStyleSheet("color: #10b981; font-weight: bold;")
        layout.addWidget(self.current_time_label, 0, 1)
        
        layout.addWidget(QLabel("📊 Total eventos:"), 1, 0)
        self.events_count_label = QLabel("0")
        self.events_count_label.setStyleSheet("color: #3b82f6; font-weight: bold;")
        layout.addWidget(self.events_count_label, 1, 1)
        
        layout.addWidget(QLabel("🚪 Accesos hoy:"), 2, 0)
        self.access_count_label = QLabel("0")
        self.access_count_label.setStyleSheet("color: #10b981; font-weight: bold;")
        layout.addWidget(self.access_count_label, 2, 1)
        
        return group
    
    def _create_right_panel(self):
        """Crea el panel derecho con logs"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Log de eventos
        events_group = self._create_events_log_widget()
        layout.addWidget(events_group)
        
        # Historial de accesos
        history_group = self._create_access_history_widget()
        layout.addWidget(history_group)
        
        return panel
    
    def _create_events_log_widget(self):
        """Crea el widget de log de eventos"""
        group = QGroupBox("📝 Log de Eventos")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        group.setStyleSheet(CONNECTION_GROUP_STYLE)
        
        layout = QVBoxLayout(group)
        
        # Área de texto para eventos
        self.events_text = QTextEdit()
        self.events_text.setMaximumHeight(450)
        self.events_text.setStyleSheet("""
            QTextEdit {
                background-color: #232323;
                color: #e5e7eb;
                border: none;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        self.events_text.setReadOnly(True)
        
        layout.addWidget(self.events_text)
        return group
    
    def _create_access_history_widget(self):
        """Crea el widget de historial de accesos"""
        group = QGroupBox("🚪 Historial de Accesos")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        group.setStyleSheet(CONNECTION_GROUP_STYLE)
        
        layout = QVBoxLayout(group)
        
        # Área de texto para historial
        self.history_text = QTextEdit()
        self.history_text.setMaximumHeight(450)
        self.history_text.setStyleSheet("""
            QTextEdit {
                background-color: #232323;
                color: #e5e7eb;
                border: none;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        self.history_text.setReadOnly(True)
        
        layout.addWidget(self.history_text)
        return group
    
    def _start_time_update(self):
        """Inicia la actualización del reloj"""
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self._update_current_time)
        self.time_timer.start(1000)  # Actualizar cada segundo
        self._update_current_time()  # Actualizar inmediatamente
    
    def _update_current_time(self):
        """Actualiza la hora actual"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.current_time_label.setText(current_time)
    
    def update_person_info(self, data: dict):
        """Actualiza la información de la persona mostrada"""
        name = data.get('name', 'Desconocido')
        info = data.get('info', 'Sin información')
        timestamp = data.get('timestamp', 'Sin timestamp')
        auth_verified = data.get('auth_verified', False)
        access_granted = data.get('access_granted', False)
        
        # Actualizar información actual
        self.person_name_label.setText(f"👤 {name}")
        self.person_name_label.setStyleSheet(
            f"color: {'#10b981' if auth_verified else '#ef4444'}; font-size: 16px; font-weight: bold; margin: 5px;"
        )
        
        self.person_info_label.setText(f"ℹ️ {info}")
        self.person_timestamp_label.setText(f"🕒 {timestamp}")
        
        # Estado de acceso
        if auth_verified:
            if access_granted:
                access_text = "🚪 ✅ ACCESO PERMITIDO"
                access_color = "#10b981"
                # Agregar al historial de accesos
                self._add_to_access_history(name, timestamp, True)
                # 🔥 SOLO AGREGAR AL LOG SI ESTÁ VERIFICADO
                self._add_to_events_log(f"[{timestamp}] {name} - {access_text}")
            else:
                access_text = "🚪 ❌ ACCESO DENEGADO"
                access_color = "#ef4444"
                self._add_to_access_history(name, timestamp, False)
                # 🔥 SOLO AGREGAR AL LOG SI ESTÁ VERIFICADO
                self._add_to_events_log(f"[{timestamp}] {name} - {access_text}")
        else:
            access_text = "🚪 ⚠️ VERIFICANDO..."  # 🔥 CAMBIAR TEXTO TEMPORAL
            access_color = "#f59e0b"
            # 🔥 NO AGREGAR AL LOG HASTA QUE SE VERIFIQUE
        
        self.person_access_label.setText(access_text)
        self.person_access_label.setStyleSheet(
            f"color: {access_color}; font-size: 14px; font-weight: bold; margin: 8px;"
        )
        
        # 🔥 REMOVER ESTA LÍNEA QUE CAUSABA EL PROBLEMA
        # self._add_to_events_log(f"[{timestamp}] {name} - {access_text}")
        
        # Actualizar imagen si existe
        self._update_person_image(data)
        
        # Actualizar contadores
        self._update_counters()
    
    def _update_person_image(self, data: dict):
        """Actualiza la imagen de la persona"""
        name = data.get('name', 'Usuario')
        
        # 🔥 VERIFICAR SI HAY DATOS DE BD CON IMAGEN
        db_data = data.get('db_data', {})
        image_path = db_data.get('image_path')
        
        if image_path:
            # 🔥 CARGAR IMAGEN DEL BACKEND
            self._load_image_from_backend(image_path, name)
        else:
            # 🔥 USAR INICIALES COMO FALLBACK
            self._show_person_initials(name)
    
    def _load_image_from_backend(self, image_path: str, name: str):
        """Carga imagen desde el backend"""
        try:
            # 🔥 CONSTRUIR URL COMPLETA
            # Si image_path es algo como "/static/images/filename.jpg"
            base_url = api_client.base_url.rstrip('/')  # Remover / final si existe
            if image_path.startswith('/'):
                image_url = f"{base_url}{image_path}"
            else:
                image_url = f"{base_url}/{image_path}"
            
            print(f"[DEBUG] Cargando imagen desde: {image_url}")
            
            # 🔥 CREAR WORKER PARA CARGAR IMAGEN EN SEGUNDO PLANO
            self.image_worker = ImageLoaderWorker(image_url, name)
            self.image_worker.image_loaded.connect(self._on_image_loaded)
            self.image_worker.image_failed.connect(self._on_image_failed)
            self.image_worker.start()
            
        except Exception as e:
            print(f"[ERROR] Error configurando carga de imagen: {e}")
            self._show_person_initials(name)
    
    def _on_image_loaded(self, pixmap: QPixmap, name: str):
        """Callback cuando la imagen se carga exitosamente"""
        try:
            size = 120
            
            # 🔥 CREAR IMAGEN CIRCULAR COMPLETA CON BORDE INTEGRADO
            
            # 1. Crear canvas más grande para incluir el borde
            full_size = size + 6  # 3px de borde en cada lado
            full_image = QPixmap(full_size, full_size)
            full_image.fill(Qt.GlobalColor.transparent)
            
            # 2. Configurar painter
            from PyQt6.QtGui import QPainter, QPainterPath, QPen, QBrush
            painter = QPainter(full_image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # 3. Dibujar borde circular
            border_pen = QPen(Qt.GlobalColor.green)  # Color verde del borde
            border_pen.setWidth(3)
            painter.setPen(border_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(1, 1, full_size - 2, full_size - 2)
            
            # 4. Crear path circular para la imagen (más pequeño que el borde)
            image_circle = QPainterPath()
            margin = 3  # Espacio para el borde
            image_circle.addEllipse(margin, margin, size, size)
            painter.setClipPath(image_circle)
            
            # 5. Escalar imagen para llenar el círculo interior
            scaled_pixmap = pixmap.scaled(
                size, size,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # 6. Centrar imagen si es más grande
            x = (scaled_pixmap.width() - size) // 2 if scaled_pixmap.width() > size else 0
            y = (scaled_pixmap.height() - size) // 2 if scaled_pixmap.height() > size else 0
            
            # 7. Dibujar imagen dentro del círculo
            painter.drawPixmap(margin, margin, scaled_pixmap, x, y, size, size)
            painter.end()
            
            # 8. Aplicar imagen circular SIN bordes CSS
            self.person_image.setPixmap(full_image)
            self.person_image.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    border: none;
                }
            """)
            
            # 9. Ajustar tamaño del label para la imagen más grande
            self.person_image.setFixedSize(full_size, full_size)
            
            print(f"[DEBUG] ✅ Imagen circular completa cargada para {name}")
            
        except Exception as e:
            print(f"[ERROR] Error creando imagen circular: {e}")
            import traceback
            traceback.print_exc()
            self._show_person_initials(name)
    
    def _on_image_failed(self, error_msg: str, name: str):
        """Callback cuando falla la carga de imagen"""
        print(f"[WARNING] Error cargando imagen: {error_msg}")
        self._show_person_initials(name)
    
    def _show_person_initials(self, name: str):
        """Muestra las iniciales de la persona"""
        try:
            size = 120
            full_size = size + 6  # Incluir espacio para borde
            
            # 🔥 CREAR IMAGEN CIRCULAR COMPLETA PARA INICIALES
            
            # 1. Crear canvas
            full_image = QPixmap(full_size, full_size)
            full_image.fill(Qt.GlobalColor.transparent)
            
            # 2. Configurar painter
            from PyQt6.QtGui import QPainter, QPen, QBrush, QFont as QGuiFont
            painter = QPainter(full_image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # 3. Dibujar fondo circular
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(Qt.GlobalColor.darkGray))  # Fondo gris oscuro
            painter.drawEllipse(3, 3, size, size)
            
            # 4. Dibujar borde
            border_pen = QPen(Qt.GlobalColor.green)
            border_pen.setWidth(3)
            painter.setPen(border_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(1, 1, full_size - 2, full_size - 2)
            
            # 5. Dibujar iniciales
            painter.setPen(QPen(Qt.GlobalColor.green))
            font = QGuiFont("Arial", 24, QGuiFont.Weight.Bold)
            painter.setFont(font)
            
            # Obtener iniciales
            initials = ''.join([word[0].upper() for word in name.split()[:2]])
            if not initials:
                initials = "?"
            
            # Centrar texto
            from PyQt6.QtCore import QRect
            text_rect = QRect(3, 3, size, size)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, initials)
            
            painter.end()
            
            # 6. Aplicar imagen
            self.person_image.setPixmap(full_image)
            self.person_image.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    border: none;
                }
            """)
            
            # 7. Ajustar tamaño
            self.person_image.setFixedSize(full_size, full_size)
            
            print(f"[DEBUG] Mostrando iniciales circulares '{initials}' para {name}")
            
        except Exception as e:
            print(f"[ERROR] Error creando iniciales circulares: {e}")
            # Fallback simple
            self.person_image.clear()
            initials = ''.join([word[0].upper() for word in name.split()[:2]])
            self.person_image.setText(initials or "?")
            self.person_image.setStyleSheet("""
                QLabel {
                    border: 2px solid #10b981;
                    border-radius: 60px;
                    background-color: #1f2937;
                    color: #10b981;
                    font-size: 24px;
                    font-weight: bold;
                }
            """)
    
    def _add_to_events_log(self, event: str):
        """Agrega un evento al log"""
        # 🔥 SI EL ÚLTIMO EVENTO ES "VERIFICANDO" Y ESTE ES DEFINITIVO, REEMPLAZAR
        if (self.events_log and 
            "🔄 Verificando..." in self.events_log[-1] and 
            "🔄 Verificando..." not in event):
            # Reemplazar el último evento en lugar de agregar uno nuevo
            self.events_log[-1] = event
        else:
            # Agregar evento normal
            self.events_log.append(event)
        
        # Mantener solo los últimos 50 eventos
        if len(self.events_log) > 50:
            self.events_log.pop(0)
        
        # Actualizar el display
        self.events_text.clear()
        self.events_text.append('\n'.join(self.events_log))
        
        # Scroll hacia abajo
        scrollbar = self.events_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _add_to_access_history(self, name: str, timestamp: str, granted: bool):
        """Agrega un acceso al historial"""
        status = "✅ PERMITIDO" if granted else "❌ DENEGADO"
        entry = f"[{timestamp}] {name} - {status}"
        
        self.access_history.append(entry)
        
        # Mantener solo los últimos 30 accesos
        if len(self.access_history) > 30:
            self.access_history.pop(0)
        
        # Actualizar el display
        self.history_text.clear()
        self.history_text.append('\n'.join(self.access_history))
        
        # Scroll hacia abajo
        scrollbar = self.history_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _update_counters(self):
        """Actualiza los contadores del sistema"""
        total_events = len(self.events_log)
        today_accesses = len([h for h in self.access_history if datetime.now().strftime("%Y-%m-%d") in h])
        
        self.events_count_label.setText(str(total_events))
        self.access_count_label.setText(str(today_accesses))
    
    def closeEvent(self, event):
        """Limpia recursos al cerrar"""
        if hasattr(self, 'time_timer'):
            self.time_timer.stop()
        
        # 🔥 LIMPIAR WORKER DE IMAGEN
        if hasattr(self, 'image_worker') and self.image_worker:
            if self.image_worker.isRunning():
                self.image_worker.quit()
                self.image_worker.wait(2000)
            self.image_worker.deleteLater()
        
        super().closeEvent(event)
    
    def _on_identifier_not_found(self, rfid_id: str, rfid_data: dict):
        """Cuando no se encuentra la tarjeta - SOBRESCRIBIR BaseInterface"""
        name = rfid_data.get('name', 'Desconocido')
        timestamp = rfid_data.get('timestamp', 'Sin timestamp')
        
        # 🔥 ACTUALIZAR INTERFAZ PARA NO REGISTRADO
        self.person_access_label.setText("🚪 ⚠️ NO REGISTRADO")
        self.person_access_label.setStyleSheet(
            "color: #f59e0b; font-size: 14px; font-weight: bold; margin: 8px;"
        )
        
        # 🔥 AHORA SÍ AGREGAR AL LOG PORQUE YA SE CONFIRMÓ
        self._add_to_events_log(f"[{timestamp}] {name} - 🚪 ⚠️ NO REGISTRADO")
        
        # Llamar al método padre para mostrar diálogos
        super()._on_identifier_not_found(rfid_id, rfid_data)
    
    def show_verification_status(self, name: str, timestamp: str):
        """Muestra estado temporal mientras se verifica"""
        # Actualizar solo el estado, no el log
        self.person_access_label.setText("🚪 🔄 VERIFICANDO...")
        self.person_access_label.setStyleSheet(
            "color: #3b82f6; font-size: 14px; font-weight: bold; margin: 8px;"
        )
        
        # Agregar evento temporal al log
        self._add_to_events_log(f"[{timestamp}] {name} - 🔄 Verificando...")
        
        # Actualizar la interfaz
        self.update()