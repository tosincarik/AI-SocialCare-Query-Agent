import asyncio
from agent_config import resultagent
from agents.runner import Runner
import streamlit as st

async def test_agent():
    try:
        # Simple SQL query to test
        query = "SELECT * FROM clients LIMIT 1;"
        result = await Runner.run(resultagent, query)
        if result is None:
            return "⚠️ Agent returned None. Possible model/API issue."
        return getattr(result, "final_output", str(result))
    except Exception as e:
        return f"⚠️ Error running agent: {e}"

# Run async function safely
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
output = loop.run_until_complete(test_agent())
loop.close()

st.write("Agent output:", output)
