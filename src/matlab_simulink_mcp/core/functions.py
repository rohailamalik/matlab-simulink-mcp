import tempfile
import matlab.engine
from pathlib import Path
from typing import Any
from difflib import get_close_matches

import asyncio

from matlab_simulink_mcp.utils.convert import fetch
from matlab_simulink_mcp.utils.security import check_path, check_code
from matlab_simulink_mcp.core.state import get_engine, get_state
from fastmcp.exceptions import ToolError
from matlab_simulink_mcp.utils.logger import logger

# TODO: Incorporate image reading and multi modality, also needed for simulink broader view using snapshots
# for graph reading etc it's just an addon, not necessary since the llm can just parse through arrays plotting the graph
# though it is not much optimal at large lengths etc

# TODO: figure out some how to undo stuff in simulink
# TODO: figure out how to remove redline connections left after deleting blocks in simulink


def _raise_error(msg: str, exception: Exception | None = None):
    if exception:
        logger.error(f"{msg} Original error: {str(exception)}")
        if isinstance(exception, matlab.engine.MatlabExecutionError):
          error_msg = str(exception).strip().splitlines()[-1]
          raise ToolError(f"MATLAB returned error: {error_msg}")    
    raise ToolError(msg)


async def read_simulink_model(system: str) -> dict:
    """
    Returns JSON information about the layout of a simulink object containing elements, ports, connections, etc.

    Arguments:
        system: Path to the system or subsystem. e.g. system/subsystem1

    Returns:
        A dictionary of tool execution status and the information about all the elements, their ports, and their connections in the system or subsystem.
    """

    eng = get_engine()

    check_path(system)
    
    try:
        content = await asyncio.to_thread(eng.describe_system, system)
        return content 
    except Exception as e:
        return _raise_error("Error reading file.", e)
    

async def clean_simulink_model(arrange: bool = False) -> dict:
    """
    Cleans up, and optionally improves the layout, of currently open Simulink system/subsystem. 
    Recommended to use after modifying models to ensure cleanup of any unconnected lines.

    Arguments:
        arrange: Whether to improve the layout of blocks after cleanup.
    
    Returns:
        Number of unconnected lines deleted.   
    """

    eng = get_engine()
    mode = "dangling"
    target = "line"
    arrg = "true" if arrange else "false"
    
    try:
        content = await asyncio.to_thread(eng.format_simulink_model, target, mode, arrg, nargout=1)
        return content
    except Exception as e:
        return _raise_error("Error executing operation.", e)       

  
async def read_matlab_code(file: str, open: bool = False) -> str:
    """
    Returns the code inside a MATLAB script file (or any text file), and optionally opens it in MATLAB window.

    Arguments:
        script: Path to the .m file, relative to the working directory.
        open: Whether to open the file in MATLAB desktop. False unless asked.

    Returns:
        A dictionary of tool execution status and code inside the script.
    """

    eng = get_engine()

    check_path(file)
    
    if open:
        try:
            await asyncio.to_thread(eng.edit, file, 0)
        except Exception as e:
            _raise_error(f"Unexpected error while opening in desktop.", e)

    try:
        content = await asyncio.to_thread(eng.fileread, file, 1)
        return content
    except Exception as e:
        _raise_error(f"Unexpected error when reading file.", e)   


async def save_matlab_code(code: str, file: str, overwrite: bool = False) -> str:
    """
    Validates and saves MATLAB code to a .m file.

    Arguments:
        code: MATLAB code as a string
        file: Path to file (relative to current working directory) with .m extension.
        overwrite: Whether to overwrite if the file already exists.

    Returns:
        Tool execution status.
    """

    eng = get_engine()

    check_path(file)
    check_code(code)

    mode = "w" if overwrite else "x"

    try:
        cwd = await asyncio.to_thread(eng.pwd, nargout=1)
        path = Path(str(cwd)) / Path(file)
        path.parent.mkdir(parents=True, exist_ok=True) 
        with path.open(mode) as f:
            f.write(code)
    except Exception as e:
        _raise_error(f"Error saving the code.", e)
    
    try: 
        issues = await asyncio.to_thread(eng.validate_code, file)
        if issues:
            return "Code saved but failed validation with errors:\n" + "\n".join(issues)
        else:
            return "Code saved and validated successfully."
    except Exception as e:
        _raise_error(f"Error validating the code.", e) 
    
    


async def run_matlab_code(code: str) -> dict[str, Any]:
    """
    Executes code in MATLAB, and returns command window answerults as a string.

    Parameters:
        code: MATLAB code to run.

    Returns:
        A dictionary of tool execution status and answerults printed to command window.
    """

    # TODO: Later implement a canvas based editor
    eng = get_engine()

    check_code(code)

    async def _write_and_run(path: Path) -> str:
        with path.open("w") as f:
            f.write(code)
        content = await asyncio.to_thread(eng.evalc, f"run('{path.name}')", nargout=1)
        return content

    try: 
        cwd = await asyncio.to_thread(eng.pwd, nargout=1)
        path = Path(str(cwd)) / "canvas.m"
        content = asyncio.run(_write_and_run(path))
        return content 
    except PermissionError:
        path = Path(tempfile.gettempdir()) / "canvas.m"
        content = asyncio.run(_write_and_run(path))
        return content 
    except Exception as e:
        _raise_error("Unexpected error while running MATLAB code.", e)


async def get_variables(variables: list[str], convert = False) -> dict:
    """
    Fetches specified variables from MATLAB workspace.

    Parameters:
        variables: List of variable names to retrieve from workspace.
        convert: Whether to convert the variables to Python types. Otherwise, values will be returned as string-wrapped MATLAB types. False by default

    Returns:
        A dictionary of tool execution status, variables and their values.
    """

    eng = get_engine()

    answer = {}
    for var in variables:
        try:
            # Cannot do "if in eng.workspace" since it is not a native Python dict, rather a MATLAB object with some dict-like properties.
            # eng.exist automatically ensuanswer that the var is a proper variable name, without any code injection which could execute through evalc
            exists = await asyncio.to_thread(eng.exist, var, "var") 
            if exists == 1: 
                if convert:
                    answer[var] = fetch(eng, var)
                else:
                    answer[var] = await asyncio.to_thread(eng.evalc, f"{var}", nargout=1)
            else:
                answer[var] = "Not in workspace"

        except Exception:
            _raise_error(f"Error getting variable '{var}'.")
        
    return answer


def search_library(query) -> dict:
    """
    Searches for a block name in the Simulink block library and returns all matching source paths.

    Parameters:
        query: Name of the block to search for.

    Returns:
        A dictionary of tool execution status, a paths of blocks with similar names.
    """

    simlib = get_state().simlib

    n = 2
    cutoff = 0.5

    try:
        block_names = list(simlib.keys())
        matches = get_close_matches(query, block_names, n=n, cutoff=cutoff)
        return {name: simlib[name]['paths'] for name in matches}
    
    except Exception as e:
       _raise_error(f"Error searching Simulink library.")
    
# TODO remember the newline thing for \n 
# ['VehicleWithFourSpeedTransmission/Inertia', newline, 'Impeller']


