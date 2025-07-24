from functools import wraps
from time import perf_counter


def measure_time(func):
    """
    Decorator to measure the execution time of a function.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The wrapped function that measures execution time.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Wrapper function that measures the execution time of the decorated function.

        Args:
            *args: Variable length argument list for the decorated function.
            **kwargs: Arbitrary keyword arguments for the decorated function.

        Returns:
            tuple: A tuple containing the result of the decorated function and the execution time.
        """
        start_time = perf_counter()
        result = func(*args, **kwargs)
        end_time = perf_counter()
        execution_time = end_time - start_time
        return result, execution_time

    return wrapper