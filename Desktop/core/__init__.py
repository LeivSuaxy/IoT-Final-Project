"""Core components de la aplicación"""

from .socket_worker import SocketWorker
from .rfid_data_handler_new import RFIDDataHandler  # 🔥 CAMBIO AQUÍ
from .auth_models import UserData
from .api_client import api_client

__all__ = ['SocketWorker', 'RFIDDataHandler', 'UserData', 'api_client']