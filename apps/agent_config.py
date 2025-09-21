import sqlite3, os
from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool


base_dir = os.path.dirname(__file__)  # the folder where app.py lives
db_path = os.path.join(base_dir, "synthetic_socialcare2.db")

@function_tool
def execute_sql(query: str):
    """Run read-only SQL query on SQLite DB."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
    return [dict(zip(colnames, row)) for row in rows]

schema = {
    "clients": ["client_id", "name", "age", "gender", "postcode"],
    "assessments": ["assessment_id", "client_id", "assessment_date", "assessment_type", "assessor"],
    "services": ["service_id", "client_id", "service_name", "start_date", "end_date", "provider"],
    "outcomes": ["outcome_id", "client_id", "outcome_date", "outcome_type", "outcome_value"]
}

load_dotenv(override=True)

instruction1 = f"""
You are a SQL assistant for adult social care data.
Always generate SELECT-only SQL for the SQLite schema provided.
Return JSON: {{sql, explanation}}
Schema: {schema}
"""

Agent1 = Agent(name="QueryExecutor", instructions=instruction1, model="gpt-4o-mini")
tool1 = Agent1.as_tool(tool_name="instruct", tool_description=instruction1)

tools = [tool1, execute_sql]

resultagent = Agent(
    name="strictinstruct",
    instructions="Execute the SQL query and return a clean formatted table.",
    tools=tools,
    model="gpt-4o-mini"
)
