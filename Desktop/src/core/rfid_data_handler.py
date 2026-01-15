"""Manejador de datos RFID - Unificado"""

from datetime import datetime
from typing import Dict, Any, Union
from PyQt6.QtCore import QObject, pyqtSignal

class RFIDDataHandler(QObject):
    """Maneja el procesamiento y formato de datos RFID"""
    
    data_processed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.last_scan_time = None
        self.duplicate_threshold = 2.0  # segundos para considerar duplicado
    
    def process_rfid_data(self, raw_data: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """
        Procesa datos RFID crudos y emite la señal data_processed
        """
        try:
            # Procesar string si es necesario
            if isinstance(raw_data, str):
                raw_data = {
                    'type': 'raw_string',
                    'message': raw_data,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            if not isinstance(raw_data, dict):
                raw_data = {
                    'type': 'unknown',
                    'message': str(raw_data),
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

            current_time = datetime.now()
            
            # Verificar duplicados para escaneos RFID
            if raw_data.get('type') == 'rfid_scan':
                if self._is_duplicate_scan(current_time):
                    # Ignorar duplicado silenciosamente o emitir error leve
                    # return None means duplicate ignored
                    return None
                self.last_scan_time = current_time
                result = self._process_rfid_scan(raw_data, current_time)
            
            elif raw_data.get('type') in ['info', 'confirmation', 'acknowledgment', 'authentication']:
                result = self._process_system_message(raw_data, current_time)
            
            elif raw_data.get('type') == 'raw_string':
                result = self._process_raw_string(raw_data, current_time)
            
            else:
                result = self._process_generic_message(raw_data, current_time)
            
            # Emitir señal con los datos procesados
            if result:
                self.data_processed.emit(result)
            
            return result

        except Exception as e:
            self.error_occurred.emit(str(e))
            return None
    
    def _process_rfid_scan(self, data: Dict[str, Any], scan_time: datetime) -> Dict[str, Any]:
        """Procesa un escaneo RFID específico"""
        card_id = data.get('card_id', 'Unknown')
        card_hash = data.get('card_hash', '')
        name = data.get('name', f'Usuario {card_id}')
        info = data.get('info', 'Tarjeta escaneada')
        
        # Buscar información adicional si es necesario
        enhanced_info = self._enhance_card_info(card_id, card_hash)
        
        return {
            'type': 'rfid_scan',
            'card_id': card_id,
            'card_hash': card_hash,
            'name': enhanced_info.get('name', name),
            'info': enhanced_info.get('info', info),
            'timestamp': scan_time.strftime("%Y-%m-%d %H:%M:%S"),
            'message_type': data.get('message_type', 'OK'),
            'auth_verified': bool(data.get('auth', '')),
            'raw_data': data
        }
    
    def _process_system_message(self, data: Dict[str, Any], scan_time: datetime) -> Dict[str, Any]:
        """Procesa mensajes del sistema"""
        message_type = data.get('type', 'system')
        message = data.get('message', 'Mensaje del sistema')
        
        return {
            'type': 'system_message',
            'card_id': 'SYSTEM',
            'card_hash': '',
            'name': 'Sistema',
            'info': f'{message_type.upper()}: {message}',
            'timestamp': scan_time.strftime("%Y-%m-%d %H:%M:%S"),
            'message_type': data.get('message_type', 'INFO'),
            'auth_verified': bool(data.get('auth', '')),
            'raw_data': data
        }
    
    def _process_raw_string(self, data: Dict[str, Any], scan_time: datetime) -> Dict[str, Any]:
        """Procesa strings crudos"""
        raw_message = data.get('message', 'Mensaje desconocido')
        
        return {
            'type': 'raw_data',
            'card_id': 'RAW',
            'card_hash': '',
            'name': 'Datos crudos',
            'info': f'Mensaje: {raw_message}',
            'timestamp': scan_time.strftime("%Y-%m-%d %H:%M:%S"),
            'message_type': 'RAW',
            'auth_verified': False,
            'raw_data': data
        }
    
    def _process_generic_message(self, data: Dict[str, Any], scan_time: datetime) -> Dict[str, Any]:
        """Procesa mensajes genéricos"""
        card_id = str(data.get('card_id', 'GENERIC'))
        name = str(data.get('name', 'Mensaje genérico'))
        info = str(data.get('message', data.get('data', 'Datos procesados')))
        
        return {
            'type': 'generic_message',
            'card_id': card_id,
            'card_hash': data.get('card_hash', ''),
            'name': name,
            'info': info,
            'timestamp': scan_time.strftime("%Y-%m-%d %H:%M:%S"),
            'message_type': data.get('message_type', 'UNKNOWN'),
            'auth_verified': bool(data.get('auth', '')),
            'raw_data': data
        }
    
    def _enhance_card_info(self, card_id: str, card_hash: str) -> Dict[str, str]:
        """Mejora la información de la tarjeta"""
        # Base de datos simulada de tarjetas conocidas (para fallback)
        known_cards = {
            'D52D74FE': {'name': 'Juan Pérez', 'info': 'Empleado - Departamento IT'},
            'A1B2C3D4': {'name': 'María García', 'info': 'Administradora - RR.HH.'},
        }
        
        search_key = card_id
        if card_hash and len(card_hash) >= 8:
            search_key = card_hash[-8:].upper()
        
        return known_cards.get(search_key, {
            'name': f'Usuario {card_id}',
            'info': f'Tarjeta no registrada - ID: {card_id}'
        })
    
    def _is_duplicate_scan(self, current_time: datetime) -> bool:
        """Verifica si es un escaneo duplicado reciente"""
        if self.last_scan_time is None:
            return False
        
        time_diff = (current_time - self.last_scan_time).total_seconds()
        return time_diff < self.duplicate_threshold