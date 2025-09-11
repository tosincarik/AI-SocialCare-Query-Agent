# agents/trace.py
def trace(func):
    """Simple trace decorator for debugging calls during development."""
    def wrapper(*args, **kwargs):
        try:
            name = getattr(func, "__name__", str(func))
        except Exception:
            name = str(func)
        print(f"[TRACE] Calling {name} args={args} kwargs={kwargs}")
        return func(*args, **kwargs)
    return wrapper
