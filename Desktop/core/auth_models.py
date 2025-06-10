from dataclasses import dataclass
from typing import Optional


@dataclass
class UserData:
    """Modelo para datos del usuario autenticado"""
    id: str
    username: str
    email: str
    is_active: bool
    is_admin: bool


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