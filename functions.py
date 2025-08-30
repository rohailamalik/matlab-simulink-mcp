import tempfile
import matlab.engine
from pathlib import Path
from typing import Any
from fastmcp.exceptions import ToolError
import asyncio
from logger import logger

# some learning, do not return error objects, as the server cannot convert them to json schema stuff
# might not even be able to provide a return hint string for the error as it might be included in the mcp schema 
# it's better to just raise an error with a message and the server automatically converts it to a proper error response
# raising tool errors or any other error is the same, but toolerror always displays the content even if the agurment when defining the server prevents details be sent to the llm, also tool error 
# when used  it doesnt say "error running tool" instead just directly giving content of error
# so raise the tool error with a message. maybe with details/traceback in case of unknown errors
# alongisde this, use logging to log the full traceback in terminal or files for details perhaps.

from small_server import mcp
from fastmcp.server.dependencies import get_context

def _raise_error(msg: str, exception: Exception | None = None):
    #if exception:
        #logger.error(f"{msg} Original error: {str(exception)}")
    #else: 
        #logger.error(msg)
    raise ToolError(msg)

def _get_state() -> dict:
    ctx = get_context()
    return ctx.request_context.lifespan_context
      
def _get_cwd() -> Path:
    try:
        eng = _get_state().eng
        return Path(str(eng.pwd(nargout=1)))
    except Exception as e:
        _raise_error(f"Error getting current working directory", e)
    
def _get_engine():
    eng = _get_state().eng
    
    return eng


async def read_code(file: str, open: bool = False) -> str:
    """
    Returns the code inside a MATLAB script file (or any text file), and optionally opens it in MATLAB window.

    Arguments:
        script: Path to the .m file, relative to the working directory.
        open: Whether to open the file in MATLAB desktop. 

    Returns:
        A dictionary of tool execution status and code inside the script.
    """

    eng = _get_engine()
    if eng is None:
        return "oh. No MATLAB engine connected. Please connect to a shared MATLAB session."
    
    if open:
        try:
            await asyncio.to_thread(eng.edit, file, 0)
        except Exception:
            _raise_error(f"Unexpected error while opening in desktop.")

    try:
        content = await asyncio.to_thread(eng.fileread, file, 1)
        return content 
    except Exception as e:
        error_msg = str(e).strip().splitlines()[-1]
        _raise_error(f"Error reading file: {error_msg}")   


def run_code(code: str) -> str:
    """
    Executes code in MATLAB, and returns command window answerults as a string.

    Parameters:
        code: MATLAB code to run.

    Returns:
        A dictionary of tool execution status and answerults printed to command window.
    """

    eng = _get_engine()
    
    def _write_and_run(path: Path) -> str:
        with path.open("w") as f:
            f.write(code)
        return eng.evalc(f"run('{path.name}')", nargout=1)

    try: 
        path = _get_cwd() / "canvas.m"
        return _write_and_run(path)

    except PermissionError: # Fallback to temporary file
        path = Path(tempfile.gettempdir()) / "canvas.m"
        return _write_and_run(path)

    except matlab.engine.MatlabExecutionError as e:
        error_msg = str(e).strip().splitlines()[-1]
        _raise_error(f"MATLAB returned error: {error_msg}")

    except Exception:
        _raise_error("Unexpected error while running MATLAB code.")



