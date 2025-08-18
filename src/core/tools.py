import inspect
import sys
from difflib import get_close_matches
from core.state import get_state 
from utils.converters import fetch
from utils.checks import check_file, check_code
from utils.utils import get_cwd, err, res
from langchain_core.tools import tool, BaseTool
from pathlib import Path
import matlab.engine

# TODO: introduce a fallback where the saving/writing/running directory is changed from working directory to temp
# TODO: Incorporate image reading and multi modality, also needed for simulink broader view using snapshots
# for graph reading etc it's just an addon, not necessary since the llm can just parse through arrays plotting the graph
# though it is not much optimal at large lengths etc

def open_simulink_file(file: str, get_content: bool = True, open_in_desktop: bool = False) -> dict:
    """
    Opens a Simulink file and/or returns its content.

    Arguments:
        file: Path to .slx file (relative to working directory) 
        get_content: Whether to return description of content in the Simulink file. 
        open_in_desktop: Whether to open the file in desktop.

    Returns:
        A dictionary of tool execution status and Simulink file content.
    """

    eng = get_state().eng
    if (issues:= check_file(eng, file, ".slx", "read", False)):
        return issues
    
    content = None

    if open_in_desktop:
        try:
            eng.open_system(file, nargout=0)
            content = f"{file} opened successfully in MATLAB desktop."
        except Exception:
            return err("Unexpected error while opening in desktop.")
    else: 
        eng.load_system(file)
    
    if get_content:  
        try:
            content = eng.describe_system(file) 
        except Exception:
            return err("Unexpected error while reading file.")
        
    return res(content)


def open_matlab_file(file: str, get_content: bool = True, open_in_desktop: bool = False) -> dict:
    """
    Returns the content of a matlab script and/or opens it in MATLAB desktop.

    Arguments:
        file: Path to .m file (relative to working directory) 
        get_content: Whether to return code in the script. 
        open_in_desktop: Whether to open the script in MATLAB desktop. 

    Returns:
        A dictionary of tool execution status and file code.
    """
    
    eng = get_state().eng
    if (issues:= check_file(eng, file, ".m", "read", False)):
        return issues
    
    if open_in_desktop:
        try:
            eng.edit(file, nargout=0)
            content = f"{file} opened successfully in MATLAB desktop."
        except Exception:
            return err(f"Unexpected error while opening in desktop.")

    if get_content: 
        try:
            content = eng.fileread(file, nargout=1) 
        except Exception:
            return err(f"Unexpected error while reading MATLAB file.") 
        
    return res(content)


def save_matlab_code(code: str, file: str, overwrite: bool = False) -> dict:
    """
    Validates and saves MATLAB code to a .m file in the current MATLAB working directory.

    Arguments:
        code: MATLAB code as a string
        file: Path to script file (relative to current working directory) with .m extension.
        overwrite: Whether to overwrite if the file already exists.

    Returns:
        A dictionary of tool execution status.
    """

    eng = get_state().eng
    if (issues:= check_file(eng, file, ".m", "write", overwrite)):
        return issues
    if (issues:= check_code(code)):
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


def run_matlab_code(code: str) -> dict:
    """
    Executes code in MATLAB windows, and returns command window results as a string.

    Parameters:
        code: MATLAB code to run.

    Returns:
        A dictionary of tool execution status and results printed to command window.
    """

    eng = get_state().eng
    if (issues:= check_code(code)):
        return issues

    try:
        # eval does not support multi-line code, so we write it to the canvas (i.e. a temporary file) and run it through evalc.
        # evalc also returns whatever is printed to command window as a string, so it helps with disp functions etc.
        # TODO: Later it will be replaced by a canvas-based editor.
        path = get_cwd(eng) / "canvas.m" 
        with path.open("w") as f:
            f.write(code)
        
        results = eng.evalc("run('canvas.m')", nargout = 1)
        return res(results)
    
    except matlab.engine.MatlabExecutionError as e:
        error_msg = str(e).strip().splitlines()[-1]
        return err(f"MATLAB returned error: {error_msg}")

    except Exception:
        return err(f"Unexpected error while running MATLAB code.")


def get_variables(variables: list[str], convert = False) -> dict:
    """
    Fetches specified variables from MATLAB workspace.

    Parameters:
        variables: List of variable names to retrieve from workspace.
        convert: Whether to convert the variables to Python types. When False, the values will be returned as string-wrapped MATLAB types.

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
        results = {name: simlib[name]['paths'] for name in matches}
        return res(results)
    
    except Exception as e:
       return err(f"Error searching Simulink library.")
    
# TODO remember the newline thing for \n 
# ['VehicleWithFourSpeedTransmission/Inertia', newline, 'Impeller']


# Get all the tools 
_current_module = sys.modules[__name__]
tools = [
    tool(obj)
    for name, obj in inspect.getmembers(_current_module, inspect.isfunction)
    if not isinstance(obj, BaseTool) and not name.startswith("_")
]
