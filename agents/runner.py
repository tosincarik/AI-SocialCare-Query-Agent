# agents/runner.py
import asyncio

class Runner:
    @staticmethod
    async def run(agent, prompt: str):
        """
        Run the agent asynchronously. Calls the first tool in agent.tools.
        Returns a Result object with final_output.
        """
        if not agent.tools or len(agent.tools) == 0:
            raise ValueError("Agent has no tools to run.")

        # Run synchronous tool in thread to avoid blocking async loop
        tool_fn = agent.tools[0]
        output = await asyncio.to_thread(tool_fn, prompt)

        class Result:
            def __init__(self, final_output):
                self.final_output = final_output

        return Result(output)
