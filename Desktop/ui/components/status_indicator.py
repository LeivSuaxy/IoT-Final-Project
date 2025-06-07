from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QRadialGradient


class StatusIndicator(QFrame):
    """Indicador visual modernizado del estado de conexión"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(35, 35)
        self.connected = False
        self._setup_animation()
        
    def _setup_animation(self):
        """Configura la animación del indicador"""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_pulse)
        self.pulse_opacity = 1.0
        self.pulse_direction = -0.1
        
    def set_status(self, connected):
        """Actualiza el estado del indicador"""
        self.connected = connected
        self._update_style()
        
        if connected:
            self.animation_timer.start(100)  # Pulso cada 100ms
        else:
            self.animation_timer.stop()
            self.pulse_opacity = 1.0
    
    def _animate_pulse(self):
        """Anima el pulso del indicador"""
        self.pulse_opacity += self.pulse_direction
        if self.pulse_opacity <= 0.3:
            self.pulse_direction = 0.1
        elif self.pulse_opacity >= 1.0:
            self.pulse_direction = -0.1
        self.update()
    
    def _update_style(self):
        """Actualiza el estilo visual según el estado"""
        if self.connected:
            self.setStyleSheet("""
                StatusIndicator {
                    background: qradialgradient(
                        cx: 0.5, cy: 0.5, radius: 0.5,
                        stop: 0 #22c55e,
                        stop: 0.7 #16a34a,
                        stop: 1 #15803d
                    );
                    border: 3px solid #dcfce7;
                    border-radius: 17px;
                }
            """)
        else:
            self.setStyleSheet("""
                StatusIndicator {
                    background: qradialgradient(
                        cx: 0.5, cy: 0.5, radius: 0.5,
                        stop: 0 #ef4444,
                        stop: 0.7 #dc2626,
                        stop: 1 #b91c1c
                    );
                    border: 3px solid #fecaca;
                    border-radius: 17px;
                }
            """)
    
    def paintEvent(self, event):
        """Dibuja el indicador con efectos especiales"""
        super().paintEvent(event)
        
        if self.connected:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Efecto de pulso
            color = QColor(34, 197, 94)
            color.setAlphaF(self.pulse_opacity * 0.3)
            
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            
            # Círculo de pulso más grande
            pulse_size = 45
            x = (self.width() - pulse_size) // 2
            y = (self.height() - pulse_size) // 2
            painter.drawEllipse(x, y, pulse_size, pulse_size)