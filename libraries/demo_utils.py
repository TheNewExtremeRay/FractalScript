"""
demo_utils.py — Example EzCode Library

This library demonstrates how to write functions that EzCode scripts
can call via `call(Lib[demo_utils] {FunctionName, args...})`.

Library functions are plain Python — they can:
  - Accept any number of arguments
  - Return values (results are not yet captured in EzCode, but useful for debugging)
  - Use Python's full standard library
  - Import and interact with the engine's globals (grid, variables, etc.)
"""

import math


def greet(name: str) -> str:
    """Return a greeting. Useful for testing library calls from EzCode."""
    msg = f"Hello, {name}! Welcome to EzCode libraries."
    print(f"[LIB:demo_utils] {msg}")
    return msg


def add(a, b):
    """Add two numbers and print the result."""
    result = a + b
    print(f"[LIB:demo_utils] {a} + {b} = {result}")
    return result


def multiply(a, b):
    """Multiply two numbers and print the result."""
    result = a * b
    print(f"[LIB:demo_utils] {a} × {b} = {result}")
    return result


def circle_area(radius: float) -> float:
    """Calculate the area of a circle."""
    area = math.pi * radius * radius
    print(f"[LIB:demo_utils] circle_area({radius}) = {area:.2f}")
    return area


def roll_dice(sides: int = 6) -> int:
    """Simulate rolling a die with the given number of sides."""
    import random
    result = random.randint(1, sides)
    print(f"[LIB:demo_utils] rolled d{sides} = {result}")
    return result
