# agents/runner.py
import json
from typing import Any
from openai import OpenAI

client = OpenAI()

class Runner:
    """
    Runner.run(agent, prompt) orchestrates:
      1) call the agent's SQL-generator tool (first tool in agent.tools) to get JSON {"sql","explanation"}
      2) call the DB execution tool (a callable provided as second tool) with the SQL string
      3) assemble a JSON string that the Streamlit app expects as result.final_output
    """
    @staticmethod
    async def run(agent, prompt: str) -> Any:
        # minimal validation
        if not agent.tools or len(agent.tools) < 1:
            # nothing to run; return a Result with an explanation
            class Result: 
                def __init__(self, final_output): self.final_output = final_output
            return Result(json.dumps({"sql": "", "explanation": "No agent tools available", "rows": []}))

        # 1) SQL tool (assume first tool generates JSON with 'sql' and 'explanation')
        sql_tool = agent.tools[0]
        sql_response = sql_tool(prompt)

        # if tool returned JSON string, try load
        if isinstance(sql_response, str):
            try:
                sql_response = json.loads(sql_response)
            except Exception:
                sql_response = {"sql": "", "explanation": sql_response}

        sql = sql_response.get("sql", "") if isinstance(sql_response, dict) else ""
        explanation = sql_response.get("explanation", "") if isinstance(sql_response, dict) else ""

        # 2) If a db execution tool exists, call it; otherwise rows = []
        rows = []
        if len(agent.tools) >= 2 and callable(agent.tools[1]) and sql:
            try:
                rows = agent.tools[1](sql)  # execute_sql returns list[dict]
            except Exception as e:
                rows = []
                explanation += f" | DB execution error: {e}"

        # 3) Build final output as JSON string so SocialCareQuery can json.loads it
        final_obj = {
            "sql": sql,
            "explanation": explanation,
            "rows": rows
        }

        class Result:
            def __init__(self, final_output):
                self.final_output = final_output

        return Result(json.dumps(final_obj))
