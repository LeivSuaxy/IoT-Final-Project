import sys
from PyQt6.QtWidgets import QApplication

from ui import RFIDInterface
from ui.user_interface import UserInterface
from ui.components import AuthDialog
from ui.styles import DARK_THEME
from core.api_client import api_client


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)

    # Autenticación
    auth_dialog = AuthDialog()
    
    if auth_dialog.exec() == AuthDialog.DialogCode.Accepted:
        user_data = auth_dialog.get_authenticated_user()
        
        # Configurar token
        if hasattr(user_data, 'token') and user_data.token:
            api_client.set_auth_token(user_data.token)
        
        # Crear interfaz según tipo de usuario
        if user_data.is_admin:
            window = RFIDInterface()
            window.user_data = user_data  # Asignar después
            window.setWindowTitle(f"{window.windowTitle()} - Admin: {user_data.username}")
        else:
            window = UserInterface(user_data)
        
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()