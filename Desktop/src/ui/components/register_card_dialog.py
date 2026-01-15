"""Dialog para registrar nuevas tarjetas RFID"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QCheckBox, QPushButton, QLabel, 
                             QFileDialog, QMessageBox, QFrame, QTextEdit)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path

from core.api_client import api_client


class RegisterWorker(QThread):
    """Worker para registrar tarjeta en segundo plano"""
    
    success = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, rfid, name, access, image_path):
        super().__init__()
        self.rfid = rfid
        self.name = name
        self.access = access
        self.image_path = image_path
    
    def run(self):
        print(f"[DEBUG] === RegisterWorker.run() INICIADO ===")
        print(f"[DEBUG] rfid: {self.rfid}, name: {self.name}, access: {self.access}")
        
        try:
            # Verificar si el thread fue interrumpido antes de empezar
            if self.isInterruptionRequested():
                print(f"[DEBUG] Worker interrumpido antes de empezar")
                return
            
            result = api_client.create_identifier(
                rfid=self.rfid,
                name=self.name,
                access=self.access,
                image_path=self.image_path
            )
            
            # Verificar si el thread fue interrumpido después de la petición
            if self.isInterruptionRequested():
                print(f"[DEBUG] Worker interrumpido después de la petición")
                return
            
            print(f"[DEBUG] ✅ Worker success: {result}")
            self.success.emit(result)
            
        except Exception as e:
            if not self.isInterruptionRequested():
                print(f"[DEBUG] ❌ Worker error: {e}")
                self.error.emit(str(e))
        
        print(f"[DEBUG] === RegisterWorker.run() TERMINADO ===")
    
    def stop(self):
        """Método para detener el worker de forma controlada"""
        print(f"[DEBUG] Deteniendo RegisterWorker...")
        self.requestInterruption()
        self.quit()


class RegisterCardDialog(QDialog):
    """Dialog para registrar nuevas tarjetas RFID"""
    
    def __init__(self, rfid_id: str, parent=None):
        super().__init__(parent)
        self.rfid_id = rfid_id
        self.selected_image_path = None
        self.register_worker = None
        
        self.setWindowTitle("Registrar Nueva Tarjeta")
        self.setFixedSize(500, 600)
        self.setModal(True)
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Configura la interfaz del dialog"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_layout = self._create_header()
        layout.addLayout(header_layout)
        
        # Formulario
        form_layout = self._create_form()
        layout.addLayout(form_layout)
        
        # Botones
        button_layout = self._create_buttons()
        layout.addLayout(button_layout)
    
    def _create_header(self):
        """Crea el header del dialog"""
        header_layout = QVBoxLayout()
        
        title = QLabel("🆔 Registrar Nueva Tarjeta")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #60a5fa; margin-bottom: 10px;")
        
        subtitle = QLabel(f"ID de Tarjeta: {self.rfid_id}")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #9ca3af; background: #374151; padding: 8px; border-radius: 6px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        return header_layout
    
    def _create_form(self):
        """Crea el formulario de registro"""
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Campo RFID (solo lectura)
        self.rfid_input = QLineEdit(self.rfid_id)
        self.rfid_input.setReadOnly(True)
        self.rfid_input.setStyleSheet("background: #4b5563; color: #9ca3af;")
        form_layout.addRow("🆔 RFID:", self.rfid_input)
        
        # Campo nombre
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Juan Pérez")
        form_layout.addRow("👤 Nombre completo:", self.name_input)
        
        # Campo acceso
        self.access_checkbox = QCheckBox("Permitir acceso al sistema")
        self.access_checkbox.setChecked(True)
        form_layout.addRow("🔐 Permisos:", self.access_checkbox)
        
        # Selector de imagen
        image_layout = QHBoxLayout()
        
        self.image_label = QLabel("Ninguna imagen seleccionada")
        self.image_label.setStyleSheet("color: #9ca3af; padding: 8px;")
        
        self.select_image_btn = QPushButton("📁 Seleccionar Imagen")
        self.select_image_btn.clicked.connect(self._select_image)
        
        self.clear_image_btn = QPushButton("🗑️")
        self.clear_image_btn.clicked.connect(self._clear_image)
        self.clear_image_btn.setMaximumWidth(40)
        self.clear_image_btn.setEnabled(False)
        
        image_layout.addWidget(self.image_label, 1)
        image_layout.addWidget(self.select_image_btn)
        image_layout.addWidget(self.clear_image_btn)
        
        form_layout.addRow("🖼️ Imagen:", image_layout)
        
        # Preview de imagen
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(120, 120)
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setStyleSheet("""
            border: 2px dashed #4b5563;
            border-radius: 8px;
            background: #374151;
            color: #9ca3af;
        """)
        self.image_preview.setText("Sin imagen")
        
        preview_layout = QHBoxLayout()
        preview_layout.addStretch()
        preview_layout.addWidget(self.image_preview)
        preview_layout.addStretch()
        
        form_layout.addRow("", preview_layout)
        
        return form_layout
    
    def _create_buttons(self):
        """Crea los botones del dialog"""
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("❌ Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.register_btn = QPushButton("✅ Registrar Tarjeta")
        self.register_btn.clicked.connect(self._register_card)
        self.register_btn.setDefault(True)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.register_btn)
        
        return button_layout
    
    def _select_image(self):
        """Selecciona una imagen"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Seleccionar Imagen",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.selected_image_path = file_path
            filename = Path(file_path).name
            self.image_label.setText(f"📎 {filename}")
            self.clear_image_btn.setEnabled(True)
            
            # Mostrar preview
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    120, 120, 
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_preview.setPixmap(scaled_pixmap)
    
    def _clear_image(self):
        """Limpia la imagen seleccionada"""
        self.selected_image_path = None
        self.image_label.setText("Ninguna imagen seleccionada")
        self.clear_image_btn.setEnabled(False)
        self.image_preview.clear()
        self.image_preview.setText("Sin imagen")
    
    def _register_card(self):
        """Registra la tarjeta"""
        # Validar campos
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Campo Requerido", "Por favor ingresa el nombre completo")
            self.name_input.setFocus()
            return
        
        if len(name) < 2:
            QMessageBox.warning(self, "Nombre Inválido", "El nombre debe tener al menos 2 caracteres")
            self.name_input.setFocus()
            return
        
        # Deshabilitar botón y cambiar texto
        self.register_btn.setEnabled(False)
        self.register_btn.setText("⏳ Registrando...")
        self.cancel_btn.setEnabled(False)
        
        # Crear worker para registro
        self.register_worker = RegisterWorker(
            rfid=self.rfid_id,
            name=name,
            access=self.access_checkbox.isChecked(),
            image_path=self.selected_image_path
        )
        
        self.register_worker.success.connect(self._on_register_success)
        self.register_worker.error.connect(self._on_register_error)
        self.register_worker.start()
    
    def _on_register_success(self, result):
        """Cuando el registro es exitoso"""
        print(f"[DEBUG] === _on_register_success ===")
        print(f"[DEBUG] Resultado: {result}")
        
        # 🔥 LIMPIAR EL WORKER CORRECTAMENTE
        if self.register_worker:
            self.register_worker.quit()  # Terminar el thread correctamente
            self.register_worker.wait()  # Esperar a que termine
            self.register_worker = None
            print(f"[DEBUG] Worker terminado correctamente")
        
        
        print(f"[DEBUG] Cerrando dialog con accept()")
        self.accept()  # Cerrar con código de éxito
    
    def _on_register_error(self, error_message):
        """Cuando hay error en el registro"""
        print(f"[DEBUG] === _on_register_error ===")
        print(f"[DEBUG] Error: {error_message}")
        
        # 🔥 LIMPIAR EL WORKER CORRECTAMENTE
        if self.register_worker:
            self.register_worker.quit()
            self.register_worker.wait()
            self.register_worker = None
            print(f"[DEBUG] Worker terminado correctamente")
        
        # Restaurar botones
        self.register_btn.setEnabled(True)
        self.register_btn.setText("✅ Registrar Tarjeta")
        self.cancel_btn.setEnabled(True)
        
        QMessageBox.critical(
            self,
            "❌ Error de Registro",
            f"No se pudo registrar la tarjeta:\n\n{error_message}"
        )
    
    def _apply_styles(self):
        """Aplica estilos al dialog"""
        self.setStyleSheet("""
            QDialog {
                background: #1f2937;
                color: #e5e7eb;
            }
            QLineEdit, QCheckBox {
                background: #374151;
                border: 1px solid #4b5563;
                border-radius: 6px;
                padding: 8px;
                color: #e5e7eb;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 2px solid #60a5fa;
            }
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #2563eb;
            }
            QPushButton:pressed {
                background: #1d4ed8;
            }
            QPushButton:disabled {
                background: #4b5563;
                color: #9ca3af;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                background: #374151;
                border: 1px solid #4b5563;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background: #3b82f6;
                border: 1px solid #3b82f6;
                border-radius: 3px;
            }
        """)
    
    def closeEvent(self, event):
        """Maneja el cierre del dialog"""
        print(f"[DEBUG] === RegisterCardDialog.closeEvent ===")
        
        # 🔥 MEJORAR LA LIMPIEZA DEL WORKER
        if self.register_worker and self.register_worker.isRunning():
            print(f"[DEBUG] Terminando worker en curso...")
            
            # Desconectar señales para evitar llamadas después del cierre
            try:
                self.register_worker.success.disconnect()
                self.register_worker.error.disconnect()
            except:
                pass
            
            # Terminar el worker
            self.register_worker.quit()
            if not self.register_worker.wait(3000):  # Esperar máximo 3 segundos
                print(f"[WARNING] Worker no terminó a tiempo, forzando terminación")
                self.register_worker.terminate()
                self.register_worker.wait()
            
            self.register_worker = None
            print(f"[DEBUG] Worker limpiado en closeEvent")
        
        print(f"[DEBUG] Aceptando evento de cierre")
        event.accept()