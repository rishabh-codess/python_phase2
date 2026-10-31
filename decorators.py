# Decorators: a timer decorator and a retry decorator with arguments
import functools
import time


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper


def retry(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except ValueError as error:
                    print(f"Attempt {attempt} failed: {error}")
            return None
        return wrapper
    return decorator


@timer
def slow_sum(n):
    return sum(range(n))


calls = {"count": 0}


@retry(times=3)
def flaky():
    calls["count"] += 1
    if calls["count"] < 3:
        raise ValueError("not ready yet")
    return "success"


print(slow_sum(1_000_000))
print(flaky())
