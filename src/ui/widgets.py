from PyQt6.QtWidgets import QPushButton, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtProperty, QRectF, QPoint, QEasingCurve, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont, QBrush, QPen
from src.ui import styles

class CalculatorButton(QPushButton):
    def __init__(self, text, bg_color, text_color, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(styles.BUTTON_SIZE, styles.BUTTON_SIZE)
        
        # Colors
        self.normal_bg = QColor(bg_color)
        self.text_color = QColor(text_color)
        self.pressed_bg = self.normal_bg.lighter(120) if bg_color != styles.COLOR_TEXT_WHITE else QColor("#D0D0D0")
        
        self.current_bg = self.normal_bg
        self._scale_factor = 1.0
        
        # Font
        font = QFont(styles.FONT_FAMILY)
        font.setPixelSize(styles.FONT_SIZE_BUTTON)
        self.setFont(font)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    @pyqtProperty(float)
    def scale_factor(self):
        return self._scale_factor

    @scale_factor.setter
    def scale_factor(self, value):
        self._scale_factor = value
        self.update()

    def hitButton(self, pos: QPoint):
        # Circular hit detection - optional, but nice
        center = self.rect().center()
        radius = self.width() / 2
        dx = pos.x() - center.x()
        dy = pos.y() - center.y()
        return (dx*dx + dy*dy) <= (radius*radius)

    def mousePressEvent(self, event):
        self.current_bg = self.pressed_bg
        
        # Scale animation (shrink)
        self.anim = QPropertyAnimation(self, b"scale_factor")
        self.anim.setDuration(100)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.95)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.anim.start()
        
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.current_bg = self.normal_bg
        
        # Scale animation (restore)
        self.anim = QPropertyAnimation(self, b"scale_factor")
        self.anim.setDuration(300)
        self.anim.setStartValue(self._scale_factor)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutElastic) # Gentle bounce
        self.anim.start()
        
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw Background
        painter.setBrush(QBrush(self.current_bg))
        painter.setPen(Qt.PenStyle.NoPen)
        
        # If width > height (like the 0 button), draw a lozenge (rounded rect with radius = height/2)
        # Otherwise draw a circle
        
        if self.width() > self.height() * 1.2: # slight tolerance
             # Calculate scaled rect for lozenge
            w = self.width() * self._scale_factor
            h = self.height() * self._scale_factor
            x_off = (self.width() - w) / 2
            y_off = (self.height() - h) / 2
            rect = QRectF(x_off, y_off, w, h)
            radius = h / 2
            painter.drawRoundedRect(rect, radius, radius)
            
            # Text alignment adjustment if needed
            # For 0 button in iOS, text is left aligned with some padding? 
            # Actually usually it's still centered or slightly left. 
            # Let's keep it centered for simplicity unless it looks bad.
            # *Correction*: iOS 0 is left aligned. Let's try to align it left if it's wide.
            painter.setPen(self.text_color)
            painter.setFont(self.font())
            alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            # Add padding for left alignment
            text_rect = QRectF(rect.left() + radius, rect.top(), rect.width() - radius, rect.height())
            painter.drawText(text_rect, alignment, self.text())
            
        else:
            # Circle
            size = min(self.width(), self.height()) * self._scale_factor
            offset_x = (self.width() - size) / 2
            offset_y = (self.height() - size) / 2
            rect = QRectF(offset_x, offset_y, size, size)
            painter.drawEllipse(rect)
        
            # Draw Text Centered
            painter.setPen(self.text_color)
            painter.setFont(self.font())
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())


from PyQt6.QtWidgets import QGraphicsOpacityEffect

class DisplayLabel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 20, 10) # Right margin
        self.layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        
        self.main_label = QLabel("0")
        self.main_label.setStyleSheet(f"color: {styles.COLOR_TEXT_WHITE};")
        font = QFont(styles.FONT_FAMILY)
        font.setPixelSize(styles.FONT_SIZE_DISPLAY_MAIN)
        font.setWeight(QFont.Weight.Thin)
        self.main_label.setFont(font)
        self.main_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        
        # Opacity Effect for Animation
        self.eff = QGraphicsOpacityEffect(self.main_label)
        self.main_label.setGraphicsEffect(self.eff)
        
        self.layout.addWidget(self.main_label)
        
    def set_text(self, text):
        if self.main_label.text() == text:
            return
            
        # Fade Out
        self.anim_out = QPropertyAnimation(self.eff, b"opacity")
        self.anim_out.setDuration(50)
        self.anim_out.setStartValue(1.0)
        self.anim_out.setEndValue(0.0)
        self.anim_out.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.anim_out.finished.connect(lambda: self._update_text_and_fade_in(text))
        self.anim_out.start()
        
    def _update_text_and_fade_in(self, text):
        self.main_label.setText(text)
        # Fade In
        self.anim_in = QPropertyAnimation(self.eff, b"opacity")
        self.anim_in.setDuration(150)
        self.anim_in.setStartValue(0.0)
        self.anim_in.setEndValue(1.0)
        self.anim_in.setEasingCurve(QEasingCurve.Type.InQuad)
        self.anim_in.start()
