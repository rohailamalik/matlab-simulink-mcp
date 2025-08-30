import inspect
from langchain_core.tools import tool

from matlab_simulink_mcp.core import functions


tools = []
for name, fn in inspect.getmembers(functions, inspect.isfunction): 
    if fn.__module__ == functions.__name__ and not name.startswith("_"):
        tools.append(tool()(fn))