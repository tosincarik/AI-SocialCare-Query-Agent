# %%
import sqlite3
import os
from faker import Faker
import random
import asyncio
import streamlit as st
import pandas as pd

# Ensure the 'data' folder exists
os.makedirs('data', exist_ok=True)

# Define the database path
db_path = os.path.join('data', 'synthetic_socialcare2.db')

# %% [markdown]
# ### Database setup and synthetic data population

# Connect and create tables if they don't exist
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop old tables (for testing/re-runs)
cursor.execute("DROP TABLE IF EXISTS clients")
cursor.execute("DROP TABLE IF EXISTS assessments")
cursor.execute("DROP TABLE IF EXISTS services")
cursor.execute("DROP TABLE IF EXISTS outcomes")

# Create tables
cursor.execute("""
CREATE TABLE clients (
    client_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    postcode TEXT
)
""")
cursor.execute("""
CREATE TABLE assessments (
    assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    assessment_date TEXT,
    assessment_type TEXT,
    assessor TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
)
""")
cursor.execute("""
CREATE TABLE services (
    service_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    service_name TEXT,
    start_date TEXT,
    end_date TEXT,
    provider TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
)
""")
cursor.execute("""
CREATE TABLE outcomes (
    outcome_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    outcome_date TEXT,
    outcome_type TEXT,
    outcome_value TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
)
""")
conn.commit()

# Populate synthetic data
fake = Faker("en_GB")
N_CLIENTS = 50
for client_id in range(1, N_CLIENTS + 1):
    name = fake.name()
    age = random.randint(18, 95)
    gender = random.choice(["Male", "Female"])
    postcode = fake.postcode()
    cursor.execute("INSERT INTO clients VALUES (?, ?, ?, ?, ?)", (client_id, name, age, gender, postcode))

    for _ in range(random.randint(1,3)):
        cursor.execute("INSERT INTO assessments (client_id, assessment_date, assessment_type, assessor) VALUES (?, ?, ?, ?)",
                       (client_id, fake.date_between(start_date="-2y", end_date="today"),
                        random.choice(["Care Act", "Financial", "Risk"]), fake.name()))
    for _ in range(random.randint(1,2)):
        start_date = fake.date_between(start_date="-2y", end_date="-1m")
        end_date = fake.date_between(start_date=start_date, end_date="today")
        cursor.execute("INSERT INTO services (client_id, service_name, start_date, end_date, provider) VALUES (?, ?, ?, ?, ?)",
                       (client_id, random.choice(["Home Care", "Residential Care", "Day Centre", "Direct Payment"]),
                        start_date, end_date, random.choice(["Local Authority", "Private Agency", "Charity"])))
    for _ in range(random.randint(1,2)):
        cursor.execute("INSERT INTO outcomes (client_id, outcome_date, outcome_type, outcome_value) VALUES (?, ?, ?, ?)",
                       (client_id, fake.date_between(start_date="-1y", end_date="today"),
                        random.choice(["Independence", "Wellbeing", "Safety", "Financial"]),
                        random.choice(["Improved", "Maintained", "Declined"])))

conn.commit()
conn.close()

# %% [markdown]
# ### Schema dictionary for agent reference
schema = {
    "clients": ["client_id", "name", "age", "gender", "postcode"],
    "assessments": ["assessment_id", "client_id", "assessment_date", "assessment_type", "assessor"],
    "services": ["service_id", "client_id", "service_name", "start_date", "end_date", "provider"],
    "outcomes": ["outcome_id", "client_id", "outcome_date", "outcome_type", "outcome_value"]
}

# %% [markdown]
# ### AI SQL Agent Setup
from dotenv import load_dotenv
from openai import OpenAI

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from agents import Agent, Runner, trace, function_tool

load_dotenv(override=True)
openaikey = os.getenv("OPENAI_API_KEY")
if openaikey:
    print(f"OpenAI API key found: {openaikey[:8]}")
else:
    print("OpenAI API key not found")

# %% [markdown]
# #### SQL execution tool
@function_tool
def execute_sql(query: str):
    """Run a read-only SQL query on the SQLite DB and return results as list of dicts."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
    return [dict(zip(colnames, row)) for row in rows]

# %% [markdown]
# #### Agent instructions
instruction1 = f"""
You are a SQL assistant for adult social care data.
Always generate SELECT-only SQL for the SQLite schema provided.
Never use DROP, INSERT, UPDATE, DELETE, ALTER, ATTACH, or PRAGMA.
Return strictly JSON with keys:
- sql: the SQL query string
- explanation: a short (1-2 sentence) explanation of the query logic
Schema reference: {schema}
Make sure the output is a single valid JSON object, nothing else.
"""

Agent1 = Agent(name='QueryExecutor', instructions=instruction1, model="gpt-4o-mini")
tool1 = Agent1.as_tool(tool_name='instruct', tool_description=instruction1)
tools = [tool1, execute_sql]

instruction2 = "You are to execute the SQL query you generate and return a clean formatted table. Use the tools provided to you"
resultagent = Agent(name="strictinstruct", instructions=instruction2, tools=tools, model='gpt-4o-mini')

# %% [markdown]
# ### Streamlit App UI
st.title("Social Care Query Agent")

# Initialize conversation
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask me about the social care database..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Placeholder for assistant
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("⏳ Querying database...")

        async def run_agent():
            result = await Runner.run(resultagent, prompt)
            return result.final_output

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        output = loop.run_until_complete(run_agent())
        loop.close()

        # Try to parse JSON for table display
        import json
        table_data = None
        try:
            parsed = json.loads(output)
            sql_query = parsed.get("sql")
            explanation = parsed.get("explanation")
            # Execute the query to get actual results
            table_data = execute_sql(sql_query)
            df = pd.DataFrame(table_data)
            placeholder.markdown(f"**Explanation:** {explanation}")
            if not df.empty:
                st.dataframe(df)  # Display as table
                st.bar_chart(df.select_dtypes(include="number"))  # Chart numeric columns
                csv = df.to_csv(index=False)
                st.download_button("Download CSV", csv, "query_results.csv")
        except Exception:
            # Fallback if output is not JSON
            placeholder.markdown(output)

        # Save assistant response
        st.session_state.messages.append({"role": "assistant", "content": output})
