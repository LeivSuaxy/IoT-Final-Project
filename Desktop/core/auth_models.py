"""Modelos de autenticación"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class UserData:
    """Datos del usuario autenticado"""
    username: str
    is_admin: bool
    user_id: Optional[int] = None
    email: Optional[str] = None
    token: Optional[str] = None
    id: Optional[int] = None  # 🔥 AGREGAR ESTE CAMPO
    is_active: Optional[bool] = True
    
    def __post_init__(self):
        """Validaciones post-inicialización"""
        if not self.username:
            raise ValueError("Username no puede estar vacío")
        
        # Si se proporciona 'id' pero no 'user_id', usar 'id' como 'user_id'
        if self.id is not None and self.user_id is None:
            self.user_id = self.id


@dataclass
class LoginCredentials:
    """Modelo para credenciales de login"""
    username: str
    password: str


@dataclass
class RegisterData:
    """Modelo para datos de registro"""
    username: str
    email: str
    password: str