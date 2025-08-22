# calculator.py

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    # ❌ Bug: No check for division by zero
    return a / b

if __name__ == "__main__":
    print("Add: ", add(2, 3))
    print("Subtract: ", subtract(5, 1))
    print("Multiply: ", multiply(2, 4))
    print("Divide: ", divide(10, 0))  # ⚠️ This will crash
