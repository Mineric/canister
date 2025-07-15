# fibonacci.py
# This file contains functions to calculate Fibonacci numbers using various methods.

from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci_memo(n):
    """Calculate Fibonacci number using memoization."""
    if n < 2:
        return n
    return fibonacci_memo(n-1) + fibonacci_memo(n-2)

def fibonacci_dynamic(n):
    """Calculate Fibonacci number using dynamic programming."""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    seq = [0, 1]
    for i in range(2, n):
        seq.append(seq[i-1] + seq[i-2])
    return seq

def fibonacci_generator(n):
    """Generate Fibonacci numbers up to n using a generator."""
    a, b = 0, 1
    yield a
    yield b
    for _ in range(2, n):
        a, b = b, a + b
        yield b

if __name__ == "__main__":
    import sys
    try:
        n = int(sys.argv[1])
        print(f"Fibonacci sequence up to {n} terms using dynamic programming:", fibonacci_dynamic(n))
        print(f"Fibonacci sequence up to {n} terms using generator:", list(fibonacci_generator(n)))
        print(f"Fibonacci number at position {n} using memoization:", fibonacci_memo(n))
    except (IndexError, ValueError):
        print("Usage: python fibonacci.py <number_of_terms>")
