class Runner:
    @staticmethod
    async def run(agent, prompt):
        class Result:
            final_output = f"Stubbed output from {agent.name} for: {prompt}"
        return Result()
