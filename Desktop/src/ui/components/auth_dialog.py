from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QPushButton, QTabWidget, QWidget,
                             QMessageBox, QProgressBar, QFrame, QApplication)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from core.auth_models import LoginCredentials, RegisterData, UserData
import requests
from core.auth_service import AuthService
from ..styles import (
    AUTH_DIALOG_STYLE, 
    AUTH_INPUT_STYLE, 
    AUTH_PRIMARY_BTN_STYLE, 
    AUTH_TAB_STYLE
)


class LoginWorker(QThread):
    """Worker para realizar login en segundo plano"""
    
    success = pyqtSignal(object)  # UserData object
    error = pyqtSignal(str)
    
    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password
        self.backend_url = "http://localhost:8000"  # 🔥 URL del backend
    
    def run(self):
        """Ejecuta el proceso de login"""
        try:
            print(f"[DEBUG] === LoginWorker.run() ===")
            print(f"[DEBUG] username: {self.username}")
            print(f"[DEBUG] backend_url: {self.backend_url}")
            
            # Preparar datos para el login
            login_data = {
                'username': self.username,
                'password': self.password
            }
            print(f"[DEBUG] login_data: {login_data}")
            
            # Hacer petición HTTP al backend
            print(f"[DEBUG] Enviando petición de login...")
            response = requests.post(
                f"{self.backend_url}/login",
                data=login_data,  # OAuth2PasswordRequestForm espera form data
                timeout=10
            )
            
            print(f"[DEBUG] Status code: {response.status_code}")
            print(f"[DEBUG] Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                # Login exitoso
                response_data = response.json()
                print(f"[DEBUG] 🎉 Respuesta del backend: {response_data}")
                
                # Extraer datos
                access_token = response_data.get('access_token', '')
                user_data_dict = response_data.get('user_data', {})
                
                print(f"[DEBUG] 🔑 Token recibido: {access_token[:20]}..." if access_token else "[DEBUG] ❌ No token")
                print(f"[DEBUG] 👤 User data: {user_data_dict}")
                
                # Crear UserData con token real
                user_data = UserData(
                    username=user_data_dict.get('name', self.username),
                    is_admin=user_data_dict.get('is_admin', False),
                    user_id=user_data_dict.get('id'),
                    email=user_data_dict.get('email'),
                    token=access_token  # 🔥 TOKEN REAL DEL BACKEND
                )
                
                print(f"[DEBUG] ✅ UserData creado:")
                print(f"[DEBUG] - username: {user_data.username}")
                print(f"[DEBUG] - is_admin: {user_data.is_admin}")
                print(f"[DEBUG] - token: {user_data.token[:20]}..." if user_data.token else "[DEBUG] - Sin token")
                print(f"[DEBUG] - token completo: {user_data.token}")  # Para debugging
                
                self.success.emit(user_data)
                
            elif response.status_code == 401:
                print(f"[DEBUG] ❌ Login fallido - credenciales incorrectas")
                self.error.emit("Credenciales incorrectas")
            else:
                print(f"[DEBUG] ❌ Error inesperado: {response.status_code}")
                print(f"[DEBUG] Response body: {response.text}")
                self.error.emit(f"Error del servidor: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error de conexión: {e}")
            self.error.emit(f"Error de conexión al servidor: {str(e)}")
        except Exception as e:
            print(f"[ERROR] Error inesperado en LoginWorker: {e}")
            import traceback
            traceback.print_exc()
            self.error.emit(f"Error inesperado: {str(e)}")


class AuthDialog(QDialog):
    """Diálogo de autenticación con login y registro"""
    
    # Señal emitida cuando la autenticación es exitosa
    authentication_success = pyqtSignal(UserData)
    
    def __init__(self, api_base_url: str = "http://localhost:8000", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Autenticación")
        self.setModal(True)
        
        # 🔥 INICIALIZAR EL SERVICIO DE AUTENTICACIÓN
        self.auth_service = AuthService()
        
        # Datos de usuario autenticado
        self.authenticated_user = None
        
        self._init_ui()
        self._apply_styles()
        
        # 🔥 COMENTAR ESTAS CONEXIONES DEL AUTH_SERVICE
        # self.auth_service.login_success.connect(self._on_login_success)
        # self.auth_service.login_error.connect(self._on_login_error)
        # self.auth_service.register_success.connect(self._on_register_success)
        # self.auth_service.register_error.connect(self._on_register_error)
    
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
        title.setObjectName("Title")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtítulo
        subtitle = QLabel("Control de Acceso Inteligente")
        subtitle.setObjectName("Subtitle")
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
        """Aplica estilos al diálogo usando las constantes centralizadas"""
        # Combinar todos los estilos
        combined_style = "\n".join([
            AUTH_DIALOG_STYLE,
            AUTH_INPUT_STYLE,
            AUTH_PRIMARY_BTN_STYLE,
            AUTH_TAB_STYLE
        ])
        
        self.setStyleSheet(combined_style)
        
        # Ajustes adicionales para la barra de progreso
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: #1e1e1e;
                border: none;
                border-radius: 3px;
                height: 6px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #7c3aed,
                    stop: 1 #6d28d9
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
        
        print("[DEBUG] === _handle_login ===")
        print(f"[DEBUG] username: {username}")
        
        self._set_loading_state(True)
        
        # 🔥 USAR LOGINWORKER EN LUGAR DE AUTH_SERVICE
        self.login_worker = LoginWorker(username, password)
        self.login_worker.success.connect(self._on_login_success)
        self.login_worker.error.connect(self._on_login_worker_error)
        self.login_worker.start()
        
        print("[DEBUG] LoginWorker iniciado...")
    
    def _on_login_worker_error(self, error_message: str):
        """Maneja errores del LoginWorker"""
        print(f"[DEBUG] Error en LoginWorker: {error_message}")
        self._set_loading_state(False)
        QMessageBox.critical(self, "Error de Autenticación", error_message)
    
    def _handle_register(self):
        """Maneja el registro de usuario con login automático"""
        try:
            # Verificaciones básicas
            username = self.register_username.text().strip()
            password = self.register_password.text()
            email = self.register_email.text().strip()
            
            # Validaciones básicas
            if not (username and password and email):
                self.show_error("Todos los campos son obligatorios")
                return
            
            if len(password) < 6:
                self.show_error("La contraseña debe tener al menos 6 caracteres")
                return
            
            # Crear datos para registro
            from core.auth_models import RegisterData
            register_data = RegisterData(
                username=username,
                password=password,
                email=email,
            )
            
            # Mostrar spinner o deshabilitar botón mientras procesa
            self.register_btn.setText("Registrando...")
            self.register_btn.setEnabled(False)
            QApplication.processEvents()  # Actualizar UI
            
            # 🔥 USAR EL SERVICIO DE AUTENTICACIÓN CON LOGIN AUTOMÁTICO
            success, message = self.auth_service.register(register_data)
            
            # Restaurar botón
            self.register_btn.setText("Registrarse")
            self.register_btn.setEnabled(True)
            
            if success:
                # 🔥 VERIFICAR SI HAY USUARIO AUTENTICADO (LOGIN AUTOMÁTICO)
                if self.auth_service.is_authenticated():
                    # Login automático exitoso - cerrar diálogo
                    self.authenticated_user = self.auth_service.current_user
                    QMessageBox.information(
                        self, 
                        "Registro Exitoso", 
                        "¡Bienvenido! Tu cuenta ha sido creada y has iniciado sesión automáticamente."
                    )
                    self.accept()  # Cerrar diálogo con éxito
                else:
                    # Registro exitoso pero sin login automático
                    QMessageBox.information(
                        self, 
                        "Registro Exitoso", 
                        "Usuario registrado correctamente.\nAhora puede iniciar sesión."
                    )
                    self.auth_tabs.setCurrentIndex(0)  # Cambiar a la pestaña de login
                    
                    # Pre-llenar el campo de usuario en login
                    self.login_username.setText(username)
                    self.login_password.setFocus()
                    
                # Limpiar campos de registro
                self.register_username.clear()
                self.register_password.clear()
                self.register_email.clear()
            else:
                self.show_error(f"Error en registro: {message}")
                
        except Exception as e:
            self.register_btn.setText("Registrarse")
            self.register_btn.setEnabled(True)
            self.show_error(f"Error inesperado: {str(e)}")
            print(f"[ERROR] Excepción en registro: {e}")
            import traceback
            traceback.print_exc()

    def get_authenticated_user(self):
        """Obtiene el usuario autenticado"""
        if self.authenticated_user:
            return self.authenticated_user
        elif hasattr(self, 'auth_service') and self.auth_service.is_authenticated():
            return self.auth_service.current_user
        else:
            return None
        
    def _set_loading_state(self, loading: bool):
        """Configura el estado de carga"""
        self.login_btn.setEnabled(not loading)
        self.register_btn.setEnabled(not loading)
        self.progress_bar.setVisible(loading)
        
        if loading:
            self.progress_bar.setRange(0, 0)  # Progreso indeterminado
        else:
            self.progress_bar.setRange(0, 100)
    
    def _on_login_success(self, response_data):
        """Maneja el éxito del login"""
        print(f"[DEBUG] Login exitoso - Datos: {response_data}")
        print(f"[DEBUG] Tipo de response_data: {type(response_data)}")
        
        # Ahora response_data siempre debería ser UserData
        if isinstance(response_data, UserData):
            print("[DEBUG] ✅ UserData recibido correctamente")
            self.authenticated_user = response_data
            
            print("[DEBUG] ✅ UserData final:")
            print(f"[DEBUG] - username: {self.authenticated_user.username}")
            print(f"[DEBUG] - is_admin: {self.authenticated_user.is_admin}")
            print(f"[DEBUG] - token presente: {bool(self.authenticated_user.token)}")
            print(f"[DEBUG] - token: {self.authenticated_user.token[:20]}..." if self.authenticated_user.token else "[DEBUG] Sin token")
            
        else:
            print(f"[ERROR] Tipo de datos inesperado: {type(response_data)}")
            self.error.emit("Error interno: tipo de datos inesperado")
            return
        
        self._set_loading_state(False)
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
    
    def show_error(self, message: str):
        """Muestra un mensaje de error"""
        QMessageBox.critical(self, "Error", message)