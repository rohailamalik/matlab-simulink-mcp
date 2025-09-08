import inspect
from fastmcp import FastMCP

import matlab_simulink_mcp.state as state
from matlab_simulink_mcp.state import lifespan, logger
from matlab_simulink_mcp import functions


# Make functions into tools
tools = []
for name, fn in inspect.getmembers(functions, inspect.isfunction):
    if fn.__module__ == functions.__name__ and not name.startswith("_"):
        tools.append(fn)

# Define server
mcp = FastMCP("MATLAB_Simulink_MCP", lifespan=lifespan, tools = tools)

# Run server
def run(console: bool = False):
    try:
        state.console = console
        mcp.run(transport="stdio")
    except Exception:
        logger.exception("Issue running server.")

 
