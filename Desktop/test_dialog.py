"""Script de prueba para verificar que los dialogs funcionen"""

import sys
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

from ui.components.register_card_dialog import RegisterCardDialog
from ui.components.contact_admin_dialog import ContactAdminDialog
from core.auth_models import UserData

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Dialogs")
        self.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        
        # Botón para probar dialog de admin
        admin_btn = QPushButton("Probar Dialog Admin")
        admin_btn.clicked.connect(self.test_admin_dialog)
        layout.addWidget(admin_btn)
        
        # Botón para probar dialog de usuario
        user_btn = QPushButton("Probar Dialog Usuario")
        user_btn.clicked.connect(self.test_user_dialog)
        layout.addWidget(user_btn)
        
        self.setLayout(layout)
    
    def test_admin_dialog(self):
        dialog = RegisterCardDialog("123456789ABCDEF", self)
        result = dialog.exec()
        print(f"Admin dialog result: {result}")
    
    def test_user_dialog(self):
        dialog = ContactAdminDialog("123456789ABCDEF", self)
        result = dialog.exec()
        print(f"User dialog result: {result}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())