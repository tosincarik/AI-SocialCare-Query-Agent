import sys, os
import streamlit as st
import asyncio

# --- Ensure repo root is on Python path ---
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# --- Imports ---
from agents.runner import Runner
from agent_config import resultagent

st.title("💡 Social Care Query Agent")

# --- Debug preflight ---
st.write("DEBUG: Repo root exists?", os.path.isdir(repo_root))
st.write("DEBUG: Agents folder exists?", os.path.isdir(os.path.join(repo_root, "agents")))
st.write("DEBUG: DB exists?", os.path.isfile(os.path.join(os.path.dirname(__file__), "synthetic_socialcare2.db")))
st.write("DEBUG: OPENAI_API_KEY present?", bool(os.getenv("OPENAI_API_KEY")))

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
            try:
                result = await Runner.run(agent, prompt_text)
                if result is None:
                    return "⚠️ Agent returned no output. Check API key, model, or DB."
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
