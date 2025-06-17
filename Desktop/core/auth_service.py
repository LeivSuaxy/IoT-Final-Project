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
                
                # Usar los datos del usuario incluidos en la respuesta
                if 'user_data' in token_data:
                    user_info = token_data['user_data']
                    user_data = UserData(
                        id="",  # No está incluido en la respuesta
                        username=user_info['name'],  # Tu backend usa 'name'
                        email="",  # No está incluido en la respuesta
                        is_active=True,  # Asumimos que está activo ya que puede hacer login
                        is_admin=user_info['is_admin']
                    )
                    self.current_user = user_data
                    self.login_success.emit(user_data)
                    return True, "Login exitoso"
                else:
                    # Fallback en caso de que no estén los datos del usuario
                    basic_user = UserData(
                        id="",
                        username=credentials.username,
                        email="",
                        is_active=True,
                        is_admin=False
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
        Realiza registro síncrono y login automático si es exitoso
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
                
                # 🔥 REALIZAR LOGIN AUTOMÁTICO DESPUÉS DEL REGISTRO EXITOSO
                print("[DEBUG] Registro exitoso, realizando login automático...")
                
                # Crear credenciales para el login
                from .auth_models import LoginCredentials
                login_credentials = LoginCredentials(
                    username=register_data.username,
                    password=register_data.password
                )
                
                # Intentar login automático
                login_success, login_message = self.login(login_credentials)
                
                if login_success:
                    # Login automático exitoso
                    print("[DEBUG] ✅ Login automático exitoso")
                    return True, "Registro exitoso - Sesión iniciada automáticamente"
                else:
                    # Registro exitoso pero login falló
                    print(f"[WARNING] Registro exitoso pero login automático falló: {login_message}")
                    
                    # Crear user_data básico para el registro
                    user_data = UserData(
                        username=user_response.get('username', register_data.username),
                        is_admin=user_response.get('is_admin', False),
                        email=register_data.email,
                        is_active=True
                    )
                    self.register_success.emit(user_data)
                    
                    return True, f"Registro exitoso. Login manual requerido: {login_message}"
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

    def auto_login_after_register(self, register_data: RegisterData) -> Tuple[bool, str, Optional[UserData]]:
        """
        Método alternativo que devuelve también los datos del usuario
        Returns: (success: bool, message: str, user_data: Optional[UserData])
        """
        try:
            # Primero hacer el registro
            success, message = self.register(register_data)
            
            if success and self.current_user:
                # El login automático ya se hizo en register()
                return True, message, self.current_user
            elif success:
                # Registro exitoso pero sin login automático
                return True, message, None
            else:
                # Error en registro
                return False, message, None
                
        except Exception as e:
            error_msg = f"Error en registro/login automático: {str(e)}"
            return False, error_msg, None
    
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