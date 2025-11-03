import os
import openai
import asyncio

class Agent:
    def __init__(self, name, instructions, tools=None, model="gpt-4o-mini"):
        self.name = name
        self.instructions = instructions
        self.tools = tools or []
        self.model = model

    def as_tool(self, tool_name, tool_description):
        """Register agent as a callable tool"""
        return {
            "tool_name": tool_name,
            "tool_description": tool_description,
            "agent": self
        }

    async def run(self, message):
        """Call OpenAI API asynchronously using the new v1+ API"""
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            return "⚠️ OpenAI API key not found."

        def sync_call():
            try:
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.instructions},
                        {"role": "user", "content": message}
                    ],
                    temperature=0
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"⚠️ OpenAI API error: {e}"

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, sync_call)


# --- Helpers ---
def trace(name: str):
    """Decorator to trace function calls"""
    def wrapper(func):
        def inner(*args, **kwargs):
            print(f"[TRACE] {name}")
            return func(*args, **kwargs)
        return inner
    return wrapper


def function_tool(func):
    """Mark a Python function as an agent tool"""
    func.is_tool = True
    return func
