from PyQt6.QtWidgets import QMainWindow, QMessageBox, QDialog
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime

from core import SocketWorker
from core.rfid_data_handler import RFIDDataHandler
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
        from .components import ConnectionPanel
        
        self.connection_panel = ConnectionPanel()
        
        # Conectar botones
        self.connection_panel.connection_btn.clicked.connect(self._toggle_connection)
        # 🔥 CONECTAR BOTÓN ARDUINO
        self.connection_panel.arduino_btn.clicked.connect(self._toggle_arduino_state)
        
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
        """Maneja datos del socket con detección de auto-desactivación Arduino"""
        try:
            print(f"[DEBUG] Datos recibidos del socket: {data}")
            
            # 🔥 VERIFICAR SI ES ACK DE COMANDO ARDUINO
            if data.get('type') == 'arduino_command_ack':
                command = data.get('command', '')
                print(f"[DEBUG] ✅ Recibido ACK de Arduino para comando: {command}")
                
                # 🔥 MANEJAR ACK DE COMANDOS DE ACCESO
                current_time = datetime.now().strftime("%H:%M:%S")
                if command == 'PERMIT':
                    self._add_connection_event(f"[{current_time}] 🔊 ✅ Arduino reprodujo sonido de ACCESO PERMITIDO")
                elif command == 'DENY':
                    self._add_connection_event(f"[{current_time}] 🔊 ❌ Arduino reprodujo sonido de ACCESO DENEGADO")
                elif command == 'ENABLE':
                    print("[DEBUG] Confirmado: Arduino activado")
                elif command == 'DISABLE':
                    print("[DEBUG] Confirmado: Arduino desactivado")
            
            # 🔥 VERIFICAR SI ES CUALQUIER ESCANEO RFID
            elif data.get('type') == 'rfid_scan':
                print("[DEBUG] 🔄 Escaneo RFID detectado - Arduino se desactiva automáticamente")
                self._handle_arduino_auto_disable()
            
            # El data_handler procesará automáticamente y emitirá señal
            self.data_handler.process_rfid_data(data)
                
        except Exception as e:
            current_time = datetime.now().strftime("%H:%M:%S")
            self._add_connection_event(f"[{current_time}] ❌ ERROR PROCESANDO DATOS: {str(e)}")
            print(f"Error procesando datos: {e}")
    
    def _handle_arduino_auto_disable(self):
        """Maneja la desactivación automática del Arduino después de un escaneo"""
        try:
            if hasattr(self, 'connection_panel') and self.connection_panel.is_connected():
                # 🔥 USAR EL MÉTODO ESPECÍFICO DEL PANEL
                was_disabled = self.connection_panel.auto_disable_arduino()
                
                if was_disabled:
                    current_time = datetime.now().strftime("%H:%M:%S")
                    self._add_connection_event(f"[{current_time}] 🔄 Arduino desactivado automáticamente tras escaneo")
                    print("[DEBUG] ✅ Arduino auto-desactivado tras escaneo RFID")
                
        except Exception as e:
            print(f"[ERROR] Error en auto-desactivación de Arduino: {e}")
    
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
        
        # Determinar si el acceso está permitido
        access_granted = db_data.get('access', False)
        user_name = db_data.get('name', 'Usuario')
        
        # 🔥 ENVIAR COMANDO AL ARDUINO SEGÚN EL RESULTADO
        self._send_access_command(access_granted, user_name)
        
        # Combinar datos incluyendo DB_DATA completo
        combined_data = {
            **rfid_data,
            'name': user_name,
            'info': f"Acceso: {'✅ Permitido' if access_granted else '❌ Denegado'}",
            'auth_verified': True,
            'access_granted': access_granted,
            'db_data': db_data  # Incluir datos completos de BD para imagen
        }
        
        print(f"[DEBUG] Datos combinados con imagen: {combined_data}")
        self._display_rfid_data(combined_data)
    
    def _on_identifier_not_found(self, rfid_id: str, rfid_data: dict):
        """Cuando no se encuentra la tarjeta"""
        print(f"[DEBUG] Tarjeta NO encontrada en BD: {rfid_id}")
        
        # 🔥 ENVIAR COMANDO DE DENY PARA TARJETAS NO REGISTRADAS
        self._send_access_command(False, f"Tarjeta {rfid_id[-8:]}")
        
        # Crear datos para mostrar
        not_found_data = {
            **rfid_data,
            'name': f'Tarjeta {rfid_id[-8:]}',
            'info': '⚠️ No registrada en el sistema',
            'auth_verified': False,
            'access_granted': False
        }
        
        # Mostrar información de tarjeta no encontrada
        self._display_rfid_data(not_found_data)
        
        # Mostrar diálogos según el tipo de usuario
        if self.user_data and self.user_data.is_admin:
            self._show_register_dialog(rfid_id)
        else:
            self._show_contact_admin_dialog(rfid_id)

    def _on_identifier_error(self, error: str, rfid_data: dict):
        """Error al consultar BD"""
        print(f"[DEBUG] Error consultando BD: {error}")
        
        # 🔥 ENVIAR COMANDO DE DENY EN CASO DE ERROR
        self._send_access_command(False, "Error BD")
        
        # Crear datos de error
        error_data = {
            **rfid_data,
            'name': 'Error del Sistema',
            'info': f'Error consultando BD: {error}',
            'auth_verified': False,
            'access_granted': False
        }
        
        self._display_rfid_data(error_data)
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
    
    def _toggle_arduino_state(self):
        """Alterna el estado del Arduino (activar/desactivar modo espera)"""
        try:
            if not self.connection_panel.is_connected():
                QMessageBox.warning(self, "Error", "Debe estar conectado al servidor primero")
                return
            
            # 🔥 OBTENER ESTADO ACTUAL ANTES DE CAMBIAR
            was_ready = self.connection_panel.is_arduino_ready()
            
            # Deshabilitar botón temporalmente
            self.connection_panel.arduino_btn.setEnabled(False)
            self.connection_panel.arduino_btn.setText("⏳ Enviando...")
            
            # Obtener comando basado en estado actual
            command_data = self.connection_panel.get_arduino_command()
            command = command_data.get('command', '')
            
            print(f"[DEBUG] Estado Arduino actual: {'Ready' if was_ready else 'Idle'}")
            print(f"[DEBUG] Enviando comando: {command}")
            
            # Enviar comando
            if self.socket_worker and self.socket_worker.running:
                success = self.socket_worker.send_arduino_command(command)
                
                if success:
                    # 🔥 CAMBIAR ESTADO BASADO EN EL COMANDO ENVIADO
                    current_time = datetime.now().strftime("%H:%M:%S")
                    
                    if command == "ENABLE":
                        # Se envió ENABLE, Arduino ahora está activo
                        self.connection_panel.set_arduino_ready_state()
                        self._add_connection_event(f"[{current_time}] 🔓 Arduino: Modo espera ACTIVADO (CMD_ENABLE)")
                    elif command == "DISABLE":
                        # Se envió DISABLE, Arduino ahora está inactivo
                        self.connection_panel.set_arduino_idle_state()
                        self._add_connection_event(f"[{current_time}] 🔒 Arduino: Modo espera DESACTIVADO (CMD_DISABLE)")
                    
                    # 🔥 ASEGURAR QUE EL BOTÓN SE REHABILITE
                    self.connection_panel.arduino_btn.setEnabled(True)
                    
                    print(f"[DEBUG] ✅ Estado Arduino actualizado: {'Ready' if self.connection_panel.is_arduino_ready() else 'Idle'}")
                    
                else:
                    # 🔥 RESTAURAR BOTÓN EN CASO DE ERROR
                    self._restore_arduino_button_state(was_ready)
                    QMessageBox.warning(self, "Error", f"Error enviando comando {command}")
            else:
                # 🔥 RESTAURAR BOTÓN SI NO HAY CONEXIÓN
                self._restore_arduino_button_state(was_ready)
                QMessageBox.warning(self, "Error", "No hay conexión activa con el servidor")
                
        except Exception as e:
            # 🔥 RESTAURAR BOTÓN EN CASO DE EXCEPCIÓN
            if hasattr(self, 'connection_panel'):
                self._restore_arduino_button_state(getattr(self, '_arduino_was_ready', False))
            
            QMessageBox.critical(self, "Error", f"Error enviando comando al Arduino: {e}")
            print(f"[ERROR] Error toggle Arduino: {e}")
    
    def _restore_arduino_button_state(self, was_ready):
        """Restaura el estado del botón Arduino"""
        try:
            self.connection_panel.arduino_btn.setEnabled(True)
            if was_ready:
                self.connection_panel.set_arduino_ready_state()
            else:
                self.connection_panel.set_arduino_idle_state()
        except Exception as e:
            print(f"[ERROR] Error restaurando estado del botón: {e}")
    
    def _send_access_command(self, access_granted: bool, user_name: str):
        """Envía comando PERMIT o DENY al Arduino"""
        try:
            if not (hasattr(self, 'socket_worker') and self.socket_worker and self.socket_worker.running):
                print("[WARNING] No hay conexión de socket para enviar comando de acceso")
                return
            
            # Determinar comando según el acceso
            command = "PERMIT" if access_granted else "DENY"
            
            # Enviar comando al Arduino
            success = self.socket_worker.send_arduino_command(command)
            
            if success:
                current_time = datetime.now().strftime("%H:%M:%S")
                status_msg = "✅ ACCESO PERMITIDO" if access_granted else "❌ ACCESO DENEGADO"
                sound_msg = "♪ Sonido de éxito" if access_granted else "♫ Sonido de error"
                
                # Log del evento
                self._add_connection_event(f"[{current_time}] 🔊 {status_msg} - {user_name} (CMD_{command})")
                print(f"[DEBUG] ✅ Comando {command} enviado al Arduino para {user_name}")
                print(f"[INFO] {current_time} - {status_msg} - {user_name} - {sound_msg}")
                
            else:
                print(f"[ERROR] ❌ Error enviando comando {command} al Arduino")
                current_time = datetime.now().strftime("%H:%M:%S")
                self._add_connection_event(f"[{current_time}] ❌ Error enviando CMD_{command} para {user_name}")
                
        except Exception as e:
            print(f"[ERROR] Error en _send_access_command: {e}")
            current_time = datetime.now().strftime("%H:%M:%S")
            self._add_connection_event(f"[{current_time}] ❌ Excepción en comando de acceso: {str(e)}")