from time import perf_counter
from functools import wraps


# Decorador para medir o tempo de execução da função
def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        result = func(*args, **kwargs)
        end_time = perf_counter()
        execution_time = end_time - start_time
        return result, execution_time

    return wrapper
