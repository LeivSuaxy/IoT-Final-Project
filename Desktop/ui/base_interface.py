from PyQt6.QtWidgets import QMainWindow, QMessageBox, QDialog
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime

from core import SocketWorker
from core.rfid_data_handler_new import RFIDDataHandler
from core.auth_models import UserData
from core.api_client import api_client
from .components import ConnectionPanel
from .components.register_card_dialog import RegisterCardDialog
from .components.contact_admin_dialog import ContactAdminDialog


class IdentifierWorker(QThread):
    """Worker para consultar identificadores en segundo plano"""
    
    found = pyqtSignal(dict)
    not_found = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, rfid_id: str):
        super().__init__()
        self.rfid_id = rfid_id
    
    def run(self):
        try:
            result = api_client.get_identifier(self.rfid_id)
            if result:
                self.found.emit(result)
            else:
                self.not_found.emit(self.rfid_id)
        except Exception as e:
            self.error.emit(str(e))


class BaseInterface(QMainWindow):
    """Clase base simplificada para interfaces RFID"""
    
    def __init__(self, user_data: UserData = None):
        super().__init__()
        self.user_data = user_data
        
        # Inicializar workers
        self.socket_worker = None
        self.identifier_worker = None
        
        # Inicializar data handler
        self.data_handler = RFIDDataHandler()
        self.data_handler.data_processed.connect(self._handle_rfid_data)
    
    def _create_connection_section(self):
        """Crea la sección de conexión"""
        self.connection_panel = ConnectionPanel()
        self.connection_panel.connection_btn.clicked.connect(self._toggle_connection)
        return self.connection_panel
    
    def _toggle_connection(self):
        """Alterna el estado de conexión"""
        if self.socket_worker is None or not self.socket_worker.isRunning():
            self._connect_to_server()
        else:
            self._disconnect_from_server()
    
    def _connect_to_server(self):
        """Conecta al servidor"""
        try:
            host, port = self.connection_panel.get_connection_data()
            
            if not host or not (1 <= port <= 65535):
                QMessageBox.warning(self, "Error", "Host o puerto inválido")
                return
            
            # 🔥 AGREGAR EVENTO DE INTENTO DE CONEXIÓN
            current_time = datetime.now().strftime("%H:%M:%S")
            self._add_connection_event(f"[{current_time}] 🔌 🔄 CONECTANDO A {host}:{port}...")
            
            # Crear worker
            self.socket_worker = SocketWorker(host, port)
            
            # Conectar señales existentes
            if hasattr(self.socket_worker, 'data_received'):
                self.socket_worker.data_received.connect(self._on_socket_data)
            
            if hasattr(self.socket_worker, 'connection_status'):
                self.socket_worker.connection_status.connect(self._on_connection_status)
            
            # Iniciar
            self.socket_worker.start()
            self.connection_panel.set_connecting_state()
            
        except Exception as e:
            current_time = datetime.now().strftime("%H:%M:%S")
            self._add_connection_event(f"[{current_time}] 🔌 ❌ ERROR DE CONEXIÓN: {str(e)}")
            QMessageBox.critical(self, "Error de Conexión", str(e))
            self.connection_panel.set_disconnected_state()
    
    def _disconnect_from_server(self):
        """Desconecta del servidor"""
        if self.socket_worker:
            current_time = datetime.now().strftime("%H:%M:%S")
            self._add_connection_event(f"[{current_time}] 🔌 🔄 DESCONECTANDO...")
            
            self.socket_worker.close_connection()
            self.socket_worker.wait(3000)
            self.socket_worker = None
            self.connection_panel.set_disconnected_state()
            
            # El evento final de desconexión se agregará en _on_connection_status
    
    def _on_socket_data(self, data):
        """Maneja datos del socket"""
        try:
            # El data_handler procesará automáticamente y emitirá señal
            self.data_handler.process_rfid_data(data)
            
            # 🔥 AGREGAR EVENTO DE DATOS RECIBIDOS (OPCIONAL)
            current_time = datetime.now().strftime("%H:%M:%S")
            if isinstance(data, dict) and data.get('type') == 'rfid_scan':
                # No loguear cada dato RFID, solo errores importantes
                pass
            else:
                self._add_connection_event(f"[{current_time}] 📡 Datos recibidos del servidor")
                
        except Exception as e:
            current_time = datetime.now().strftime("%H:%M:%S")
            self._add_connection_event(f"[{current_time}] ❌ ERROR PROCESANDO DATOS: {str(e)}")
            print(f"Error procesando datos: {e}")
    
    def _on_connection_status(self, connected, message):
        """Maneja cambios de estado de conexión"""
        current_time = datetime.now().strftime("%H:%M:%S")
        
        if connected:
            self.connection_panel.set_connected_state()
            # 🔥 AGREGAR EVENTO DE CONEXIÓN AL LOG
            self._add_connection_event(f"[{current_time}] 🔌 ✅ CONECTADO AL SERVIDOR")
        else:
            self.connection_panel.set_disconnected_state()
            # 🔥 AGREGAR EVENTO DE DESCONEXIÓN AL LOG
            self._add_connection_event(f"[{current_time}] 🔌 ❌ DESCONECTADO DEL SERVIDOR")
    
    def _add_connection_event(self, event: str):
        """Agrega evento de conexión al log - implementar en clases hijas"""
        # Llamar método específico si existe
        if hasattr(self, '_add_to_events_log'):
            self._add_to_events_log(event)
        else:
            print(f"[DEBUG] Evento de conexión: {event}")
    
    def _handle_rfid_data(self, data):
        """Maneja datos RFID procesados"""
        print(f"[DEBUG] Datos RFID: {data}")
        
        if data.get('type') == 'rfid_scan':
            # 🔥 MOSTRAR ESTADO INICIAL DE "VERIFICANDO"
            temp_data = {
                **data,
                'name': data.get('name', 'Usuario'),
                'info': 'Verificando en base de datos...',
                'auth_verified': False,  # Importante: False para mostrar "VERIFICANDO"
                'access_granted': False
            }
            self._display_rfid_data(temp_data)
            
            # Luego verificar en BD
            rfid_id = data.get('card_hash') or data.get('card_id')
            if rfid_id:
                self._check_identifier(rfid_id, data)
        else:
            # Mostrar directamente si no es RFID
            self._display_rfid_data(data)
    
    def _check_identifier(self, rfid_id: str, rfid_data: dict):
        """Verifica el identificador en la BD"""
        # Limpiar worker anterior
        if self.identifier_worker:
            self.identifier_worker.quit()
            self.identifier_worker.wait()
        
        # Crear nuevo worker
        self.identifier_worker = IdentifierWorker(rfid_id)
        self.identifier_worker.found.connect(
            lambda db_data: self._on_identifier_found(db_data, rfid_data)
        )
        self.identifier_worker.not_found.connect(
            lambda: self._on_identifier_not_found(rfid_id, rfid_data)
        )
        self.identifier_worker.error.connect(
            lambda error: self._on_identifier_error(error, rfid_data)
        )
        self.identifier_worker.start()
    
    def _on_identifier_found(self, db_data: dict, rfid_data: dict):
        """Cuando se encuentra la tarjeta en BD"""
        print(f"[DEBUG] Tarjeta encontrada en BD: {db_data}")
        
        # 🔥 COMBINAR DATOS INCLUYENDO DB_DATA COMPLETO
        combined_data = {
            **rfid_data,
            'name': db_data.get('name', 'Usuario'),
            'info': f"Acceso: {'✅ Permitido' if db_data.get('access') else '❌ Denegado'}",
            'auth_verified': True,
            'access_granted': db_data.get('access', False),
            'db_data': db_data  # 🔥 INCLUIR DATOS COMPLETOS DE BD PARA IMAGEN
        }
        
        print(f"[DEBUG] Datos combinados con imagen: {combined_data}")
        self._display_rfid_data(combined_data)
    
    def _on_identifier_not_found(self, rfid_id: str, rfid_data: dict):
        """Cuando no se encuentra la tarjeta"""
        if self.user_data and self.user_data.is_admin:
            self._show_register_dialog(rfid_id)
        else:
            self._show_contact_admin_dialog(rfid_id)
    
    def _on_identifier_error(self, error: str, rfid_data: dict):
        """Error al consultar BD"""
        QMessageBox.warning(self, "Error", f"Error consultando BD: {error}")
    
    def _show_register_dialog(self, rfid_id: str):
        """Muestra diálogo de registro"""
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            self._add_connection_event(f"[{current_time}] 📝 Abriendo diálogo de registro para tarjeta {rfid_id}")
            
            dialog = RegisterCardDialog(rfid_id, parent=self)
            result = dialog.exec()
            
            if result == QDialog.DialogCode.Accepted:
                current_time = datetime.now().strftime("%H:%M:%S")
                self._add_connection_event(f"[{current_time}] ✅ TARJETA {rfid_id} REGISTRADA EXITOSAMENTE")
                QMessageBox.information(self, "Éxito", "Tarjeta registrada exitosamente")
            else:
                current_time = datetime.now().strftime("%H:%M:%S")
                self._add_connection_event(f"[{current_time}] ❌ Registro de tarjeta {rfid_id} cancelado")
            
        except Exception as e:
            current_time = datetime.now().strftime("%H:%M:%S")
            self._add_connection_event(f"[{current_time}] ❌ ERROR EN REGISTRO: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error en registro: {e}")
    
    def _show_contact_admin_dialog(self, rfid_id):
        """Muestra diálogo de contacto admin"""
        try:
            dialog = ContactAdminDialog(rfid_id, self)
            dialog.exec()
        except Exception as e:
            print(f"Error mostrando dialog: {e}")
    
    def _display_rfid_data(self, data: dict):
        """Muestra datos RFID - implementar en clases hijas"""
        # Actualizar título como mínimo
        name = data.get('name', 'Desconocido')
        current_title = self.windowTitle()
        base_title = current_title.split(" - Último:")[0]
        self.setWindowTitle(f"{base_title} - Último: {name}")
        
        # Llamar método específico si existe
        if hasattr(self, 'update_person_info'):
            self.update_person_info(data)
    
    def closeEvent(self, event):
        """Limpia al cerrar"""
        if self.socket_worker:
            self.socket_worker.close_connection()
            self.socket_worker.wait(1000)
        
        if self.identifier_worker:
            self.identifier_worker.quit()
            self.identifier_worker.wait(1000)
        
        super().closeEvent(event)
    
    def _start_connection(self):
        """Inicia la conexión del socket (método alternativo)"""
        try:
            # Obtener host y puerto del connection_panel
            host, port = "localhost", 9999  # Valores por defecto
            if hasattr(self, 'connection_panel'):
                try:
                    host, port = self.connection_panel.get_connection_data()
                except:
                    print(f"[WARNING] No se pudo obtener datos de conexión, usando defaults")
            
            current_time = datetime.now().strftime("%H:%M:%S")
            self._add_connection_event(f"[{current_time}] 🔌 🔄 INICIANDO CONEXIÓN A {host}:{port}...")
            
            # Limpiar conexión anterior
            if self.socket_worker and self.socket_worker.isRunning():
                self.socket_worker.quit()
                self.socket_worker.wait()
                self.socket_worker.deleteLater()
            
            # Crear nuevo worker
            from core import SocketWorker
            self.socket_worker = SocketWorker(host, port)
            
            # Conectar señales
            if hasattr(self.socket_worker, 'data_received'):
                self.socket_worker.data_received.connect(self._on_socket_data)
            
            if hasattr(self.socket_worker, 'connection_status'):
                self.socket_worker.connection_status.connect(self._on_connection_status)
            
            # Iniciar worker
            self.socket_worker.start()
            
            if hasattr(self, 'connection_panel'):
                self.connection_panel.set_connecting_state()
            
        except Exception as e:
            current_time = datetime.now().strftime("%H:%M:%S")
            self._add_connection_event(f"[{current_time}] 🔌 ❌ ERROR INICIANDO CONEXIÓN: {str(e)}")
            raise
    
    def _stop_connection(self):
        """Detiene la conexión del socket"""
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            self._add_connection_event(f"[{current_time}] 🔌 🔄 DETENIENDO CONEXIÓN...")
            
            if self.socket_worker and self.socket_worker.isRunning():
                self.socket_worker.quit()
                
                if not self.socket_worker.wait(3000):
                    self.socket_worker.terminate()
                    self.socket_worker.wait()
                
                self.socket_worker.deleteLater()
                self.socket_worker = None
                
            current_time = datetime.now().strftime("%H:%M:%S")
            self._add_connection_event(f"[{current_time}] 🔌 ✅ CONEXIÓN DETENIDA")
                
        except Exception as e:
            current_time = datetime.now().strftime("%H:%M:%S")
            self._add_connection_event(f"[{current_time}] 🔌 ❌ ERROR DETENIENDO CONEXIÓN: {str(e)}")
            print(f"Error deteniendo conexión: {e}")