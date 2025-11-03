import os
import sqlite3
from dotenv import load_dotenv
import streamlit as st

# --- Load local .env (for local dev) ---
load_dotenv(override=True)

# --- Load OpenAI API key ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    pass

print("DEBUG: OPENAI_API_KEY present?", bool(OPENAI_API_KEY))

# --- Database path ---
db_path = os.path.join(os.path.dirname(__file__), "synthetic_socialcare2.db")
if not os.path.isfile(db_path):
    print(f"WARNING: Database not found at {db_path}")

# --- SQL tool ---
from agents import Agent, Runner, trace, function_tool

@function_tool
def execute_sql(query: str):
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

# --- Instructions ---
instruction1 = f"""
You are a SQL assistant for adult social care data.
Always generate SELECT-only SQL for the SQLite schema provided.
Return JSON: {{sql, explanation}}
Schema: {schema}
"""

# --- Create Agent ---
Agent1 = Agent(name="QueryExecutor", instructions=instruction1, model="gpt-4o-mini")

# --- Safe tool attachment ---
tool1_func = getattr(Agent1, "as_tool", None)
tool1 = tool1_func(tool_name="instruct", tool_description=instruction1) if callable(tool1_func) else execute_sql

tools = [tool1, execute_sql]

resultagent = Agent(
    name="strictinstruct",
    instructions="Execute the SQL query and return a clean formatted table.",
    tools=tools,
    model="gpt-4o-mini"
)

# --- Debug ---
print("DEBUG: resultagent tools =", tools)
print("DEBUG: DB exists?", os.path.isfile(db_path))
