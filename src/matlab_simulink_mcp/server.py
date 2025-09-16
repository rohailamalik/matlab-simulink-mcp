import inspect, time
from fastmcp import FastMCP
from contextlib import asynccontextmanager

from matlab_simulink_mcp.state import EngineState, logger, log_console
from matlab_simulink_mcp import functions

console = False

# Create lifespan function
@asynccontextmanager
async def lifespan(server): # do not remove server argument as it will break stuff
    """Launch pre-reqs for the server as context accessible during its run"""
    log_console.open()
    time.sleep(1)

    state = EngineState()
    state.initialize()

    if not console:
        time.sleep(1)
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
        mcp.run(transport="stdio", show_banner=False)
    except Exception as e:
        if hasattr(e, "exceptions"): 
            for sub in e.exceptions:
                logger.exception(f"{sub}")
        else:
            logger.exception(f"{e}")
        #sys.exit(1)

 
