import unittest
from src.logic import CalculatorModel, Operation

class TestCalculatorModel(unittest.TestCase):
    def setUp(self):
        self.model = CalculatorModel()

    def test_initial_state(self):
        self.assertEqual(self.model.current_value, "0")
        self.assertEqual(self.model.pending_operation, Operation.NONE)

    def test_input_digit(self):
        self.model.input_digit("1")
        self.assertEqual(self.model.current_value, "1")
        self.model.input_digit("2")
        self.assertEqual(self.model.current_value, "12")

    def test_input_decimal(self):
        self.model.input_digit("1")
        self.model.input_decimal()
        self.model.input_digit("5")
        self.assertEqual(self.model.current_value, "1.5")
        self.model.input_decimal()  # Should ignore second decimal
        self.assertEqual(self.model.current_value, "1.5")

    def test_addition(self):
        self.model.input_digit("2")
        self.model.set_operation(Operation.ADD)
        self.model.input_digit("3")
        self.model.calculate()
        self.assertEqual(self.model.current_value, "5")

    def test_subtraction(self):
        self.model.input_digit("5")
        self.model.set_operation(Operation.SUBTRACT)
        self.model.input_digit("2")
        self.model.calculate()
        self.assertEqual(self.model.current_value, "3")

    def test_multiplication(self):
        self.model.input_digit("4")
        self.model.set_operation(Operation.MULTIPLY)
        self.model.input_digit("3")
        self.model.calculate()
        self.assertEqual(self.model.current_value, "12")

    def test_division(self):
        self.model.input_digit("1")
        self.model.input_digit("0")
        self.model.set_operation(Operation.DIVIDE)
        self.model.input_digit("2")
        self.model.calculate()
        self.assertEqual(self.model.current_value, "5")

    def test_division_by_zero(self):
        self.model.input_digit("5")
        self.model.set_operation(Operation.DIVIDE)
        self.model.input_digit("0")
        self.model.calculate()
        self.assertEqual(self.model.current_value, "Error")
        self.assertTrue(self.model.error_state)

    def test_chain_operations(self):
        # 2 + 3 * 4 should be (2+3)*4 in a standard simple calculator flow or 2+(3*4) ?
        # The user requirement: "2 + 3 × 4 aplicando lógica de calculadora convencional" -> likely 2+3=5, then x4 = 20
        # Wait, "lógica de calculadora convencional" usually implies standard order of operations if it's a scientific calculator, 
        # BUT iOS calculator does NOT do order of operations in standard mode, it does immediate execution:
        # iOS: 2 + 3 * 4 = 20 (calculates 2+3=5, then 5*4=20).
        # Let's verify my implementation does immediate chain execution.
        
        self.model.input_digit("2")
        self.model.set_operation(Operation.ADD)
        self.model.input_digit("3")
        self.model.set_operation(Operation.MULTIPLY) # Should trigger 2+3=5
        self.assertEqual(self.model.current_value, "5") 
        self.model.input_digit("4")
        self.model.calculate() # 5 * 4
        self.assertEqual(self.model.current_value, "20")

    def test_toggle_sign(self):
        self.model.input_digit("5")
        self.model.toggle_sign()
        self.assertEqual(self.model.current_value, "-5")
        self.model.toggle_sign()
        self.assertEqual(self.model.current_value, "5")

    def test_percentage(self):
        self.model.input_digit("5")
        self.model.input_digit("0") # 50
        self.model.percentage()
        self.assertEqual(self.model.current_value, "0.5")

if __name__ == '__main__':
    unittest.main()
