import os
import openai

class Agent:
    def __init__(self, name, instructions, tools=None, model="gpt-4o-mini"):
        self.name = name
        self.instructions = instructions
        self.tools = tools or []
        self.model = model

    def as_tool(self, tool_name, tool_description):
        return {
            "tool_name": tool_name,
            "tool_description": tool_description,
            "agent": self
        }

    async def run(self, message):
        """Call OpenAI API asynchronously"""
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            return "⚠️ OpenAI API key not found."

        # Minimal async wrapper
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.instructions},
                    {"role": "user", "content": message}
                ]
            )
        )
        return response.choices[0].message.content

# --- Helpers ---
def trace(name: str):
    def wrapper(func):
        def inner(*args, **kwargs):
            print(f"[TRACE] {name}")
            return func(*args, **kwargs)
        return inner
    return wrapper

def function_tool(func):
    func.is_tool = True
    return func
