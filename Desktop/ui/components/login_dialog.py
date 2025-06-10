from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QPushButton, QTabWidget, QWidget,
                             QMessageBox, QProgressBar, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from core.auth_service import AuthService
from core.auth_models import LoginCredentials, RegisterData, UserData


class AuthDialog(QDialog):
    """Diálogo de autenticación con login y registro"""
    
    # Señal emitida cuando la autenticación es exitosa
    authentication_success = pyqtSignal(UserData)
    
    def __init__(self, api_base_url: str = "http://localhost:8000", parent=None):
        super().__init__(parent)
        self.auth_service = AuthService(api_base_url)
        self.authenticated_user = None
        self._init_ui()
        self._apply_styles()
        
        # Conectar señales del servicio de autenticación
        self.auth_service.login_success.connect(self._on_login_success)
        self.auth_service.login_error.connect(self._on_login_error)
        self.auth_service.register_success.connect(self._on_register_success)
        self.auth_service.register_error.connect(self._on_register_error)
    
    def _init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("🔐 Autenticación - Sistema RFID")
        self.setModal(True)
        self.setFixedSize(500, 650)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        main_layout.addWidget(self._create_header())
        
        # Tabs para Login/Registro
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self._create_login_tab(), "🔑 Iniciar Sesión")
        self.tab_widget.addTab(self._create_register_tab(), "👤 Registrarse")
        main_layout.addWidget(self.tab_widget)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(6)
        main_layout.addWidget(self.progress_bar)
    
    def _create_header(self):
        """Crea el header del diálogo"""
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.setSpacing(10)
        
        # Título principal
        title = QLabel("🏷️ Sistema RFID")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtítulo
        subtitle = QLabel("Control de Acceso Inteligente")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Mensaje de autenticación
        auth_msg = QLabel("Ingresa tus credenciales para continuar")
        auth_msg.setFont(QFont("Segoe UI", 11))
        auth_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addWidget(auth_msg)
        
        return header_frame
    
    def _create_login_tab(self):
        """Crea la pestaña de login"""
        login_widget = QWidget()
        layout = QVBoxLayout(login_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Formulario de login
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Campo usuario
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Ingresa tu nombre de usuario")
        self.login_username.setMinimumHeight(45)
        self.login_username.setFont(QFont("Segoe UI", 11))
        form_layout.addRow("👤 Usuario:", self.login_username)
        
        # Campo contraseña
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Ingresa tu contraseña")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_password.setMinimumHeight(45)
        self.login_password.setFont(QFont("Segoe UI", 11))
        self.login_password.returnPressed.connect(self._handle_login)
        form_layout.addRow("🔒 Contraseña:", self.login_password)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Botón de login
        self.login_btn = QPushButton("🔑 Iniciar Sesión")
        self.login_btn.setMinimumHeight(50)
        self.login_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.login_btn.clicked.connect(self._handle_login)
        self.login_btn.setDefault(True)
        layout.addWidget(self.login_btn)
        
        return login_widget
    
    def _create_register_tab(self):
        """Crea la pestaña de registro"""
        register_widget = QWidget()
        layout = QVBoxLayout(register_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Formulario de registro
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Campo usuario
        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("Elige un nombre de usuario")
        self.register_username.setMinimumHeight(45)
        self.register_username.setFont(QFont("Segoe UI", 11))
        form_layout.addRow("👤 Usuario:", self.register_username)
        
        # Campo email
        self.register_email = QLineEdit()
        self.register_email.setPlaceholderText("tu@email.com")
        self.register_email.setMinimumHeight(45)
        self.register_email.setFont(QFont("Segoe UI", 11))
        form_layout.addRow("📧 Email:", self.register_email)
        
        # Campo contraseña
        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Crea una contraseña segura")
        self.register_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.register_password.setMinimumHeight(45)
        self.register_password.setFont(QFont("Segoe UI", 11))
        self.register_password.returnPressed.connect(self._handle_register)
        form_layout.addRow("🔒 Contraseña:", self.register_password)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Botón de registro
        self.register_btn = QPushButton("👤 Crear Cuenta")
        self.register_btn.setMinimumHeight(50)
        self.register_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.register_btn.clicked.connect(self._handle_register)
        layout.addWidget(self.register_btn)
        
        return register_widget
    
    def _apply_styles(self):
        """Aplica estilos al diálogo"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #1e293b,
                    stop: 1 #0f172a
                );
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
            }
            QLabel {
                color: #e2e8f0;
            }
            QLabel[text*="Sistema RFID"] {
                color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #3b82f6,
                    stop: 1 #8b5cf6
                );
            }
            QLabel[text*="Control de Acceso"] {
                color: #94a3b8;
            }
            QLabel[text*="credenciales"] {
                color: #64748b;
            }
            QTabWidget::pane {
                border: 2px solid #334155;
                border-radius: 12px;
                background: #1e293b;
            }
            QTabBar::tab {
                background: #334155;
                color: #94a3b8;
                padding: 12px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
                font-weight: 600;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background: #3b82f6;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #475569;
                color: #e2e8f0;
            }
            QLineEdit {
                background: #334155;
                color: #e2e8f0;
                border: 2px solid #475569;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background: #1e293b;
            }
            QLineEdit::placeholder {
                color: #64748b;
                font-style: italic;
            }
            QPushButton {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3b82f6,
                    stop: 1 #2563eb
                );
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2563eb,
                    stop: 1 #1d4ed8
                );
            }
            QPushButton:pressed {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #1d4ed8,
                    stop: 1 #1e3a8a
                );
            }
            QPushButton:disabled {
                background: #475569;
                color: #64748b;
            }
            QProgressBar {
                background: #334155;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #3b82f6,
                    stop: 1 #8b5cf6
                );
                border-radius: 3px;
            }
        """)
    
    def _handle_login(self):
        """Maneja el proceso de login"""
        username = self.login_username.text().strip()
        password = self.login_password.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Campos Requeridos", 
                              "Por favor completa todos los campos")
            return
        
        self._set_loading_state(True)
        credentials = LoginCredentials(username=username, password=password)
        success, message = self.auth_service.login(credentials)
        
        if not success:
            self._set_loading_state(False)
            QMessageBox.critical(self, "Error de Autenticación", message)
    
    def _handle_register(self):
        """Maneja el proceso de registro"""
        username = self.register_username.text().strip()
        email = self.register_email.text().strip()
        password = self.register_password.text()
        
        if not username or not email or not password:
            QMessageBox.warning(self, "Campos Requeridos", 
                              "Por favor completa todos los campos")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Contraseña Débil", 
                              "La contraseña debe tener al menos 6 caracteres")
            return
        
        self._set_loading_state(True)
        register_data = RegisterData(username=username, email=email, password=password)
        success, message = self.auth_service.register(register_data)
        
        if not success:
            self._set_loading_state(False)
            QMessageBox.critical(self, "Error de Registro", message)
    
    def _set_loading_state(self, loading: bool):
        """Configura el estado de carga"""
        self.login_btn.setEnabled(not loading)
        self.register_btn.setEnabled(not loading)
        self.progress_bar.setVisible(loading)
        
        if loading:
            self.progress_bar.setRange(0, 0)  # Progreso indeterminado
        else:
            self.progress_bar.setRange(0, 100)
    
    def _on_login_success(self, user_data: UserData):
        """Maneja login exitoso"""
        self._set_loading_state(False)
        self.authenticated_user = user_data
        self.authentication_success.emit(user_data)
        self.accept()
    
    def _on_login_error(self, error_message: str):
        """Maneja error en login"""
        self._set_loading_state(False)
        # El error ya se muestra en _handle_login
    
    def _on_register_success(self, user_data: UserData):
        """Maneja registro exitoso"""
        self._set_loading_state(False)
        QMessageBox.information(
            self, 
            "✅ Registro Exitoso", 
            f"Cuenta creada correctamente para {user_data.username}.\n"
            "Ahora puedes iniciar sesión."
        )
        # Cambiar a la pestaña de login
        self.tab_widget.setCurrentIndex(0)
        self.login_username.setText(user_data.username)
        self.login_password.setFocus()
    
    def _on_register_error(self, error_message: str):
        """Maneja error en registro"""
        self._set_loading_state(False)
        # El error ya se muestra en _handle_register
    
    def get_authenticated_user(self) -> UserData:
        """Retorna los datos del usuario autenticado"""
        return self.authenticated_user