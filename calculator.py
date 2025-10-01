# modified-by-module3
from flask import Flask, render_template, request

app = Flask(__name__)

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0: # modified
        return 'Cannot divide by zero' # modified
    return a / b

# Test cases for divide function # modified

import unittest # modified
from calculator import divide # modified

class TestDivideFunction(unittest.TestCase): # modified
    def test_divide_by_zero(self): # modified
        self.assertEqual(divide(10, 0), 'Cannot divide by zero') # modified

    def test_divide_by_non_zero(self): # modified
        self.assertEqual(divide(10, 2), 5.0) # modified

if __name__ == "__main__": # modified
    unittest.main() # modified

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            operation = request.form["operation"]

            if operation == "add":
                result = add(num1, num2)
            elif operation == "subtract":
                result = subtract(num1, num2)
            elif operation == "multiply":
                result = multiply(num1, num2)
            elif operation == "divide":
                result = divide(num1, num2)
        except ValueError:
            error = "Please enter valid numbers."

    return render_template("index.html", result=result, error=error)

