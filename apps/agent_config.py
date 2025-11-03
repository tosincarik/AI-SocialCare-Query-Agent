import os
import sqlite3
import streamlit as st
from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool

# --- Load .env locally if exists ---
load_dotenv(override=True)

# --- Set OpenAI API key from Streamlit secrets ---
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
st.write("DEBUG: OPENAI_API_KEY present?", bool(os.getenv("OPENAI_API_KEY")))

# --- Database path ---
base_dir = os.path.dirname(__file__)
db_path = os.path.join(base_dir, "synthetic_socialcare2.db")
if not os.path.isfile(db_path):
    st.warning(f"Database not found at {db_path}. Queries may fail.")

# --- SQL execution tool ---
@function_tool
def execute_sql(query: str):
    """Run read-only SQL query on SQLite DB."""
    if not os.path.isfile(db_path):
        return {"error": "Database file not found."}
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
    return [dict(zip(colnames, row)) for row in rows]

# --- Schema ---
schema = {
    "clients": ["client_id", "name", "age", "gender", "postcode"],
    "assessments": ["assessment_id", "client_id", "assessment_date", "assessment_type", "assessor"],
    "services": ["service_id", "client_id", "service_name", "start_date", "end_date", "provider"],
    "outcomes": ["outcome_id", "client_id", "outcome_date", "outcome_type", "outcome_value"]
}

# --- Agent instructions ---
instruction1 = f"""
You are a SQL assistant for adult social care data.
Always generate SELECT-only SQL for the SQLite schema provided.
Return JSON: {{sql, explanation}}
Schema: {schema}
"""

# --- Safe Agent1 ---
Agent1 = Agent(name="QueryExecutor", instructions=instruction1, model="gpt-4o-mini")
tool1_func = getattr(Agent1, "as_tool", None)
if callable(tool1_func):
    tool1 = tool1_func(tool_name="instruct", tool_description=instruction1)
else:
    tool1 = execute_sql  # fallback

tools = [tool1, execute_sql]

# --- Result agent ---
resultagent = Agent(
    name="strictinstruct",
    instructions="Execute the SQL query and return a clean formatted table.",
    tools=tools,
    model="gpt-4o-mini"
)

# --- Debug ---
st.write("DEBUG: tool1 is", tool1)
st.write("DEBUG: resultagent tools =", tools)
st.write("DEBUG: DB exists?", os.path.isfile(db_path))
