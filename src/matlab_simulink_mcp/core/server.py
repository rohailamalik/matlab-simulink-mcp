import sys
import inspect
import time
from fastmcp import FastMCP
from contextlib import asynccontextmanager

from matlab_simulink_mcp.config import logger, log_console
from matlab_simulink_mcp.engine.handler import EngineState
from matlab_simulink_mcp.core import functions

console = False


# Create lifespan function
@asynccontextmanager
async def lifespan(server): # do not remove server argument as it will break stuff
    log_console.open()
    
    state = EngineState()
    state.initialize()
    
    if not console:
        time.sleep(3) # some delay
        log_console.close()

    yield state


# Compile tools
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
        console = console
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Failed to start the server: {str(e)}")
        sys.exit(1)

 
