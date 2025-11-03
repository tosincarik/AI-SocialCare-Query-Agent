import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # Ensure repo root is on path

from agents.runner import Runner
from agent_config import resultagent

import streamlit as st
import asyncio

st.title("💡 Social Care Query Agent")

# --- Initialize chat session ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat input ---
if prompt := st.chat_input("Ask me about the social care database..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("⏳ Querying database...")

        async def run_agent_safe(agent, prompt_text):
            """Run agent safely and return string output."""
            try:
                result = await Runner.run(agent, prompt_text)
                # If the agent returned None, fallback message
                if result is None:
                    return "⚠️ Agent returned no output. Check API key, model, or DB."
                # Use final_output if present, else str(result)
                return getattr(result, "final_output", str(result))
            except Exception as e:
                return f"⚠️ Error running agent: {e}"

        # Run in asyncio loop
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            output = loop.run_until_complete(run_agent_safe(resultagent, prompt))
        finally:
            loop.close()

        placeholder.markdown(output)
        st.session_state["messages"].append({"role": "assistant", "content": output})
