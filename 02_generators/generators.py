# Generators: lazy sequences with yield and generator expressions
def fibonacci(limit):
    a, b = 0, 1
    while a < limit:
        yield a
        a, b = b, a + b


def read_in_chunks(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


print(list(fibonacci(100)))

for chunk in read_in_chunks(list(range(1, 11)), 3):
    print(chunk)

squares = (n * n for n in range(1, 6))
print(next(squares), next(squares))
print(sum(squares))
