# agents/agent_core.py
import os
import json
from openai import OpenAI

# Initialize OpenAI client with explicit API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Agent:
    def __init__(self, name, instructions, model="gpt-4o-mini", tools=None):
        self.name = name
        self.instructions = instructions
        self.model = model
        self.tools = tools or []

    def as_tool(self, tool_name: str, tool_description: str):
        """
        Return a callable tool that wraps this agent.
        The tool sends the prompt to OpenAI and returns structured JSON.
        """
        def tool_fn(prompt: str):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.instructions},
                        {"role": "user", "content": prompt}
                    ]
                )
                content = response.choices[0].message["content"]
                print(f"[DEBUG] OpenAI response: {content}")  # Debug output
                # Try parsing JSON
                try:
                    parsed = json.loads(content)
                    return parsed
                except json.JSONDecodeError:
                    # Fallback: return explanation as content
                    return {"sql": "", "explanation": content}
            except Exception as e:
                # Fallback for any API errors
                print(f"[ERROR] Agent tool failed: {e}")
                return {"sql": "", "explanation": f"Agent error: {e}"}
        return tool_fn
