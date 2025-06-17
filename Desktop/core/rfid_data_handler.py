"""Manejador de datos RFID"""

from datetime import datetime
from typing import Dict, Any, Union

class RFIDDataHandler:
    """Maneja el procesamiento y formato de datos RFID"""
    
    def __init__(self):
        self.last_scan_time = None
        self.duplicate_threshold = 2  # segundos para considerar duplicado
        print("[DEBUG] RFIDDataHandler inicializado - VERSIÓN NUEVA")  # Para verificar que se ejecuta
    
    def process_rfid_data(self, raw_data: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """
        Procesa datos RFID crudos y retorna datos estructurados
        """
        print("[DEBUG] === RFIDDataHandler.process_rfid_data() VERSIÓN NUEVA ===")
        print(f"[DEBUG] raw_data tipo: {type(raw_data)}")
        print(f"[DEBUG] raw_data contenido: {raw_data}")
        
        # FORZAR QUE SIEMPRE MANTENGA EL TIPO PARA DEBUG
        if isinstance(raw_data, dict) and raw_data.get('type') == 'rfid_scan':
            print("[DEBUG] 🚨 DETECTADO ESCANEO RFID - PROCESANDO DIRECTAMENTE")
            
            current_time = datetime.now()
            
            # Verificar duplicados
            if self._is_duplicate_scan(current_time):
                raise Exception("Escaneo duplicado detectado")
            
            self.last_scan_time = current_time
            
            # Procesar directamente como RFID scan
            result = self._process_rfid_scan(raw_data, current_time)
            print(f"[DEBUG] 🎯 Resultado RFID directo: {result}")
            return result
        
        # Si no es RFID scan, continuar con el flujo normal...
        # (resto del código original)
        
        # Verificar tipo de datos de entrada
        if isinstance(raw_data, str):
            print("[DEBUG] Datos tipo string recibidos, convirtiendo a dict")
            raw_data = {
                'type': 'raw_string',
                'message': raw_data,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        if not isinstance(raw_data, dict):
            print("[DEBUG] Tipo inesperado, convirtiendo a dict genérico")
            raw_data = {
                'type': 'unknown',
                'message': str(raw_data),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        current_time = datetime.now()
        
        # Verificar duplicados recientes solo para escaneos RFID reales
        if raw_data.get('type') == 'rfid_scan' and self._is_duplicate_scan(current_time):
            raise Exception("Escaneo duplicado detectado")
        
        self.last_scan_time = current_time
        
        # Extraer información del mensaje del protocolo
        data_type = raw_data.get('type', 'unknown')
        print(f"[DEBUG] Tipo de datos determinado: {data_type}")
        
        if data_type == 'rfid_scan':
            print("[DEBUG] Procesando como rfid_scan")
            result = self._process_rfid_scan(raw_data, current_time)
        elif data_type in ['info', 'confirmation', 'acknowledgment', 'authentication']:
            print("[DEBUG] Procesando como mensaje del sistema")
            result = self._process_system_message(raw_data, current_time)
        elif data_type == 'raw_string':
            print("[DEBUG] Procesando como string crudo")
            result = self._process_raw_string(raw_data, current_time)
        else:
            print("[DEBUG] Procesando como mensaje genérico")
            result = self._process_generic_message(raw_data, current_time)
        
        print(f"[DEBUG] Resultado final: {result}")
        print(f"[DEBUG] Tipo resultado: {result.get('type')}")
        return result
    
    def _process_rfid_scan(self, data: Dict[str, Any], scan_time: datetime) -> Dict[str, Any]:
        """Procesa un escaneo RFID específico"""
        print("[DEBUG] === _process_rfid_scan VERSIÓN NUEVA ===")
        print(f"[DEBUG] data recibida: {data}")
        
        card_id = data.get('card_id', 'Unknown')
        card_hash = data.get('card_hash', '')
        name = data.get('name', f'Usuario {card_id}')
        info = data.get('info', 'Tarjeta escaneada')
        
        print(f"[DEBUG] Datos extraídos - card_id: {card_id}, card_hash: {card_hash}")
        
        # Buscar información adicional de la tarjeta si es necesario
        enhanced_info = self._enhance_card_info(card_id, card_hash)
        
        result = {
            'type': 'rfid_scan',  # ¡IMPORTANTE! Mantener el tipo
            'card_id': card_id,
            'card_hash': card_hash,
            'name': enhanced_info.get('name', name),
            'info': enhanced_info.get('info', info),
            'timestamp': scan_time.strftime("%Y-%m-%d %H:%M:%S"),
            'message_type': data.get('message_type', 'OK'),
            'auth_verified': bool(data.get('auth', '')),
            'raw_data': data
        }
        
        print(f"[DEBUG] ✅ Resultado _process_rfid_scan: {result}")
        print(f"[DEBUG] ✅ Tipo establecido: {result.get('type')}")
        return result
    
    def _process_system_message(self, data: Dict[str, Any], scan_time: datetime) -> Dict[str, Any]:
        """Procesa mensajes del sistema"""
        message_type = data.get('type', 'system')
        message = data.get('message', 'Mensaje del sistema')
        
        return {
            'type': 'system_message',  # Tipo específico para sistema
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
            'type': 'raw_data',  # Tipo específico para datos crudos
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
        print("[DEBUG] === _process_generic_message ===")
        print(f"[DEBUG] data: {data}")
        
        # Intentar extraer información útil del diccionario
        card_id = 'GENERIC'
        name = 'Mensaje genérico'
        info = 'Datos procesados'
        
        # Buscar campos conocidos
        if 'card_id' in data:
            card_id = str(data['card_id'])
        if 'name' in data:
            name = str(data['name'])
        if 'message' in data:
            info = str(data['message'])
        elif 'data' in data:
            info = str(data['data'])
        
        result = {
            'type': 'generic_message',  # Tipo específico para genéricos
            'card_id': card_id,
            'card_hash': data.get('card_hash', ''),
            'name': name,
            'info': info,
            'timestamp': scan_time.strftime("%Y-%m-%d %H:%M:%S"),
            'message_type': data.get('message_type', 'UNKNOWN'),
            'auth_verified': bool(data.get('auth', '')),
            'raw_data': data
        }
        
        print(f"[DEBUG] Resultado _process_generic_message: {result}")
        return result
    
    def _enhance_card_info(self, card_id: str, card_hash: str) -> Dict[str, str]:
        """
        Mejora la información de la tarjeta consultando fuentes adicionales
        """
        # Base de datos simulada de tarjetas conocidas
        known_cards = {
            'D52D74FE': {
                'name': 'Juan Pérez',
                'info': 'Empleado - Departamento IT'
            },
            'A1B2C3D4': {
                'name': 'María García',
                'info': 'Administradora - RR.HH.'
            },
        }
        
        # Buscar por card_id o por los últimos 8 caracteres del hash
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
    
    def format_history_item(self, card_id: str, name: str, timestamp: str) -> str:
        """Formatea un elemento para el historial"""
        try:
            time_part = timestamp.split(' ')[1] if ' ' in timestamp else timestamp
            return f"[{time_part}] {card_id} - {name}"
        except (IndexError, AttributeError):
            return f"[??:??:??] {card_id} - {name}"
    
    def format_tooltip(self, card_id: str, name: str, timestamp: str) -> str:
        """Formatea un tooltip con información detallada"""
        return f"Tarjeta: {card_id}\nUsuario: {name}\nHora: {timestamp}"