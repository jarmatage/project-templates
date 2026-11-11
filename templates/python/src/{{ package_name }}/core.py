"""Core functionality."""


def fibonacci(n: int) -> int:
    """Return the n-th Fibonacci number.

    Args:
        n: Zero-based position in the sequence, so ``fibonacci(0) == 0``.

    Returns:
        The n-th Fibonacci number.

    Raises:
        ValueError: If ``n`` is negative.
    """
    if n < 0:
        msg = "n must be non-negative"
        raise ValueError(msg)
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
