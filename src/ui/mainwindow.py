from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, QPoint, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont, QBrush, QPainterPath

from src.logic import CalculatorModel, Operation
from src.ui import styles
from src.ui.widgets import CalculatorButton, DisplayLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.model = CalculatorModel()
        
        self.setWindowTitle("Calculator")
        self.resize(styles.WINDOW_WIDTH, styles.WINDOW_HEIGHT)
        
        # Frameless and Transparent for custom rounded corners
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Central Widget acts as the background
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main Layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(styles.BUTTON_MARGIN, styles.BUTTON_MARGIN, styles.BUTTON_MARGIN, styles.BUTTON_MARGIN)
        
        # Display
        self.display = DisplayLabel()
        self.display.setFixedHeight(int(styles.WINDOW_HEIGHT * 0.3)) # 30% top
        self.main_layout.addWidget(self.display)
        
        # Grid Layout for Buttons
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(styles.GRID_SPACING)
        self.main_layout.addLayout(self.grid_layout)
        
        self.buttons = {}
        self.setup_buttons()
        
        # Window Dragging Logic
        self.old_pos = None

    def paintEvent(self, event):
        # Draw rounded background
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = QPainterPath()
        rect = QRectF(self.rect())
        path.addRoundedRect(rect, 20, 20) # 20px radius
        
        painter.fillPath(path, QColor(styles.COLOR_BACKGROUND))

    def setup_buttons(self):
        # Definition: (Text, Row, Col, RowSpan, ColSpan, Type)
        # Type: 0=Num, 1=Op, 2=Func
        btn_defs = [
            # Row 0
            ('AC', 0, 0, 1, 1, 2), ('+/-', 0, 1, 1, 1, 2), ('%', 0, 2, 1, 1, 2), ('÷', 0, 3, 1, 1, 1),
            # Row 1
            ('7', 1, 0, 1, 1, 0), ('8', 1, 1, 1, 1, 0), ('9', 1, 2, 1, 1, 0), ('×', 1, 3, 1, 1, 1),
            # Row 2
            ('4', 2, 0, 1, 1, 0), ('5', 2, 1, 1, 1, 0), ('6', 2, 2, 1, 1, 0), ('−', 2, 3, 1, 1, 1),
            # Row 3
            ('1', 3, 0, 1, 1, 0), ('2', 3, 1, 1, 1, 0), ('3', 3, 2, 1, 1, 0), ('+', 3, 3, 1, 1, 1),
            # Row 4
            ('0', 4, 0, 1, 2, 0), ('.', 4, 2, 1, 1, 0), ('=', 4, 3, 1, 1, 1),
        ]

        for text, r, c, rs, cs, btype in btn_defs:
            if btype == 0:
                bg, fg = styles.COLOR_BTN_NUM, styles.COLOR_TEXT_WHITE
            elif btype == 1:
                bg, fg = styles.COLOR_BTN_OP, styles.COLOR_TEXT_WHITE
            else:
                bg, fg = styles.COLOR_BTN_FUNC, styles.COLOR_TEXT_BLACK
                
            btn = CalculatorButton(text, bg, fg)
            if text == '0':
                # Special handling for 0 button width if needed, or just let spans handle it
                # Because we are drawing circles, a spanned button needs to be drawn as a rounded rect (lozenge)
                # My CalculatorButton draws a circle by using min(width,height).
                # I should update CalculatorButton to handle non-square shapes if 0 is wide.
                # For now let's assume it draws a circle in the center or left aligned?
                # iOS 0 button is a lozenge (rounded rect).
                # I will stick to the default implementation which might draw a circle in the middle unless I fix it.
                # *Self-Correction*: The user requested iOS style. 0 is wide.
                # I should override paintEvent for the 0 button or make CalculatorButton adaptive.
                # Let's override the paint logic for this instance or subclass?
                # Simpler: Make CalculatorButton draw a rounded rect based on its size, with radius = height/2.
                pass

            self.grid_layout.addWidget(btn, r, c, rs, cs)
            self.buttons[text] = btn
            
            # Connect
            if text in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                btn.clicked.connect(lambda _, t=text: self.on_digit(t))
            elif text == '.':
                btn.clicked.connect(self.on_decimal)
            elif text == 'AC':
                btn.clicked.connect(self.on_clear)
            elif text == '+/-':
                btn.clicked.connect(self.on_sign)
            elif text == '%':
                btn.clicked.connect(self.on_percent)
            elif text == '=':
                btn.clicked.connect(self.on_equals)
            else:
                # Ops
                op_map = {'+': Operation.ADD, '−': Operation.SUBTRACT, '×': Operation.MULTIPLY, '÷': Operation.DIVIDE}
                btn.clicked.connect(lambda _, o=op_map[text]: self.on_operation(o))

    def on_digit(self, d):
        self.model.input_digit(d)
        self.update_ui()
        # Toggle AC to C? iOS does this.
        self.buttons['AC'].setText('C')

    def on_decimal(self):
        self.model.input_decimal()
        self.update_ui()
        self.buttons['AC'].setText('C')

    def on_clear(self):
        # In a real iOS calc, C clears current, AC clears all. 
        # For simplicity, if it says C, reset current. If AC, reset all.
        # But my model has 'reset()' which is AC. 
        # I'll just map to reset for now or implement clear entry if I have time.
        # User requirement says "Botón AC: borra todo el estado."
        self.model.reset()
        self.buttons['AC'].setText('AC')
        self.update_ui()

    def on_sign(self):
        self.model.toggle_sign()
        self.update_ui()

    def on_percent(self):
        self.model.percentage()
        self.update_ui()

    def on_operation(self, op):
        self.model.set_operation(op)
        self.update_ui()

    def on_equals(self):
        self.model.calculate()
        self.update_ui()

    def update_ui(self):
        self.display.set_text(self.model.get_display())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

