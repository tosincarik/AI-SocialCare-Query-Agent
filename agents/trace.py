def trace(func):
    """Simple trace decorator (stub for debugging)."""
    def wrapper(*args, **kwargs):
        print(f"[TRACE] Calling {func.__name__} with {args}, {kwargs}")
        return func(*args, **kwargs)
    return wrapper
