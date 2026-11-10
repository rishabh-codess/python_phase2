"""Variables, data types and f-strings."""

name = "Alice"
age = 30
height = 1.68
is_student = False

print(f"Name: {name} ({type(name).__name__})")
print(f"Age: {age} ({type(age).__name__})")
print(f"Height: {height:.1f} m ({type(height).__name__})")
print(f"Student: {is_student} ({type(is_student).__name__})")

# Multiple assignment and swapping
a, b = 1, 2
a, b = b, a
print(f"After swap: a={a}, b={b}")
