class Agent:
    def __init__(self, name, instructions, model=None, tools=None):
        self.name = name
        self.instructions = instructions
        self.model = model
        self.tools = tools or []

    def as_tool(self, tool_name, tool_description):
        """Return a callable stub tool wrapper"""
        def tool_fn(input_text):
            return {"sql": "SELECT 1", "explanation": "Stub response (replace with real agent logic)"}
        return tool_fn
