import sys
import inspect
from fastmcp import FastMCP

import matlab_simulink_mcp.state as state
from matlab_simulink_mcp.state import lifespan, logger
from matlab_simulink_mcp import functions


# Make functions into tools
def collect_tools():
    tools = []
    for name, fn in inspect.getmembers(functions, inspect.isfunction):
        if fn.__module__ == functions.__name__ and not name.startswith("_"):
            tools.append(fn)
    return tools

# Define server
mcp = FastMCP(
    name="MATLAB_Simulink_MCP", 
    lifespan=lifespan, 
    tools=collect_tools()
    )

# Run server
def run(console: bool=False):
    try:
        state.console = console
        mcp.run(transport="stdio")
    except Exception as e:
        logger.exception(f"Failed to start the server: {str(e)}")
        sys.exit(1)

 
