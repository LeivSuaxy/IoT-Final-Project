"""Manejador de datos RFID"""

from datetime import datetime
from utils.constants import MAX_HISTORY_ITEMS


class RFIDDataHandler:
    """Manejador para procesar y formatear datos RFID"""
    
    @staticmethod
    def process_rfid_data(data):
        """Procesa los datos RFID recibidos"""
        return {
            'card_id': data.get('card_id', 'ID Desconocido'),
            'name': data.get('name', 'Persona Desconocida'),
            'info': data.get('info', {}),
            'timestamp': datetime.now()
        }
    
    @staticmethod
    def format_history_item(card_id, name, timestamp):
        """Formatea un elemento para el historial"""
        time_str = timestamp.strftime('%H:%M:%S')
        return f"[{time_str}] 🏷️ {card_id} - 👤 {name}"
    
    @staticmethod
    def format_tooltip(card_id, name, timestamp):
        """Formatea el tooltip para elementos del historial"""
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return f"Tarjeta: {card_id}\nPersona: {name}\nHora: {timestamp_str}"