class Runner:
    @staticmethod
    async def run(agent, message):
        result = await agent.run(message)
        return result
