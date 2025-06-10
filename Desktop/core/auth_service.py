import requests
import json
from typing import Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal
from .auth_models import UserData, LoginCredentials, RegisterData


class AuthService(QObject):
    """Servicio para manejar autenticación con la API"""
    
    # Señales para comunicación asíncrona
    login_success = pyqtSignal(UserData)
    login_error = pyqtSignal(str)
    register_success = pyqtSignal(UserData)
    register_error = pyqtSignal(str)
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        super().__init__()
        self.api_base_url = api_base_url.rstrip('/')
        self.access_token: Optional[str] = None
        self.current_user: Optional[UserData] = None
    
    def login(self, credentials: LoginCredentials) -> Tuple[bool, str]:
        """
        Realiza login síncrono
        Returns: (success: bool, message: str)
        """
        try:
            # Preparar datos como form data para OAuth2
            form_data = {
                'username': credentials.username,
                'password': credentials.password,
            }
            
            response = requests.post(
                f"{self.api_base_url}/login",
                data=form_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                
                # Intentar obtener datos del usuario
                user_data = self._get_current_user()
                if user_data:
                    self.current_user = user_data
                    self.login_success.emit(user_data)
                    return True, "Login exitoso"
                else:
                    # Si no podemos obtener datos del usuario, crear un usuario básico
                    # con la información que tenemos
                    basic_user = UserData(
                        id="",  # No tenemos el ID
                        username=credentials.username,
                        email="",  # No tenemos el email
                        is_active=True,  # Asumimos que está activo
                        is_admin=False  # Por defecto no es admin, se puede ajustar
                    )
                    self.current_user = basic_user
                    self.login_success.emit(basic_user)
                    return True, "Login exitoso (datos limitados)"
            else:
                error_detail = response.json().get('detail', 'Error de autenticación')
                self.login_error.emit(error_detail)
                return False, error_detail
                
        except requests.exceptions.ConnectionError:
            error_msg = "No se pudo conectar con el servidor"
            self.login_error.emit(error_msg)
            return False, error_msg
        except requests.exceptions.Timeout:
            error_msg = "Tiempo de espera agotado"
            self.login_error.emit(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            self.login_error.emit(error_msg)
            return False, error_msg
    
    def register(self, register_data: RegisterData) -> Tuple[bool, str]:
        """
        Realiza registro síncrono
        Returns: (success: bool, message: str)
        """
        try:
            user_data = {
                'username': register_data.username,
                'email': register_data.email,
                'password': register_data.password
            }
            
            response = requests.post(
                f"{self.api_base_url}/register",
                json=user_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                user_response = response.json()
                user_data = UserData(
                    username=user_response['username'],
                    is_admin=user_response['is_admin']
                )
                self.register_success.emit(user_data)
                return True, "Registro exitoso"
            else:
                error_detail = response.json().get('detail', 'Error en el registro')
                self.register_error.emit(error_detail)
                return False, error_detail
                
        except requests.exceptions.ConnectionError:
            error_msg = "No se pudo conectar con el servidor"
            self.register_error.emit(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            self.register_error.emit(error_msg)
            return False, error_msg
    
    def logout(self):
        """Cierra sesión"""
        self.access_token = None
        self.current_user = None
    
    def is_authenticated(self) -> bool:
        """Verifica si el usuario está autenticado"""
        return self.access_token is not None and self.current_user is not None
    
    def is_admin(self) -> bool:
        """Verifica si el usuario actual es administrador"""
        return self.current_user is not None and self.current_user.is_admin