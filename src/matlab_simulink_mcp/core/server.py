import inspect
from fastmcp import FastMCP

from matlab_simulink_mcp.core import functions
from matlab_simulink_mcp.core.state import lifespan
from matlab_simulink_mcp.utils.logger import logger


# Make functions into tools
tools = []
for name, fn in inspect.getmembers(functions, inspect.isfunction):
    if fn.__module__ == functions.__name__ and not name.startswith("_"):
        tools.append(fn)

# Define server
mcp = FastMCP("MATLAB_Simulink_MCP", lifespan=lifespan, tools = tools)

# Run server
def run():
    try:
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Issue running server: {e}")

 
