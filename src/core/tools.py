import os
import inspect
import sys
import tempfile
from difflib import get_close_matches
from core.state import get_state 
from utils.converters import fetch, batch_fetch
from langchain_core.tools import tool, BaseTool
from pathlib import Path


@tool
def open_simulink_file(file_name: str, get_content: bool = True, open_in_desktop: bool = False) -> dict | str:
    """
    Opens a Simulink file and/or returns its content.

    Parameters:
        file_name: Simulink file name with .slx extension
        get_content: whether to return the content/system in the Simulink file. True by default.
        open_in_desktop: whether to open the Simulink file in MATLAB desktop. False by default.

    Returns:
        If asked, description of the system inside the Simulink file as a dictionary.
    """

    eng = get_state("eng")

    if not file_name.endswith(".slx"):
        raise ValueError("Only .slx files are supported.")

    if eng.exist(file_name, "file") == 0:
        raise FileNotFoundError(f"'{file_name}' not found in MATLAB's current working directory.")

    eng.load_system(file_name)

    if open_in_desktop:
        try:
            if eng.usejava("desktop"):
                eng.open_system(file_name, nargout=0)
            else:
                raise RuntimeError("Failed to open in desktop. MATLAB desktop is not running")
        except Exception as e:
            raise RuntimeError(f"Unexpected error while opening Simulink file in desktop: {e}")

    if get_content:
        try:
            content = eng.describe_system(file_name) 
            return content
        except Exception as e:
            raise RuntimeError(f"Unexpected error while reading Simulink file: {e}")

    else:
        return f"{file_name} opened successfully in MATLAB desktop."


@tool
def open_matlab_file(file_name: str, get_content: bool = True, open_in_desktop: bool = False) -> str:
    """
    Returns the content of a matlab script file and/or opens it in MATLAB desktop.

    Parameters:
        file_name: script file name with .m extension
        get_content: whether to return the code in the script file. True by default
        open_in_desktop: whether to open the script in MATLAB desktop. False by default

    Returns:
        If asked, code inside the script as a string.
    """

    eng = get_state("eng")

    if not file_name.endswith(".m"):
        raise ValueError("Only .m files can be opened.")
    
    if eng.exist(file_name, "file") == 0:
        raise FileNotFoundError(f"'{file_name}' not found in MATLAB's current working directory.")
    
    if open_in_desktop:
        try:
            if eng.usejava("desktop"):
                eng.edit(file_name, nargout=0)
            else:
                raise RuntimeError("Failed to open. MATLAB desktop is not running.")
        except Exception as e:
            raise RuntimeError(f"Unexpected error while opening MATLAB file in desktop: {e}")

    if get_content: 
        try:
            return eng.fileread(file_name, nargout=1) 
        except Exception as e:
            raise RuntimeError(f"Unexpected error while reading MATLAB file: {e}") 
    else:
        return f"{file_name} opened successfully in MATLAB desktop."


@tool
def save_matlab_code(code: str, file_name: str, overwrite: bool = False) -> str:
    """
    Validates and saves MATLAB code to a .m file in the current MATLAB working directory.

    Parameters:
        code: MATLAB code as a string
        file_name: script name with .m extension
        overwrite: whether to overwrite if the file already exists. False by default

    Returns:
        Confirmation message with validation errors if any.
    """

    eng = get_state("eng")

    if not file_name.endswith(".m"):
        raise ValueError("Please save as a .m file.")
    
    if not file_name.isidentifier():
        raise ValueError("File name must be a valid MATLAB identifier.")
    
    if not overwrite and eng.exist(file_name, "file") == 2: 
        raise FileNotFoundError(f"'{file_name}' already exists in MATLAB's current working directory.")

    file_path = Path(eng.pwd()) / file_name

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
    except Exception as e:
        raise RuntimeError(f"Error saving the code file {file_name} in current working directory: {e}")
    
    try: 
        issues = eng.validate_code(file_path)
    except Exception as e:
        raise RuntimeError(f"Error validating the code file {file_name}: {e}") 
    
    if issues:
        return f"{file_name} saved but failed validation with following errors:\n" + "\n".join(issues)

    return f"Code validated and saved successfully as {file_name}."


@tool
def run_matlab_code(code: str, variables: list[str] = None, convert= False) -> str:
    """
    Executes MATLAB code, and returns whatever is displayed in the MATLAB command window, wrapped in a string.

    Parameters:
        code: MATLAB code to run.

    Returns:
        The results printed to MATLAB command window, wrapped in a string.
    """

    eng = get_state("eng")
    canvas_path = get_state("canvas_path")

    try:
        # eval does not support multi-line code, so we write it to the canvas (i.e. a temporary file) and run it through evalc.
        # evalc also returns whatever is printed to command window as a string, so it helps with disp functions etc.
        # TODO: Later it will be replaced by a canvas-based editor.
        with open(canvas_path, "w", encoding="utf-8") as f:
            f.write(code)

        output = eng.evalc(f"run('{canvas_path}')", nargout = 1)

    except Exception as e:
        raise RuntimeError(f"MATLAB execution failed: {e}")
    
    return output

@tool
def get_variables(variables: list[str], convert = False) -> dict:
    """
    Fetches specified variables from MATLAB workspace.

    Parameters:
        variables: list of variable names to retrieve from current MATLAB workspace after the code is ran.
        convert: whether to convert the variables to Python types. When False, the values will be returned as string-wrapped MATLAB types. False by default.

    Returns:
        A dictionary of asked variables and their values.
    """

    eng = get_state("eng")

    result = {}

    for var in variables:
        try:
            # Cannot do "if in eng.workspace" since it is not a native Python dict, rather a MATLAB object with some dict-like properties.
            if eng.exist(var, "var") == 1:
                if convert:
                    result[var] = fetch(eng, var)
                else:
                    result[var] = eng.evalc(f"{var}", nargout=1)
            else:
                result[var] = "Variable not found in MATLAB workspace."
        
        except Exception as e:
            raise RuntimeError(f"Error fetching variable '{var}': {e}")
        
    return result
    

@tool
def get_workspace_summary() -> str:
    """
    Returns a summary of current MATLAB workspace: variable names, sizes, and types.
    """

    eng = get_state("eng")

    try:
        info = eng.workspace_summary(nargout=1)
    except Exception as e:
        raise RuntimeError(f"Failed to get workspace summary: {e}")

    return info

@tool
def search_library(query) -> dict:
    """
    Searches for a block name in the Simulink block library and returns all matching source paths.

    Parameters:
        query: Name of the block to search for.

    Returns:
        A list of paths of blocks with similar names.
    """

    sl_lib_data = get_state("sl_lib_data")

    n = 2
    cutoff = 0.5

    try:
        block_names = list(sl_lib_data.keys())
        matches = get_close_matches(query, block_names, n=n, cutoff=cutoff)
        return {name: sl_lib_data[name]['paths'] for name in matches}
    
    except Exception as e:
       raise RuntimeError(f"Error searching Simulink library: {e}")


# Collect all the tools 
_current_module = sys.modules[__name__]

tools = [
    obj
    for name, obj in inspect.getmembers(_current_module)
    if isinstance(obj, BaseTool)
]

# TODO remember the newline thing for \n bs
# ['VehicleWithFourSpeedTransmission/Inertia', newline, 'Impeller']
