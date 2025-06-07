from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QPushButton, QCheckBox, 
                             QMessageBox, QGroupBox, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import requests
import json


class RegisterWorker(QThread):
    """Worker thread para el registro de tarjetas"""
    success = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, api_url, rfid_data):
        super().__init__()
        self.api_url = api_url
        self.rfid_data = rfid_data
    
    def run(self):
        try:
            response = requests.post(
                f"{self.api_url}/identifier",
                json=self.rfid_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                self.success.emit(response.json())
            else:
                error_detail = response.json().get('detail', 'Error desconocido')
                self.error.emit(f"Error {response.status_code}: {error_detail}")
                
        except requests.exceptions.ConnectionError:
            self.error.emit("No se pudo conectar con el servidor API")
        except requests.exceptions.Timeout:
            self.error.emit("Tiempo de espera agotado")
        except Exception as e:
            self.error.emit(f"Error inesperado: {str(e)}")


class RegisterDialog(QDialog):
    """Diálogo para registrar nuevas tarjetas RFID"""
    
    def __init__(self, parent=None, api_base_url="http://localhost:8000"):
        super().__init__(parent)
        self.api_base_url = api_base_url
        self.register_worker = None
        self._init_ui()
    
    def _apply_styles(self):
        """Aplica estilos mejorados al diálogo"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
            }
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                border: 2px solid #404040;
                border-radius: 12px;
                margin: 15px 0;
                padding-top: 20px;
                background-color: #2a2a2a;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 5px 12px;
                color: #ffffff;
                background-color: #3b82f6;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
            }
            QLabel {
                color: #e5e7eb;
                font-weight: 500;
                font-size: 13px;
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
            }
            QLineEdit {
                padding: 14px 16px;
                border: 2px solid #404040;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 400;
                background-color: #333333;
                color: #ffffff;
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
                selection-background-color: #3b82f6;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background-color: #383838;
                outline: none;
            }
            QLineEdit::placeholder {
                color: #9ca3af;
                font-style: italic;
            }
            QCheckBox {
                font-size: 14px;
                font-weight: 500;
                color: #e5e7eb;
                spacing: 12px;
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #6b7280;
                background-color: #374151;
            }
            QCheckBox::indicator:hover {
                border-color: #3b82f6;
                background-color: #4b5563;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #3b82f6;
                background-color: #3b82f6;
                image: none;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #2563eb;
                border-color: #2563eb;
            }
            QCheckBox::indicator:checked::after {
                content: "✓";
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton {
                font-weight: 600;
                font-size: 14px;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
                min-width: 120px;
            }
            QPushButton[text*="Registrar"] {
                background-color: #10b981;
                color: white;
            }
            QPushButton[text*="Registrar"]:hover {
                background-color: #059669;
            }
            QPushButton[text*="Registrar"]:pressed {
                background-color: #047857;
            }
            QPushButton[text*="Cancelar"] {
                background-color: #ef4444;
                color: white;
            }
            QPushButton[text*="Cancelar"]:hover {
                background-color: #dc2626;
            }
            QPushButton[text*="Cancelar"]:pressed {
                background-color: #b91c1c;
            }
            QPushButton[text*="Escanear"] {
                background-color: #3b82f6;
                color: white;
            }
            QPushButton[text*="Escanear"]:hover {
                background-color: #2563eb;
            }
            QPushButton[text*="Escanear"]:pressed {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #4b5563;
                color: #9ca3af;
            }
            QProgressBar {
                background-color: #374151;
                border: none;
                border-radius: 6px;
                text-align: center;
                font-weight: 600;
                color: #ffffff;
                height: 12px;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 6px;
            }
        """)

    def _create_header(self):
        """Crea el header mejorado del diálogo"""
        header = QLabel("🏷️ Registrar Nueva Tarjeta RFID")
        header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                color: #ffffff;
                padding: 20px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #3b82f6,
                    stop: 1 #6366f1
                );
                border-radius: 12px;
                font-weight: 700;
                letter-spacing: 0.5px;
                margin: 5px;
            }
        """)
        return header

    def _create_form_group(self):
        """Crea el grupo del formulario con mejor tipografía"""
        form_group = QGroupBox("📝 Información de la Tarjeta")
        form_group.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(18)
        form_layout.setContentsMargins(25, 25, 25, 20)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # Campo RFID con etiqueta mejorada
        rfid_label = QLabel("🏷️ ID de Tarjeta RFID:")
        rfid_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium))
        self.rfid_input = QLineEdit()
        self.rfid_input.setPlaceholderText("Ejemplo: A1B2C3D4E5F6")
        self.rfid_input.setMaxLength(50)
        self.rfid_input.setFont(QFont("Segoe UI", 13))
        form_layout.addRow(rfid_label, self.rfid_input)
        
        # Campo Nombre con etiqueta mejorada
        name_label = QLabel("👤 Nombre del Usuario:")
        name_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ejemplo: Juan Pérez González")
        self.name_input.setMaxLength(100)
        self.name_input.setFont(QFont("Segoe UI", 13))
        form_layout.addRow(name_label, self.name_input)
        
        # Checkbox de acceso con mejor estilo
        permissions_label = QLabel("🔐 Permisos de Acceso:")
        permissions_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium))
        self.access_checkbox = QCheckBox("Permitir acceso automáticamente al sistema")
        self.access_checkbox.setChecked(True)
        self.access_checkbox.setFont(QFont("Segoe UI", 13))
        form_layout.addRow(permissions_label, self.access_checkbox)
        
        # Información adicional con mejor diseño
        info_label = QLabel("ℹ️ Importante: La tarjeta RFID debe ser única en el sistema")
        info_label.setWordWrap(True)
        info_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Normal))
        info_label.setStyleSheet("""
            color: #60a5fa; 
            font-style: italic; 
            margin-top: 15px; 
            padding: 12px 15px;
            background-color: rgba(59, 130, 246, 0.1);
            border-radius: 8px;
            border-left: 3px solid #3b82f6;
        """)
        form_layout.addRow("", info_label)
        
        return form_group

    def _create_buttons(self):
        """Crea los botones con mejor tipografía"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Botón Cancelar
        self.cancel_btn = QPushButton("❌ Cancelar")
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.cancel_btn.clicked.connect(self.reject)
        
        # Botón Escanear
        self.scan_btn = QPushButton("📡 Escanear Tarjeta")
        self.scan_btn.setMinimumHeight(45)
        self.scan_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.scan_btn.clicked.connect(self._scan_card)
        
        # Botón Registrar
        self.register_btn = QPushButton("✅ Registrar Tarjeta")
        self.register_btn.setMinimumHeight(45)
        self.register_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.register_btn.clicked.connect(self._register_card)
        self.register_btn.setDefault(True)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.scan_btn)
        button_layout.addWidget(self.register_btn)
        
        return button_layout

    def _init_ui(self):
        """Inicializa la interfaz con mejor espaciado"""
        self.setWindowTitle("🆔 Registrar Nueva Tarjeta RFID")
        self.setModal(True)
        self.setFixedSize(650, 600)
        
        # Layout principal con mejor espaciado
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # Header
        main_layout.addWidget(self._create_header())
        
        # Formulario
        main_layout.addWidget(self._create_form_group())
        
        # Botones
        main_layout.addLayout(self._create_buttons())
        
        # Progress bar (oculta inicialmente)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(8)
        main_layout.addWidget(self.progress_bar)
        
        # Aplicar estilos
        self._apply_styles()
    
    def _validate_form(self):
        """Valida el formulario"""
        if not self.rfid_input.text().strip():
            QMessageBox.warning(self, "Campo Requerido", "Por favor ingresa el ID de la tarjeta RFID")
            self.rfid_input.setFocus()
            return False
        
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Campo Requerido", "Por favor ingresa el nombre del usuario")
            self.name_input.setFocus()
            return False
        
        if len(self.rfid_input.text().strip()) < 4:
            QMessageBox.warning(self, "ID Inválido", "El ID de la tarjeta RFID debe tener al menos 4 caracteres")
            self.rfid_input.setFocus()
            return False
        
        return True
    
    def _register_card(self):
        """Registra la tarjeta RFID"""
        if not self._validate_form():
            return
        
        # Preparar datos
        rfid_data = {
            "rfid": self.rfid_input.text().strip(),
            "name": self.name_input.text().strip(),
            "access": self.access_checkbox.isChecked()
        }
        
        # Deshabilitar botones y mostrar progreso
        self._set_loading_state(True)
        
        # Crear y ejecutar worker
        self.register_worker = RegisterWorker(self.api_base_url, rfid_data)
        self.register_worker.success.connect(self._on_register_success)
        self.register_worker.error.connect(self._on_register_error)
        self.register_worker.start()
    
    def _scan_card(self):
        """Función para escanear tarjeta (a implementar)"""
        QMessageBox.information(
            self, 
            "Función en Desarrollo", 
            "La función de escaneo automático estará disponible en una próxima versión.\n\n"
            "Por ahora, ingresa manualmente el ID de la tarjeta RFID."
        )
    
    def _set_loading_state(self, loading):
        """Configura el estado de carga"""
        self.register_btn.setEnabled(not loading)
        self.scan_btn.setEnabled(not loading)
        self.progress_bar.setVisible(loading)
        
        if loading:
            self.progress_bar.setRange(0, 0)  # Progreso indeterminado
            self.register_btn.setText("⏳ Registrando...")
        else:
            self.progress_bar.setRange(0, 100)
            self.register_btn.setText("✅ Registrar Tarjeta")
    
    def _on_register_success(self, response_data):
        """Maneja el éxito del registro"""
        self._set_loading_state(False)
        
        QMessageBox.information(
            self,
            "✅ Registro Exitoso",
            f"La tarjeta RFID ha sido registrada correctamente:\n\n"
            f"🏷️ ID: {response_data['rfid']}\n"
            f"👤 Usuario: {response_data['name']}\n"
            f"🔐 Acceso: {'Permitido' if response_data['access'] else 'Denegado'}"
        )
        
        self.accept()
    
    def _on_register_error(self, error_message):
        """Maneja errores en el registro"""
        self._set_loading_state(False)
        
        QMessageBox.critical(
            self,
            "❌ Error en el Registro",
            f"No se pudo registrar la tarjeta RFID:\n\n{error_message}"
        )
    
    def get_registered_data(self):
        """Obtiene los datos registrados (para uso externo)"""
        return {
            "rfid": self.rfid_input.text().strip(),
            "name": self.name_input.text().strip(),
            "access": self.access_checkbox.isChecked()
        }