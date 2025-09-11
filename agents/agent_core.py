import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv(override=True)  # Ensure env variables are loaded

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # now it picks up the key

class Agent:
    def __init__(self, name, instructions, model="gpt-4o-mini", tools=None):
        self.name = name
        self.instructions = instructions
        self.model = model
        self.tools = tools or []

    def as_tool(self, tool_name, tool_description):
        """Return a callable tool that wraps this agent with a real OpenAI call."""
        def tool_fn(prompt):
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.instructions},
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.choices[0].message["content"]
            # Try to parse JSON, fallback to a simple explanation if it fails
            try:
                return json.loads(content)
            except Exception:
                return {"sql": "SELECT 1", "explanation": content}
        return tool_fn
