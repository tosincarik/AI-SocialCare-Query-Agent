import os
import sqlite3
from dotenv import load_dotenv

# Ensure local agents folder is first in path
import sys
base_dir = os.path.dirname(__file__)
sys.path.insert(0, base_dir)

from agents.agent import Agent  # explicit import
from agents.runner import Runner
from agents import trace, function_tool
import streamlit as st

# Load environment variables
load_dotenv(override=True)

# --- Database path ---
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

# --- Safe Agent1 creation ---
Agent1 = Agent(name="QueryExecutor", instructions=instruction1, model="gpt-4o-mini")
tool1 = getattr(Agent1, "as_tool", None)
if callable(tool1):
    tool1 = Agent1.as_tool(tool_name="instruct", tool_description=instruction1)
else:
    # fallback if .as_tool() missing
    tool1 = execute_sql

# --- Final agent ---
tools = [tool1, execute_sql]
resultagent = Agent(
    name="strictinstruct",
    instructions="Execute the SQL query and return a clean formatted table.",
    tools=tools,
    model="gpt-4o-mini"
)

# --- Debug output on Cloud ---
st.write("DEBUG: tool1 is", tool1)
st.write("DEBUG: resultagent tools =", tools)
