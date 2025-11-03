import os
import openai
import asyncio
import json

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
        """Call OpenAI API, run SQL if possible, and return Markdown table."""
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            return "⚠️ OpenAI API key not found."

        # --- Step 1: Call LLM to generate SQL ---
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
        llm_output = await loop.run_in_executor(None, sync_call)

        # --- Step 2: Parse SQL ---
        sql = None
        try:
            parsed = json.loads(llm_output)
            sql = parsed.get("sql")
        except Exception:
            if "SELECT" in llm_output.upper():
                sql = llm_output.strip()

        # --- Step 3: Execute SQL ---
        if sql:
            for tool in self.tools:
                if callable(tool) and getattr(tool, "is_tool", False):
                    try:
                        results = tool(sql)
                        if isinstance(results, list) and results:
                            # Convert to Markdown table
                            headers = results[0].keys()
                            md = "| " + " | ".join(headers) + " |\n"
                            md += "| " + " | ".join("---" for _ in headers) + " |\n"
                            for row in results:
                                md += "| " + " | ".join(str(row[h]) for h in headers) + " |\n"
                            return md
                        else:
                            return "⚠️ No rows returned."
                    except Exception as e:
                        return f"⚠️ Error executing SQL: {e}"

        # --- fallback: just return LLM output ---
        return llm_output


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
