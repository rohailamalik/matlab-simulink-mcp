import inspect
from mcp.server.fastmcp import FastMCP

from matlab_simulink_mcp.core import functions

mcp = FastMCP("Demo")

for name, fn in inspect.getmembers(functions, inspect.isfunction): 
    mcp.tool()(fn)