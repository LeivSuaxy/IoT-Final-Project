"""Test directo del RFIDDataHandler"""

from core.rfid_data_handler_new import RFIDDataHandler

def test_handler():
    print("=== INICIANDO TEST ===")
    handler = RFIDDataHandler()
    
    test_data = {
        'type': 'rfid_scan', 
        'card_id': 'D52D74FE', 
        'card_hash': '339CE2C11F368BB774A772C01AF01F5E9B541C9492D1DC64C086D156D52D74FE', 
        'name': 'Usuario D52D74FE', 
        'info': 'Tarjeta escaneada - Hash: 339CE2C11F368BB7...', 
        'timestamp': '2025-06-10 23:45:29', 
        'auth': '', 
        'message_type': 'OK'
    }
    
    print("=== TEST DIRECTO ===")
    result = handler.process_rfid_data(test_data)
    print(f"Resultado tipo: {result.get('type')}")
    print(f"Resultado completo: {result}")

if __name__ == "__main__":
    test_handler()