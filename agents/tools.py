# agents/tools.py
from functools import wraps

def function_tool(func):
    """
    Decorator marking a function as an agent tool (no-op behavior).
    Keeps the function callable and adds an attribute so Runner/Agent can inspect if desired.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper._is_tool = True
    return wrapper
