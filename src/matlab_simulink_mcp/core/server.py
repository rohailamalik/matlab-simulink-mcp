import inspect
from mcp.server.fastmcp import FastMCP
from matlab_simulink_mcp.core import functions

mcp = FastMCP("Demo")

for name, fn in inspect.getmembers(functions, inspect.isfunction):
    if fn.__module__ == functions.__name__ and not name.startswith("_"):
        mcp.tool()(fn)