"""Manejador de datos RFID - VERSIÓN NUEVA"""

from datetime import datetime
from typing import Dict, Any, Union
from PyQt6.QtCore import QObject, pyqtSignal

class RFIDDataHandler(QObject):
    """Manejador simplificado de datos RFID"""
    
    data_processed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.last_scan_time = None
        self.duplicate_threshold = 1.0  # 1 segundo
    
    def process_rfid_data(self, raw_data: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """Procesa datos RFID"""
        try:
            if not isinstance(raw_data, dict):
                return None
            
            if raw_data.get('type') == 'rfid_scan':
                current_time = datetime.now()
                
                # Verificar duplicados simples
                if self.last_scan_time:
                    time_diff = (current_time - self.last_scan_time).total_seconds()
                    if time_diff < self.duplicate_threshold:
                        return None
                
                self.last_scan_time = current_time
                
                # Procesar datos
                processed_data = {
                    'type': 'rfid_scan',
                    'card_id': raw_data.get('card_id'),
                    'card_hash': raw_data.get('card_hash'),
                    'name': raw_data.get('name', 'Usuario'),
                    'info': 'Tarjeta escaneada',
                    'timestamp': current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'auth_verified': False
                }
                
                # Emitir señal
                self.data_processed.emit(processed_data)
                return processed_data
            
            return raw_data
            
        except Exception as e:
            self.error_occurred.emit(str(e))
            return None