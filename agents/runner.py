
# agents/runner.py
from openai import OpenAI

client = OpenAI()

class Runner:
    @staticmethod
    async def run(agent, prompt):
        """Run an agent with a prompt and return structured result."""
        response = client.chat.completions.create(
            model=agent.model,
            messages=[
                {"role": "system", "content": agent.instructions},
                {"role": "user", "content": prompt}
            ]
        )
        class Result:
            def __init__(self, final_output):
                self.final_output = final_output

        return Result(response.choices[0].message["content"])
