"""try / except / else / finally and custom exceptions."""


class NegativeNumberError(ValueError):
    """Raised when a negative number is not allowed."""


def safe_divide(a: float, b: float) -> float | None:
    try:
        result = a / b
    except ZeroDivisionError:
        print("  Cannot divide by zero")
        return None
    else:
        return result
    finally:
        print(f"  divide({a}, {b}) finished")


def square_root(n: float) -> float:
    if n < 0:
        raise NegativeNumberError(f"{n} is negative")
    return n ** 0.5


if __name__ == "__main__":
    print(safe_divide(10, 2))
    print(safe_divide(1, 0))

    try:
        square_root(-4)
    except NegativeNumberError as exc:
        print("Caught:", exc)

    try:
        int("abc")
    except ValueError as exc:
        print("Caught:", exc)
