# agents/agent_core.py
import json
from openai import OpenAI

client = OpenAI()

class Agent:
    """
    Agent wraps instructions + model and exposes as_tool() which returns a callable.
    The returned callable takes a natural-language prompt and returns a Python dict
    (parsed JSON) expected to contain at least "sql" and "explanation".
    """
    def __init__(self, name, instructions, model="gpt-4o-mini", tools=None):
        self.name = name
        self.instructions = instructions
        self.model = model
        self.tools = tools or []

    def as_tool(self, tool_name: str, tool_description: str):
        """
        Returns a function that, when called with a prompt string, queries OpenAI
        and returns a Python dict parsed from the model output.

        The model is instructed to return strict JSON (see your app's instructions).
        We attempt json.loads() and fall back to a safe stub object if parsing fails.
        """
        def tool_fn(prompt: str):
            # Build messages: system contains the tool description/instructions
            messages = [
                {"role": "system", "content": tool_description},
                {"role": "user", "content": prompt}
            ]
            # Call OpenAI synchronously (OpenAI Python client is sync here)
            response = client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            content = response.choices[0].message["content"]
            # Try to parse JSON
            try:
                parsed = json.loads(content)
                if isinstance(parsed, dict):
                    return parsed
                # if parsed but not dict, wrap
                return {"sql": "", "explanation": str(parsed)}
            except Exception:
                # Fallback: return a safe stub (so the app doesn't break)
                return {"sql": "", "explanation": content}
        # annotate tool for caller (optional)
        tool_fn._is_agent_tool = True
        return tool_fn
