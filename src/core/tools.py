import os
from state import eng, sl_lib_data
from typing import Optional
from difflib import get_close_matches

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

    if not file_name.endswith(".m"):
        raise ValueError("Please only use a .m file.")

    if not os.path.isfile(file_name):
        raise FileNotFoundError(f"'{file_name}' not found.")

    if get_content: # TODO: This assumes that the path of the server app is the same as the MATLAB working directory. 
        # Use matlab working directory here.
        with open(file_name, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = None

    if open_in_desktop:
        if eng.usejava("desktop"):
            eng.edit(file_name, nargout=0)
        else:
            raise RuntimeError("Failed to open in desktop. MATLAB Desktop is not running.")

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

    if not file_name.endswith(".m"):
        raise ValueError("Please use a .m file.")

    cwd = eng.pwd()
    file_path = os.path.join(cwd, file_name)

    if not overwrite and eng.exist(file_name, "file") == 2:
        return f"'{file_name}' already exists in MATLAB's current working folder."

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    eng.addpath(cwd, nargout=0)

    result = eng.checkcode(file_path, nargout=1)
    if result:
        os.remove(file_path)
        messages = [msg.message for msg in result]
        raise ValueError(
            f"MATLAB syntax issues found in '{file_name}':\n" + "\n".join(messages)
        )

    return f"Code saved successfully as {file_name}."


def run_matlab_code(code: str, variables: list[str] = None) -> dict:
    """
    Executes MATLAB code and retrieves values of specified variables from it.

    Parameters:
        code: MATLAB code to run
        variables: list of variable names to retrieve from MATLAB workspace after the code is ran. Leave empty if no variables are needed.

    Returns:
        A dictionary of asked variables and their values (converted to Python)
    """

    try:
        eng.eval(code, nargout=0)
    except Exception as e:
        raise RuntimeError(f"MATLAB execution failed: {e}")

    result = {}
    if variables:
        for var in variables:
            try:
                result[var] = eng.workspace[var]
            except Exception:
                result[var] = None

    return result


def get_workspace_summary():
    """
    Returns a summary of current MATLAB workspace: variable names, sizes, and types.
    """

    info = eng.eval("whos", nargout=1)

    return info


def search_library(query) -> dict:
    """
    Searches for a block name in the Simulink block library and returns all matching source paths.

    Parameters:
        query: Name of the block to search for.

    Returns:
        A list of paths of blocks with similar names.
    """

    n = 2
    cutoff = 0.5

    block_names = list(sl_lib_data.keys())
    matches = get_close_matches(query, block_names, n=n, cutoff=cutoff)
    return {name: sl_lib_data[name]['paths'] for name in matches}


# TODO remember the newline thing for \n bs
# ['VehicleWithFourSpeedTransmission/Inertia', newline, 'Impeller']
