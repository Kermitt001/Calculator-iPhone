import math
from enum import Enum

class Operation(Enum):
    ADD = '+'
    SUBTRACT = '-'
    MULTIPLY = '×'
    DIVIDE = '÷'
    NONE = None

class CalculatorModel:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.current_value = "0"
        self.pending_value = None
        self.pending_operation = Operation.NONE
        self.new_entry = True  # Flag to start a new number on next digit input
        self.error_state = False

    def input_digit(self, digit: str):
        if self.error_state:
            self.reset()
            
        if self.new_entry:
            self.current_value = digit
            self.new_entry = False
        else:
            if self.current_value == "0" and digit != ".":
                self.current_value = digit
            else:
                self.current_value += digit
                
    def input_decimal(self):
        if self.error_state:
            self.reset()
            
        if self.new_entry:
            self.current_value = "0."
            self.new_entry = False
        elif "." not in self.current_value:
            self.current_value += "."
            
    def set_operation(self, op: Operation):
        if self.error_state:
            return

        if self.pending_operation != Operation.NONE and not self.new_entry:
            # Chain calculation if user presses 2 + 3 * (calculate 2+3 first)
            self.calculate()
            
        self.pending_value = float(self.current_value)
        self.pending_operation = op
        self.new_entry = True
        
    def calculate(self):
        if self.error_state or self.pending_operation == Operation.NONE or self.pending_value is None:
            return

        try:
            current = float(self.current_value)
            result = 0.0
            
            if self.pending_operation == Operation.ADD:
                result = self.pending_value + current
            elif self.pending_operation == Operation.SUBTRACT:
                result = self.pending_value - current
            elif self.pending_operation == Operation.MULTIPLY:
                result = self.pending_value * current
            elif self.pending_operation == Operation.DIVIDE:
                if current == 0:
                    self.current_value = "Error"
                    self.error_state = True
                    return
                result = self.pending_value / current
                
            # Format result to remove trailing .0 if integer
            if result.is_integer():
                self.current_value = str(int(result))
            else:
                self.current_value = str(result)
                
            self.pending_value = result # key for repeated equals logic if we wanted it
            self.pending_operation = Operation.NONE
            self.new_entry = True
            
        except Exception:
            self.current_value = "Error"
            self.error_state = True

    def toggle_sign(self):
        if self.error_state or self.current_value == "0":
            return
            
        try:
            val = float(self.current_value)
            val = -val
            if val.is_integer():
                self.current_value = str(int(val))
            else:
                self.current_value = str(val)
        except:
            self.current_value = "Error"
            self.error_state = True

    def percentage(self):
        if self.error_state:
            return
        
        try:
            val = float(self.current_value)
            val = val / 100
            if val.is_integer():
                self.current_value = str(int(val))
            else:
                self.current_value = str(val)
            self.new_entry = True
        except:
            self.current_value = "Error"
            self.error_state = True
            
    def get_display(self):
        return self.current_value
