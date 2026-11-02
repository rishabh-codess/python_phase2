# Closures: functions that remember values from their enclosing scope
def make_counter(start=0):
    count = start

    def counter():
        nonlocal count
        count += 1
        return count

    return counter


def make_multiplier(factor):
    return lambda value: value * factor


counter_a = make_counter()
counter_b = make_counter(10)
print(counter_a(), counter_a(), counter_a())
print(counter_b(), counter_b())

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5), triple(5))
print([make_multiplier(n)(10) for n in range(1, 5)])
