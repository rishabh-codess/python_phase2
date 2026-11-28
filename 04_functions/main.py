"""Functions: defaults, *args, **kwargs, lambda and type hints."""


def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"


def total(*args: float) -> float:
    return sum(args)


def describe(**kwargs: object) -> str:
    return ", ".join(f"{k}={v}" for k, v in kwargs.items())


square = lambda x: x * x  # noqa: E731

if __name__ == "__main__":
    print(greet("Alice"))
    print(greet("Bob", greeting="Hi"))
    print("Total:", total(1, 2, 3, 4))
    print("Describe:", describe(color="red", size=5))
    print("Square of 7:", square(7))
    print("Mapped:", list(map(square, [1, 2, 3])))
