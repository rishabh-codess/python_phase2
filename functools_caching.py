# functools: lru_cache, partial, and reduce
from functools import lru_cache, partial, reduce


@lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


print(fib(80))
print(fib.cache_info())

power = lambda base, exponent: base ** exponent
square = partial(power, exponent=2)
cube = partial(power, exponent=3)
print(square(6), cube(3))

print(reduce(lambda a, b: a * b, range(1, 8)))
