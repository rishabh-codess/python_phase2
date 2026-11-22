"""Classic algorithms: binary search, bubble sort, primes, factorial."""


def binary_search(items: list[int], target: int) -> int:
    low, high = 0, len(items) - 1
    while low <= high:
        mid = (low + high) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def bubble_sort(items: list[int]) -> list[int]:
    result = items[:]
    for i in range(len(result)):
        for j in range(len(result) - i - 1):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
    return result


def primes_up_to(n: int) -> list[int]:
    sieve = [True] * (n + 1)
    sieve[0:2] = [False, False]
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            for multiple in range(i * i, n + 1, i):
                sieve[multiple] = False
    return [i for i, is_prime in enumerate(sieve) if is_prime]


def factorial(n: int) -> int:
    return 1 if n <= 1 else n * factorial(n - 1)


if __name__ == "__main__":
    data = [64, 25, 12, 22, 11]
    ordered = bubble_sort(data)
    print("Sorted:", ordered)
    print("Index of 22:", binary_search(ordered, 22))
    print("Primes <= 30:", primes_up_to(30))
    print("5! =", factorial(5))
