import os
import streamlit as st

# Check if the OpenAI API key is loaded
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

st.write("OPENAI_API_KEY present?", bool(os.getenv("OPENAI_API_KEY")))
