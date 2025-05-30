from PyQt6.QtWidgets import QLabel


class StatusIndicator(QLabel):
    """Indicador visual del estado de conexión"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 20)
        self.connected = False
        
    def set_status(self, connected):
        """Actualiza el estado del indicador"""
        self.connected = connected
        self._update_style()
    
    def _update_style(self):
        """Actualiza el estilo visual según el estado"""
        color = "#22c55e" if self.connected else "#ef4444"
        self.setStyleSheet(f"""
            StatusIndicator {{
                background-color: {color};
                border: 2px solid #1f2937;
                border-radius: 10px;
            }}
        """)