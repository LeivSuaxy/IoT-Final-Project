from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
import requests
from core.api_client import api_client

class ImageLoaderWorker(QThread):
    """Worker para cargar imágenes desde el backend"""
    
    image_loaded = pyqtSignal(QPixmap, str)  # pixmap, name
    image_failed = pyqtSignal(str, str)      # error_msg, name
    
    def __init__(self, image_url: str, name: str):
        super().__init__()
        self.image_url = image_url
        self.name = name
    
    def run(self):
        """Descarga la imagen desde el backend"""
        try:
            # print(f"[DEBUG] Descargando imagen: {self.image_url}")
            
            headers = {}
            if hasattr(api_client, 'token') and api_client.token:
                headers['Authorization'] = f'Bearer {api_client.token}'
            
            response = requests.get(
                self.image_url,
                headers=headers,
                timeout=10,
                stream=True
            )
            
            if response.status_code == 200:
                pixmap = QPixmap()
                if pixmap.loadFromData(response.content):
                    self.image_loaded.emit(pixmap, self.name)
                else:
                    self.image_failed.emit("No se pudo procesar la imagen", self.name)
            else:
                error_msg = f"HTTP {response.status_code}: {response.reason}"
                self.image_failed.emit(error_msg, self.name)
                
        except requests.exceptions.Timeout:
            self.image_failed.emit("Timeout descargando imagen", self.name)
        except requests.exceptions.RequestException as e:
            self.image_failed.emit(f"Error de red: {str(e)}", self.name)
        except Exception as e:
            self.image_failed.emit(f"Error inesperado: {str(e)}", self.name)
