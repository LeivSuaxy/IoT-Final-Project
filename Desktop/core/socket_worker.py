"""Worker para manejo de conexiones socket"""

import socket
import json
from PyQt6.QtCore import QThread, pyqtSignal
from utils.constants import SOCKET_TIMEOUT, BUFFER_SIZE


class SocketWorker(QThread):
    """Worker thread para manejar conexiones socket de forma asíncrona"""
    
    data_received = pyqtSignal(dict)
    connection_status = pyqtSignal(bool, str)
    
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        
    def run(self):
        """Ejecuta el loop principal del worker"""
        try:
            self._connect_to_server()
            self._listen_for_data()
        except Exception as e:
            self.connection_status.emit(False, f"Error de conexión: {str(e)}")
        finally:
            self.close_connection()
    
    def _connect_to_server(self):
        """Establece la conexión con el servidor"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(SOCKET_TIMEOUT)
        self.socket.connect((self.host, self.port))
        self.socket.settimeout(None)
        self.running = True
        self.connection_status.emit(True, f"Conectado a {self.host}:{self.port}")
    
    def _listen_for_data(self):
        """Escucha datos del servidor"""
        buffer = ""
        while self.running:
            try:
                data = self.socket.recv(BUFFER_SIZE).decode('utf-8')
                if data:
                    buffer += data
                    buffer = self._process_messages(buffer)
                else:
                    break
            except Exception as e:
                if self.running:
                    self.connection_status.emit(False, f"Error al recibir datos: {str(e)}")
                break
    
    def _process_messages(self, buffer):
        """Procesa mensajes completos del buffer"""
        while '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            if line.strip():
                try:
                    rfid_data = json.loads(line.strip())
                    self.data_received.emit(rfid_data)
                except json.JSONDecodeError:
                    continue
        return buffer
    
    def close_connection(self):
        """Cierra la conexión"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connection_status.emit(False, "Desconectado")