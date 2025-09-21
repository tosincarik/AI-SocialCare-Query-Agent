# agents/runner.py

class Runner:
    @staticmethod
    async def run(agent, message):
        # Calls the agent and handles output
        result = await agent.run(message)
        return result
