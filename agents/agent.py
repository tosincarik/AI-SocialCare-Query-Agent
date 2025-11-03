# agents/agent.py


class Agent:
    def __init__(self, name, instructions, tools=None, model="gpt-4o-mini"):
        self.name = name
        self.instructions = instructions
        self.tools = tools or []  # default to empty list
        self.model = model

    def as_tool(self, tool_name, tool_description):
        # Register this agent as a tool
        return {
            "tool_name": tool_name,
            "tool_description": tool_description,
            "agent": self
        }


    async def run(self, message):
        # Logic for calling the LLM with instructions + tools
        # (adapt from your notebook)
        pass


def trace(name: str):
    # Decorator or context manager for logging agent runs
    def wrapper(func):
        def inner(*args, **kwargs):
            print(f"[TRACE] {name}")
            return func(*args, **kwargs)
        return inner
    return wrapper


def function_tool(func):
    # Mark a Python function as a tool available to agents
    func.is_tool = True
    return func
