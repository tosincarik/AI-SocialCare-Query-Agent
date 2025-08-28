🧑‍⚕️ AI-SocialCare-Query-Agent

An AI-powered query assistant that translates natural language questions into SQL queries and runs them against a synthetic Social Care database.
This project demonstrates how AI can help managers and analysts quickly explore key performance indicators (KPIs) in adult social care.

🚀 Features

🗂️ SQLite synthetic database with realistic UK-style social care data (Clients, Assessments, Services, Outcomes).

🤖 AI Query Agent powered by OpenAI (gpt-4o-mini), translating natural language → SQL → results.

🛡️ Safe execution – only SELECT queries are allowed.

📊 Formatted results – outputs in clean tables with explanations.

🔍 Trace logging – captures full chain-of-thought (NL → SQL → result) for transparency and audit.



### Tech Stack

Python

SQLite (for database)

OpenAI SDK (for AI query translation & structured outputs)

LangChain / OpenAI Tracing Tools (AgentTracer, Runner for monitoring and execution)

dotenv (for managing API keys securely)




🏗️ Database Schema

The synthetic database contains 4 core tables:

clients – demographics & postcode

assessments – assessment history (type, assessor, date)

services – allocated care services with provider info

outcomes – service outcomes (Independence, Safety, etc.)

Each table links via client_id for relational queries.




⚙️ Setup Instructions
1. Clone the repo

```bash
git clone https://github.com/tosincarik/AI-SocialCare-Query-Agent.git
cd AI-SocialCare-Query-Agent
```



2. Create environment with uv

```bash
uv venv
source .venv/bin/activate  # (or .venv\Scripts\activate on Windows)
uv pip install -r requirements.txt
```

3. Environment variables

Create a .env file:

```python
OPENAI_API_KEY=your_api_key_here
```

4. Run database setup

The script automatically:

Creates tables

Populates with Faker-generated data

```bash
python scripts/setup_db.py
```

5. Run the agent

Launch an example query:

message = "List the adults aged over 20 years with their service outcome"
result = await Runner.run(resultagent, message)
print(result.final_output)

🧪 Example Query

User:

Show me the total number of clients by gender

Agent Output:

{
  "sql": "SELECT gender, COUNT(*) as total_clients FROM clients GROUP BY gender;",
  "explanation": "This query counts the number of clients in each gender category."
}


Result (formatted):

gender	total_clients
Male	26
Female	24




### Usage

Type a natural language query (e.g., "Show me the average age of clients with pending referrals")

Agent translates query → SQL → Executes → Returns structured output

Use Agent Tracer to monitor steps, debug, and view logs

Example Queries

"List the top 5 clients by number of assessments"

"What is the average time between referral and assessment?"

"Show a summary of services provided by category"

📜 License

MIT License – feel free to use, modify, and share.