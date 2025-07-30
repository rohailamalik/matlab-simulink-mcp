import os
import inspect
import sys
from core.state import get_engine, get_sl_lib_data 
from typing import Optional
from difflib import get_close_matches
import matlab.engine
from langchain_core.tools import tool, BaseTool
from utils.type_converters import fetch

@tool
def open_simulink_file(file_name: str, get_content: bool = True, open_in_desktop: bool = False) -> Optional[dict]:
    """
    Opens a Simulink file and/or returns its content.

    Parameters:
        file_name: Simulink file name with .slx extension
        get_content: whether to view the content/system in the Simulink file.
        open_in_desktop: whether to open the Simulink file in MATLAB desktop. False by default

    Returns:
        Description of the system inside the Simulink file as a dictionary.
    """

    eng = get_engine()

    if not file_name.endswith(".slx"):
        raise ValueError("Please only use a .slx file.")

    if not os.path.isfile(file_name):
        raise FileNotFoundError(f"'{file_name}' not found.")  

    eng.load_system(file_name)

    if open_in_desktop:
        if eng.usejava("desktop"):
            eng.open_system(file_name, nargout=0)
        else:
            raise RuntimeError("Failed to open in desktop. MATLAB Desktop is not running.")

    if get_content:
        content = eng.describe_system(file_name) 
    else:
        content = None

    return content

@tool
def open_matlab_file(file_name: str, get_content: bool = True, open_in_desktop: bool = False) -> Optional[str]:
    """
    Opens a MATLAB script and/or returns its content.

    Parameters:
        file_name: script file name with .m extension
        get_content: whether to get the content in the script file. True by default
        open_in_desktop: whether to open the script in MATLAB desktop. False by default

    Returns:
        Code inside the script (if asked), as a string.
    """

    eng = get_engine()

    if not file_name.endswith(".m"):
        raise ValueError("Please only use a .m file.")

    if not os.path.isfile(file_name):
        raise FileNotFoundError(f"'{file_name}' not found.")

    if get_content: 
        try:
            content = eng.eval(f"fileread('{file_name}')", nargout=1)
        except matlab.engine.MatlabExecutionError as e:
            raise FileNotFoundError(f"MATLAB couldn't find or read the file: {file_name}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error while reading MATLAB file: {e}") from e
    else:
        content = None

    if open_in_desktop:
        if eng.usejava("desktop"):
            eng.edit(file_name, nargout=0)
        else:
            raise RuntimeError("Failed to open in desktop.")

    return content


def save_matlab_code(code: str, file_name: str, overwrite: bool = False) -> str:
    """
    Validates and saves MATLAB code to a .m file in the current MATLAB working directory.

    Parameters:
        code: MATLAB code as a string
        file_name: script file name with .m extension
        overwrite: whether to overwrite if the file already exists. False by default

    Returns:
        Confirmation message if saved. Error message if validation fails.
    """

    eng = get_engine()

    if not file_name.endswith(".m"):
        raise ValueError("Please use a .m file.")

    cwd = eng.pwd() 
    file_path = os.path.join(cwd, file_name)

    if not overwrite and eng.exist(file_name, "file") == 2: 
        return f"'{file_name}' already exists in MATLAB's current working folder."

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    eng.addpath(cwd, nargout=0)

    try: 
        # Checkcode returns a structure array (which isn't converted between MATLAB and python) in case of errors.
        #Hence we convert it to a JSON string.
        result = eng.eval(f"jsonencode(checkcode({file_name}))") # TODO: Possible source of `ValueError('only a scalar struct can be returned from MATLAB')`
    except Exception as e:
            raise RuntimeError(f"Error when validating the code file {file_name}: {e}") from e
    if result:
        os.remove(file_path)
        messages = [msg.message for msg in result]
        raise ValueError(
            f"MATLAB syntax issues found in '{file_name}':\n" + "\n".join(messages)
        )

    return f"Code saved successfully as {file_name}."

@tool
def run_matlab_code(code: str, variables: list[str] = None) -> dict: #TODO: solve the double quotation problem thing... eng.eval("whos(\"nb\")")
    """
    Executes MATLAB code and retrieves values of specified variables from workspace.

    Parameters:
        code: MATLAB code to run. Leave empty if no code is needed to run.
        variables: list of variable names to retrieve from MATLAB workspace after the code is ran. Leave empty if no variables are needed. Use "ans" as the variable when no specific variable is used in the code.

    Returns:
        A dictionary of asked variables and their values (converted to Python)
    """

    eng = get_engine()

    if code:
        try:
            eng.eval(code)
        except Exception as e:
            raise RuntimeError(f"MATLAB execution failed: {e}")

    result = {}
    if variables:
        for var in variables:
            result[var] = fetch(var, eng)

    return result

@tool
def get_workspace_summary():
    """
    Returns a summary of current MATLAB workspace: variable names, sizes, and types.
    """

    eng = get_engine()

    info = eng.eval("whos", nargout=1)

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

    eng = get_engine()
    sl_lib_data = get_sl_lib_data()

    n = 2
    cutoff = 0.5

    block_names = list(sl_lib_data.keys())
    matches = get_close_matches(query, block_names, n=n, cutoff=cutoff)
    return {name: sl_lib_data[name]['paths'] for name in matches}


# Collect all the tools 
_current_module = sys.modules[__name__]

tools = [
    obj
    for name, obj in inspect.getmembers(_current_module)
    if isinstance(obj, BaseTool)
]

notools = [open_simulink_file, open_matlab_file, save_matlab_code, run_matlab_code, get_workspace_summary, search_library]

# TODO remember the newline thing for \n bs
# ['VehicleWithFourSpeedTransmission/Inertia', newline, 'Impeller']
