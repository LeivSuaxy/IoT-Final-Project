"""Cliente para comunicarse con el backend FastAPI"""

import requests
import json
from typing import Optional, Dict, Any
from pathlib import Path


class APIClient:
    """Cliente para realizar peticiones al backend FastAPI"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.auth_token = None
    
    def set_auth_token(self, token: str):
        """Establece el token de autenticación"""
        print(f"[DEBUG] === set_auth_token ===")
        print(f"[DEBUG] Token recibido: {token[:20]}..." if token else "[DEBUG] Token vacío")
        
        self.auth_token = token
        if token:
            self.session.headers.update({'Authorization': f'Bearer {token}'})
            print(f"[DEBUG] ✅ Header Authorization configurado")
        else:
            # Remover header si no hay token
            self.session.headers.pop('Authorization', None)
            print(f"[DEBUG] ⚠️ Header Authorization removido")
            
        print(f"[DEBUG] Headers finales: {dict(self.session.headers)}")
    
    def get_identifier(self, rfid_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca un identificador por RFID
        
        Returns:
            Dict con datos del identificador si existe, None si no existe
        """
        print(f"[DEBUG] === APIClient.get_identifier() ===")
        print(f"[DEBUG] rfid_id: {rfid_id}")
        print(f"[DEBUG] base_url: {self.base_url}")
        print(f"[DEBUG] Headers de sesión: {dict(self.session.headers)}")
        
        try:
            url = f"{self.base_url}/identifier/{rfid_id}"
            print(f"[DEBUG] URL completa: {url}")
            
            print(f"[DEBUG] Realizando petición GET...")
            response = self.session.get(url, timeout=10)
            print(f"[DEBUG] Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"[DEBUG] ✅ Respuesta 200 - Datos: {result}")
                return result
            elif response.status_code == 404:
                print(f"[DEBUG] ❌ Respuesta 404 - Tarjeta no encontrada")
                return None
            elif response.status_code == 401:
                print(f"[ERROR] ❌ Error 401 - No autorizado. ¿Token válido?")
                print(f"[ERROR] Headers enviados: {dict(self.session.headers)}")
                raise Exception("No autorizado - Token inválido o expirado")
            else:
                print(f"[DEBUG] ⚠️ Código de estado inesperado: {response.status_code}")
                print(f"[DEBUG] Contenido de respuesta: {response.text}")
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error de conexión: {e}")
            raise Exception(f"Error de conexión al backend: {str(e)}")
    
    def create_identifier(self, rfid: str, name: str, access: bool = False, 
                         image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Crea un nuevo identificador
        
        Args:
            rfid: ID de la tarjeta RFID
            name: Nombre de la persona
            access: Si tiene acceso o no
            image_path: Ruta local a la imagen (opcional)
        
        Returns:
            Dict con datos del identificador creado
        """
        print(f"[DEBUG] === APIClient.create_identifier() ===")
        print(f"[DEBUG] rfid: {rfid}, name: {name}, access: {access}")
        print(f"[DEBUG] Headers de sesión: {dict(self.session.headers)}")
        
        try:
            url = f"{self.base_url}/identifier"
            print(f"[DEBUG] URL completa: {url}")
            
            # Preparar datos del formulario
            data = {
                'rfid': rfid,
                'name': name,
                'access': access
            }
            
            files = {}
            if image_path and Path(image_path).exists():
                files['image'] = open(image_path, 'rb')
            
            try:
                print(f"[DEBUG] Enviando petición POST...")
                response = self.session.post(url, data=data, files=files, timeout=30)
                print(f"[DEBUG] Status code: {response.status_code}")
                print(f"[DEBUG] Response headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"[DEBUG] ✅ Registro exitoso: {result}")
                    return result
                elif response.status_code == 401:
                    print(f"[ERROR] ❌ Error 401 - No autorizado")
                    print(f"[ERROR] Headers enviados: {dict(self.session.headers)}")
                    print(f"[ERROR] Response body: {response.text}")
                    raise Exception("No autorizado - Token inválido o expirado")
                else:
                    print(f"[ERROR] Error {response.status_code}: {response.text}")
                    response.raise_for_status()
                    
            finally:
                # Cerrar archivo si se abrió
                if files:
                    files['image'].close()
                    
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error de conexión: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    raise Exception(f"Error del servidor: {error_detail.get('detail', str(e))}")
                except:
                    raise Exception(f"Error del servidor: {e.response.status_code}")
            else:
                raise Exception(f"Error de conexión: {str(e)}")
    
    def test_connection(self) -> bool:
        """Prueba la conexión con el backend"""
        try:
            response = self.session.get(f"{self.base_url}/docs", timeout=5)
            return response.status_code == 200
        except:
            return False


# Instancia global del cliente
api_client = APIClient()