import inspect
from langchain_core.tools import tool

from matlab_simulink_mcp.core import functions


tools = []
for name, fn in inspect.getmembers(functions, inspect.isfunction): 
    agent_tool = tool()(fn)
    tools.append(agent_tool)