"""Manejador de datos RFID"""

from datetime import datetime
from typing import Dict, Any

class RFIDDataHandler:
    """Maneja el procesamiento y formato de datos RFID"""
    
    def __init__(self):
        self.last_scan_time = None
        self.duplicate_threshold = 2  # segundos para considerar duplicado
    
    def process_rfid_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa datos RFID crudos y retorna datos estructurados
        
        Args:
            raw_data: Datos del protocolo Rust parseados
            
        Returns:
            Diccionario con datos RFID procesados
        """
        current_time = datetime.now()
        
        # Verificar duplicados recientes
        if self._is_duplicate_scan(current_time):
            raise Exception("Escaneo duplicado detectado")
        
        self.last_scan_time = current_time
        
        # Extraer información del mensaje del protocolo
        if raw_data.get('type') == 'rfid_scan':
            return self._process_rfid_scan(raw_data, current_time)
        else:
            return self._process_generic_message(raw_data, current_time)
    
    def _process_rfid_scan(self, data: Dict[str, Any], scan_time: datetime) -> Dict[str, Any]:
        """Procesa un escaneo RFID específico"""
        card_id = data.get('card_id', 'Unknown')
        card_hash = data.get('card_hash', '')
        name = data.get('name', f'Usuario {card_id}')
        info = data.get('info', 'Tarjeta escaneada')
        
        # Buscar información adicional de la tarjeta si es necesario
        # (aquí podrías consultar una base de datos local o API)
        enhanced_info = self._enhance_card_info(card_id, card_hash)
        
        return {
            'card_id': card_id,
            'card_hash': card_hash,
            'name': enhanced_info.get('name', name),
            'info': enhanced_info.get('info', info),
            'timestamp': scan_time.strftime("%Y-%m-%d %H:%M:%S"),
            'message_type': data.get('message_type', 'OK'),
            'auth_verified': bool(data.get('auth', '')),
            'raw_data': data
        }
    
    def _process_generic_message(self, data: Dict[str, Any], scan_time: datetime) -> Dict[str, Any]:
        """Procesa mensajes genéricos como si fueran RFID"""
        message_type = data.get('type', 'unknown')
        message = data.get('message', str(data))
        
        return {
            'card_id': 'SYSTEM',
            'card_hash': '',
            'name': 'Mensaje del Sistema',
            'info': f'{message_type.upper()}: {message}',
            'timestamp': scan_time.strftime("%Y-%m-%d %H:%M:%S"),
            'message_type': data.get('message_type', 'INFO'),
            'auth_verified': bool(data.get('auth', '')),
            'raw_data': data
        }
    
    def _enhance_card_info(self, card_id: str, card_hash: str) -> Dict[str, str]:
        """
        Mejora la información de la tarjeta consultando fuentes adicionales
        En una implementación real, aquí consultarías una base de datos
        """
        # Base de datos simulada de tarjetas conocidas
        known_cards = {
            # Puedes agregar tarjetas conocidas aquí
            '52D74FE': {
                'name': 'Juan Pérez',
                'info': 'Empleado - Departamento IT'
            },
            # Agregar más según sea necesario
        }
        
        # Buscar por los últimos 8 caracteres del hash
        short_id = card_hash[-8:].upper() if card_hash else card_id
        
        if short_id in known_cards:
            return known_cards[short_id]
        
        # Si no se encuentra, generar información básica
        return {
            'name': f'Usuario {card_id}',
            'info': f'Tarjeta no registrada - ID: {card_id}'
        }
    
    def _is_duplicate_scan(self, current_time: datetime) -> bool:
        """Verifica si es un escaneo duplicado reciente"""
        if self.last_scan_time is None:
            return False
        
        time_diff = (current_time - self.last_scan_time).total_seconds()
        return time_diff < self.duplicate_threshold
    
    def format_history_item(self, card_id: str, name: str, timestamp: str) -> str:
        """Formatea un elemento para el historial"""
        time_part = timestamp.split(' ')[1] if ' ' in timestamp else timestamp
        return f"[{time_part}] {card_id} - {name}"
    
    def format_tooltip(self, card_id: str, name: str, timestamp: str) -> str:
        """Formatea un tooltip con información detallada"""
        return f"Tarjeta: {card_id}\nUsuario: {name}\nHora: {timestamp}"