from fastmcp import FastMCP
from contextlib import asynccontextmanager
from logger import logger
from state import MatlabState
import inspect
import functions

@asynccontextmanager
async def lifespan(server):
    try:
        state = MatlabState()
        state.load_data()
        state.connect_matlab()
        yield state

    except Exception as e:
        logger.error(f"Failed to initialize state: {e}")
        raise



tools = []
for name, fn in inspect.getmembers(functions, inspect.isfunction):
    if fn.__module__ == functions.__name__ and not name.startswith("_"):
        tools.append(fn)

mcp = FastMCP("Test_MATLAB", lifespan=lifespan, tools = tools)


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


@mcp.prompt()
def translation_ja(txt: str) -> str:
    """Translating to Japanese"""
    return f"Please translate this sentence into Japanese:\n\n{txt}"

if __name__ == "__main__":
    try:
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Issue running server: {e}")



# IMPORTANT, VISIT DOCUMENTATION FOR FASTMCP OBJECT. SAW THIS THERE: A list of tools (or functions to convert to tools) to add to the server.
#  In some cases, providing tools programmatically may be more convenient than using the @mcp.tool decorator

# raise just pushes the error to next level in the chain or nest. so dont use raise at top most level instead just log or print there.

# it might be a good idea for now to not start the server in case of those files not loading, but let it start in case of no engine. maybe display an error or smth in console tho.
# then have the engine check at each tool and if there isnt any engine the llm just tells i cant do it cuz no engine, and then there is a dedicated tool for this which loads the engine
# and adds helpers to path etc.