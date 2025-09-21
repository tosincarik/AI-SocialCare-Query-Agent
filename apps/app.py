import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # add project root

from agents import Agent, Runner, trace, function_tool


import streamlit as st
import asyncio
from agent_config import resultagent, Runner

st.title("💡 Social Care Query Agent")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask me about the social care database..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("⏳ Querying database...")

        async def run_agent():
            result = await Runner.run(resultagent, prompt)
            return result.final_output

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            output = loop.run_until_complete(run_agent())
        except Exception as e:
            output = f"⚠️ Error: {e}"
        finally:
            loop.close()

        placeholder.markdown(output)
        st.session_state["messages"].append({"role": "assistant", "content": output})
