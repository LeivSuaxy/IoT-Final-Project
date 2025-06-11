"""Worker para manejo de conexiones socket"""

import socket
import json
import re
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from utils.constants import SOCKET_TIMEOUT, BUFFER_SIZE


class SocketWorker(QThread):
    """Worker thread para manejar conexiones socket de forma asíncrona con escucha continua"""
    
    # Señales para diferentes tipos de eventos
    data_received = pyqtSignal(dict)
    connection_status = pyqtSignal(bool, str)
    broadcast_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    raw_data_received = pyqtSignal(str)
    
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        self._reconnect_delay = 2000
        
        # Timer para reconexión automática
        self.reconnect_timer = QTimer()
        self.reconnect_timer.setSingleShot(True)
        self.reconnect_timer.timeout.connect(self._attempt_reconnect)
        
    def run(self):
        """Ejecuta el loop principal del worker con reconexión automática"""
        while self._reconnect_attempts < self._max_reconnect_attempts:
            try:
                self._connect_to_server()
                self._listen_continuously()
                break
                
            except Exception as e:
                self._handle_connection_error(str(e))
                if self.running:
                    self._schedule_reconnect()
                else:
                    break
        
        self.close_connection()
    
    def _connect_to_server(self):
        """Establece la conexión con el servidor Rust"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(SOCKET_TIMEOUT)
            self.socket.connect((self.host, self.port))
            
            self.socket.settimeout(1.0)
            self.running = True
            self._reconnect_attempts = 0
            
            self.connection_status.emit(True, f"Conectado a {self.host}:{self.port}")
            
        except Exception as e:
            raise Exception(f"Error al conectar: {str(e)}")
    
    def _listen_continuously(self):
        """Escucha datos del servidor de forma continua"""
        buffer = ""
        
        while self.running:
            try:
                data = self.socket.recv(BUFFER_SIZE).decode('utf-8')
                
                if data:
                    buffer += data
                    buffer = self._process_protocol_messages(buffer)
                else:
                    raise Exception("Servidor cerró la conexión")
                    
            except socket.timeout:
                continue
                
            except Exception as e:
                if self.running:
                    raise Exception(f"Error al recibir datos: {str(e)}")
                break
    
    def _process_protocol_messages(self, buffer):
        """Procesa mensajes del protocolo Rust completos del buffer"""
        while '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            if line.strip():
                self._handle_protocol_message(line.strip())
        return buffer
    
    def _handle_protocol_message(self, message):
        """Maneja mensajes del protocolo Rust"""
        try:
            # Emitir el mensaje crudo para debugging
            self.raw_data_received.emit(message)
            
            # Parsear el mensaje usando el protocolo Rust
            parsed_data = self._parse_protocol_message(message)
            
            if parsed_data:
                message_type = parsed_data.get('message_type', 'unknown')
                
                # Manejar según el tipo de mensaje
                if message_type == 'INFO':
                    # Información general (puede incluir datos RFID)
                    self._handle_info_message(parsed_data)
                elif message_type == 'OK':
                    # Mensaje de éxito (típicamente escaneo RFID exitoso)
                    self._handle_ok_message(parsed_data)
                elif message_type == 'ERR':
                    # Error del servidor
                    self.error_occurred.emit(parsed_data.get('data', 'Error desconocido'))
                elif message_type == 'ACK':
                    # Acknowledgment
                    self._handle_ack_message(parsed_data)
                elif message_type == 'MISS':
                    # Datos perdidos
                    self._handle_miss_message(parsed_data)
                elif message_type == 'CMD':
                    # Comando (probablemente broadcast)
                    self.broadcast_received.emit(parsed_data)
                elif message_type == 'AUTH':
                    # Autenticación
                    self._handle_auth_message(parsed_data)
                else:
                    # Mensaje desconocido
                    self.data_received.emit(parsed_data)
            else:
                # Si no se puede parsear, crear un mensaje genérico
                generic_data = {
                    'type': 'unparsed_message',
                    'raw_message': message,
                    'timestamp': self._get_timestamp()
                }
                self.error_occurred.emit(f"Mensaje no reconocido: {message}")
                
        except Exception as e:
            self.error_occurred.emit(f"Error procesando mensaje: {str(e)}")
    
    def _parse_protocol_message(self, message):
        """
        Parsea mensajes del protocolo Rust: TIPO_DATOS|AUTH
        Ejemplo: OK_339CE2C11F368BB774A772C01AF01F5E9B541C9492D1DC64C086D156D52D74FE
        """
        message = message.strip()
        
        print(f"[DEBUG] Procesando mensaje del protocolo: {message}")
        
        # Separar mensaje y auth por pipe
        parts = message.split('|', 1)
        base_message = parts[0]
        auth = parts[1] if len(parts) == 2 else ""
        
        # Separar tipo de mensaje y datos por underscore
        msg_parts = base_message.split('_', 1)
        if len(msg_parts) != 2:
            print(f"[DEBUG] Formato inválido: {message}")
            return None
        
        message_type_str = msg_parts[0]
        data = msg_parts[1]
        
        # Verificar que el tipo de mensaje sea válido
        valid_types = ['AUTH', 'INFO', 'ERR', 'ACK', 'MISS', 'CMD', 'OK']
        if message_type_str not in valid_types:
            print(f"[DEBUG] Tipo de mensaje inválido: {message_type_str}")
            return None
        
        return {
            'message_type': message_type_str,
            'data': data,
            'auth': auth,
            'timestamp': self._get_timestamp(),
            'raw_message': message
        }
    
    def _handle_info_message(self, parsed_data):
        """Maneja mensajes INFO"""
        # Los mensajes INFO pueden contener datos RFID u otra información
        data = parsed_data.get('data', '')
        
        # Si parece ser un hash RFID (hexadecimal largo)
        if self._is_rfid_hash(data):
            rfid_data = self._create_rfid_data(data, parsed_data)
            self.data_received.emit(rfid_data)
        else:
            # Información general
            info_data = {
                'type': 'info',
                'message': data,
                'timestamp': parsed_data.get('timestamp'),
                'auth': parsed_data.get('auth', '')
            }
            self.data_received.emit(info_data)
    
    def _handle_ok_message(self, parsed_data):
        """Maneja mensajes OK (típicamente escaneo RFID exitoso)"""
        data = parsed_data.get('data', '')
        
        # Los mensajes OK con hash largo típicamente son escaneos RFID exitosos
        if self._is_rfid_hash(data):
            rfid_data = self._create_rfid_data(data, parsed_data)
            self.data_received.emit(rfid_data)
        else:
            # Confirmación general
            ok_data = {
                'type': 'confirmation',
                'message': f"Operación exitosa: {data}",
                'timestamp': parsed_data.get('timestamp'),
                'auth': parsed_data.get('auth', '')
            }
            self.data_received.emit(ok_data)
    
    def _handle_ack_message(self, parsed_data):
        """Maneja mensajes ACK"""
        ack_data = {
            'type': 'acknowledgment',
            'message': f"Confirmado: {parsed_data.get('data', '')}",
            'timestamp': parsed_data.get('timestamp'),
            'auth': parsed_data.get('auth', '')
        }
        self.data_received.emit(ack_data)
    
    def _handle_miss_message(self, parsed_data):
        """Maneja mensajes MISS"""
        miss_data = {
            'type': 'missed_data',
            'message': f"Datos perdidos: {parsed_data.get('data', '')}",
            'timestamp': parsed_data.get('timestamp'),
            'auth': parsed_data.get('auth', '')
        }
        self.error_occurred.emit(f"Datos perdidos: {parsed_data.get('data', '')}")
    
    def _handle_auth_message(self, parsed_data):
        """Maneja mensajes AUTH"""
        auth_data = {
            'type': 'authentication',
            'message': f"Autenticación: {parsed_data.get('data', '')}",
            'timestamp': parsed_data.get('timestamp'),
            'auth': parsed_data.get('auth', '')
        }
        self.data_received.emit(auth_data)
    
    def _is_rfid_hash(self, data):
        """Verifica si los datos parecen ser un hash RFID"""
        # Un hash RFID típicamente es una cadena hexadecimal larga
        return (
            len(data) >= 32 and  # Al menos 32 caracteres
            all(c in '0123456789ABCDEFabcdef' for c in data)  # Solo caracteres hex
        )
    
    def _create_rfid_data(self, rfid_hash, parsed_data):
        """Crea datos estructurados para escaneo RFID"""
        # Obtener los últimos 8 caracteres para crear un ID más legible
        short_id = rfid_hash[-8:].upper()
        
        return {
            'type': 'rfid_scan',
            'card_id': short_id,  # ID corto más legible
            'card_hash': rfid_hash,  # Hash completo
            'name': f'Usuario {short_id}',  # Nombre genérico
            'info': f'Tarjeta escaneada - Hash: {rfid_hash[:16]}...',
            'timestamp': parsed_data.get('timestamp'),
            'auth': parsed_data.get('auth', ''),
            'message_type': parsed_data.get('message_type'),
            'raw_message': parsed_data.get('raw_message')
        }
    
    def _get_timestamp(self):
        """Genera timestamp actual"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _handle_connection_error(self, error_msg):
        """Maneja errores de conexión"""
        self.connection_status.emit(False, f"Error de conexión: {error_msg}")
        self.error_occurred.emit(error_msg)
    
    def _schedule_reconnect(self):
        """Programa un intento de reconexión"""
        if self._reconnect_attempts < self._max_reconnect_attempts:
            self._reconnect_attempts += 1
            delay = self._reconnect_delay * self._reconnect_attempts
            
            self.connection_status.emit(
                False, 
                f"Reconectando en {delay//1000}s... (intento {self._reconnect_attempts}/{self._max_reconnect_attempts})"
            )
            
            self.reconnect_timer.start(delay)
    
    def _attempt_reconnect(self):
        """Intenta reconectar"""
        if self.running:
            self.connection_status.emit(False, "Intentando reconectar...")
    
    def send_protocol_message(self, message_type, data, auth=""):
        """Envía un mensaje usando el protocolo Rust"""
        if self.socket and self.running:
            try:
                # Construir mensaje según el protocolo: TIPO_DATOS|AUTH
                if auth:
                    protocol_message = f"{message_type}_{data}|{auth}"
                else:
                    protocol_message = f"{message_type}_{data}"
                
                # Agregar \n si no lo tiene
                if not protocol_message.endswith('\n'):
                    protocol_message += '\n'
                
                print(f"[DEBUG] Enviando: {protocol_message.strip()}")
                self.socket.send(protocol_message.encode('utf-8'))
                return True
            except Exception as e:
                self.error_occurred.emit(f"Error al enviar mensaje: {str(e)}")  # Corregir: era error_ocurrido
                return False
        return False
    
    def send_message(self, message):
        """Método de compatibilidad para envío de mensajes"""
        if isinstance(message, dict):
            message_type = message.get('type', 'CMD')
            data = message.get('data', '')
            auth = message.get('auth', '')
            return self.send_protocol_message(message_type, data, auth)
        else:
            # Asumir que es un comando
            return self.send_protocol_message('CMD', str(message))
    
    def close_connection(self):
        """Cierra la conexión"""
        self.running = False
        self.reconnect_timer.stop()
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            finally:
                self.socket = None
        
        self.connection_status.emit(False, "Desconectado")
    
    def force_disconnect(self):
        """Fuerza la desconexión sin reconexión"""
        self._reconnect_attempts = self._max_reconnect_attempts
        self.close_connection()