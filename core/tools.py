import inspect
import sys
from difflib import get_close_matches
from core.state import get_state, init_state 
from utils.converters import fetch
from utils.checks import check_file, check_code
from utils.utils import get_cwd, err, res
from langchain_core.tools import tool, BaseTool
from pathlib import Path
import matlab.engine
import tempfile
from typing import Any, Literal



# TODO: Incorporate image reading and multi modality, also needed for simulink broader view using snapshots
# for graph reading etc it's just an addon, not necessary since the llm can just parse through arrays plotting the graph
# though it is not much optimal at large lengths etc

# TODO: figure out some how to undo stuff in simulink
# TODO: figure out how to remove redline connections left after deleting blocks in simulink

'''


@tool
def snapshot_simulink(system: str) -> dict:
    """
    Take a PNG snapshot of a Simulink system/subsystem
    and return it as a base64-encoded data URI.
    
    Args:
        system: Path to the system or subsystem (e.g. "myModel/Controller").
    """

    eng = get_state().eng
    if (issues:= check_file(eng, system, adv = False)):
        return issues 

    try:
        b64 = eng.snapshot_b64(system, 150) 
        data_uri = f"data:image/png;base64,{b64}"
        return [{
            "type": "image_url", 
            "image_url": {"url": data_uri}
            }]
    except Exception as e:
        return err(f"Error taking snapshot: {e}")
'''

@tool
def read_simulink(system: str) -> dict[str, Any]:
    """
    Returns JSON information about the layout of a simulink object containing elements, ports, connections, etc.

    Arguments:
        system: Path to the system or subsystem. e.g. system/subsystem1

    Returns:
        A dictionary of tool execution status and the information about all the elements, their ports, and their connections in the system or subsystem.
    """

    eng = get_state().eng
    if (issues:= check_file(eng, system, adv = False)):
        return issues 
    
    try:
        eng.load_system(system)
        content = eng.describe_system(system) 
        return res(content)
    except Exception:
        return err("Error reading file.")
    

@tool
def clean_simulink(target: Literal["block", "line", "both"], strict: bool = False) -> dict[str, Any]:
    """
    Cleans up currently open Simulink system or subsystem by deleting unconnected lines and blocks.
    Recommended to use after modifying models to ensure cleanup of any leftover lines.

    Arguments:
        target: "block", "line" or "both"
        strict: When true, the function deletes even partially unconnected elements and not only fully unconnected ones.
    
    Returns:
        A dictionary of tool execution status    
    """

    eng = get_state().eng
    mode = "dangling" if strict else "orphaned"
    
    try:
        content = eng.cleanup(target, mode, nargout = 1)
    except Exception:
        return err("Error executing operation.")
    
    return res(content)        

  
@tool
def read_code(file: str, open: bool = False) -> dict[str, Any]:
    """
    Returns the code inside a MATLAB script file (or any text file), and optionally opens it in MATLAB window.

    Arguments:
        script: Path to the .m file, relative to the working directory.
        open: Whether to open the file in MATLAB desktop. False unless asked.

    Returns:
        A dictionary of tool execution status and code inside the script.
    """

    eng = get_state().eng
    if (issues:= check_file(eng, file)):
        return issues
    
    if open:
        try:
            eng.edit(file, nargout=0)
        except Exception:
            return err(f"Unexpected error while opening in desktop.")

    try:
        content = eng.fileread(file, nargout=1) 
    except Exception as e:
        error_msg = str(e).strip().splitlines()[-1]
        return err(f"Error reading file: {error_msg}")
        
    return res(content)    


@tool
def save_code(code: str, file: str, overwrite: bool = False) -> dict[str, Any]:
    """
    Validates and saves MATLAB code to a .m file.

    Arguments:
        code: MATLAB code as a string
        file: Path to file (relative to current working directory) with .m extension.
        overwrite: Whether to overwrite if the file already exists. False unless asked.

    Returns:
        A dictionary of tool execution status.
    """

    eng = get_state().eng
    if (issues:= check_file(eng, file, True, overwrite=overwrite)):
        return issues

    try:
        path = get_cwd(eng) / Path(file)
        path.parent.mkdir(parents=True, exist_ok=True) 
        with path.open("w") as f:
            f.write(code)
    except Exception:
        return err(f"Error saving the code.")
    
    try: 
        issues = eng.validate_code(file)
    except Exception:
        return err(f"Error validating the code.") 
    
    if issues:
        return err(f"Code saved but failed validation with errors:\n" + "\n".join(issues))
    else:
        return res(f"Code validated and saved successfully.")


@tool
def run_code(code: str) -> dict[str, Any]:
    """
    Executes code in MATLAB, and returns command window results as a string.

    Parameters:
        code: MATLAB code to run.

    Returns:
        A dictionary of tool execution status and results printed to command window.
    """

    # TODO: Later implement a canvas based editor
    eng = get_state().eng
    if (issues := check_code(code)):
        return issues

    def _write_and_run(path: Path) -> str:
        with path.open("w") as f:
            f.write(code)
        return eng.evalc(f"run('{path.name}')", nargout=1)

    try: 
        path = get_cwd(eng) / "canvas.m"
        results = _write_and_run(path)
        return res(results)

    except PermissionError: # Fallback to temporary file
        path = Path(tempfile.gettempdir()) / "canvas.m"
        results = _write_and_run(path)
        return res(results)

    except matlab.engine.MatlabExecutionError as e:
        error_msg = str(e).strip().splitlines()[-1]
        return err(f"MATLAB returned error: {error_msg}")

    except Exception:
        return err("Unexpected error while running MATLAB code.")


@tool
def get_variables(variables: list[str], convert = False) -> dict[str, Any]:
    """
    Fetches specified variables from MATLAB workspace.

    Parameters:
        variables: List of variable names to retrieve from workspace.
        convert: Whether to convert the variables to Python types. Otherwise, values will be returned as string-wrapped MATLAB types. False by default

    Returns:
        A dictionary of tool execution status, variables and their values.
    """

    eng = get_state().eng

    result = {}
    for var in variables:
        try:
            # Cannot do "if in eng.workspace" since it is not a native Python dict, rather a MATLAB object with some dict-like properties.
            # eng.exist automatically ensures that the var is a proper variable name, without any code injection which could execute through evalc
            if eng.exist(var, "var") == 1: 
                if convert:
                    result[var] = fetch(eng, var)
                else:
                    result[var] = eng.evalc(f"{var}", nargout=1)
            else:
                result[var] = "Not in workspace"

        except Exception:
            return err(f"Error getting variable '{var}'.")
        
    return res(result)


@tool
def search_library(query) -> dict[str, Any]:
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
        results = {name: simlib[name]['paths'] for name in matches}
        return res(results)
    
    except Exception as e:
       return err(f"Error searching Simulink library.")
    
# TODO remember the newline thing for \n 
# ['VehicleWithFourSpeedTransmission/Inertia', newline, 'Impeller']


# Get all the tools 
_current_module = sys.modules[__name__]
tools = [obj for name, obj in inspect.getmembers(_current_module) if isinstance(obj, BaseTool) ]