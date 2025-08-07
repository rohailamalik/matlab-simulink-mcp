import inspect
import sys
from difflib import get_close_matches
from core.state import get_state 
from utils.converters import fetch
from utils.checks import check_file_name, check_code
from utils.utils import get_cwd
from langchain_core.tools import tool, BaseTool



def open_simulink_file(file_name: str, get_content: bool = True, open_in_desktop: bool = False) -> dict:
    """
    Opens a Simulink file and/or returns its content.

    Arguments:
        file_name: Relative path to Simulink file, with .slx extension. 
        get_content: Whether to return textual representation of content in the Simulink file. True by default.
        open_in_desktop: Whether to open the file in desktop. False by default.

    Returns:
        If asked, description of the content inside the Simulink file as a dictionary.
    """

    path = check_file_name(file_name = file_name, extension = ".slx", mode = "read", overwrite = False) 
    
    eng = get_state().eng

    if open_in_desktop:
        try:
            if eng.usejava("desktop"):
                eng.open_system(file_name, nargout=0)
            else:
                raise RuntimeError("MATLAB desktop is not running")
        except Exception as e:
            raise RuntimeError(f"Unexpected error while opening in desktop: {e}")
    else: 
        eng.load_system(file_name)

    if get_content:
        try:
            content = eng.describe_system(file_name) 
            return content
        except Exception as e:
            raise RuntimeError(f"Unexpected error while reading file: {e}")
    else:
        return {"status": f"{file_name} opened successfully in MATLAB desktop."}



def open_matlab_file(file_name: str, get_content: bool = True, open_in_desktop: bool = False) -> str:
    """
    Returns the content of a matlab script and/or opens it in MATLAB desktop.

    Arguments:
        file_name: Relative path to MATLAB script, with .m extension. 
        get_content: Whether to return code inside the script. True by default.
        open_in_desktop: Whether to open the script in MATLAB desktop. False by default.

    Returns:
        If asked, code inside the script as a string.
    """

    path = check_file_name(file_name = file_name, extension = ".m", mode = "read", overwrite = False) 
    
    eng = get_state().eng
    
    if open_in_desktop:
        try:
            if eng.usejava("desktop"):
                eng.edit(file_name, nargout=0)
            else:
                raise RuntimeError("Failed to open in desktop. MATLAB desktop is not running")
        except Exception as e:
            raise RuntimeError(f"Unexpected error while opening in desktop: {e}")

    if get_content: 
        try:
            return eng.fileread(file_name, nargout=1) 
        except Exception as e:
            raise RuntimeError(f"Unexpected error while reading MATLAB file: {e}") 
    else:
        return f"{file_name} opened successfully in MATLAB desktop."



def save_matlab_code(code: str, file_name: str, overwrite: bool = False) -> str:
    """
    Validates and saves MATLAB code to a .m file in the current MATLAB working directory.

    Arguments:
        code: MATLAB code as a string
        file_name: Script name with .m extension. Use relative paths if needed. If a folder in the path does not exist, it will automatically be created.
        overwrite: Whether to overwrite if the file already exists. False by default

    Returns:
        Confirmation message with validation errors if any.
    """

    path = check_file_name(file_name = file_name, extension = ".slx", mode = "read", overwrite = False) 

    eng = get_state().eng

    try:
        path.parent.mkdir(parents=True, exist_ok=True) # Create parent folders in case they don't exist.
        with path.open("w") as f:
            f.write(code)
    except Exception as e:
        raise RuntimeError(f"Error saving the code file {file_name} in current working directory: {e}")
    
    try: 
        issues = eng.validate_code(path)
    except Exception as e:
        raise RuntimeError(f"Error validating the code file {file_name}: {e}") 
    
    if issues:
        path.unlink()
        return f"{file_name} not saved as it failed validation with following errors:\n" + "\n".join(issues)
    
    else:
        return f"Code validated and saved successfully as {file_name}."



def run_matlab_code(code: str) -> str:
    """
    Executes MATLAB code, and returns whatever is displayed in the MATLAB command window, wrapped in a string.

    Parameters:
        code: MATLAB code to run.

    Returns:
        The results printed to MATLAB command window, wrapped in a string.
    """

    eng = get_state().eng
    path = get_cwd(eng) / "canvas.m"   

    try:
        issues = check_code(code)
        if issues:
            raise PermissionError(issues)
    except Exception as e:
        raise RuntimeError(f"Failed to check code for security: {e}")

    try:
        # eval does not support multi-line code, so we write it to the canvas (i.e. a temporary file) and run it through evalc.
        # evalc also returns whatever is printed to command window as a string, so it helps with disp functions etc.
        # TODO: Later it will be replaced by a canvas-based editor.
        with path.open("w") as f:
            f.write(code)

        return eng.evalc("run('{file_path}')", nargout = 1)

    except Exception as e:
        raise RuntimeError(f"MATLAB execution failed: {e}")



def get_variables(variables: list[str], convert = False) -> dict:
    """
    Fetches specified variables from MATLAB workspace.

    Parameters:
        variables: List of variable names to retrieve from workspace.
        convert: Whether to convert the variables to Python types. When False, the values will be returned as string-wrapped MATLAB types. False by default.

    Returns:
        A dictionary of variables and their values.
    """

    eng = get_state().eng

    result = {}

    for var in variables:
        try:
            # Cannot do "if in eng.workspace" since it is not a native Python dict, rather a MATLAB object with some dict-like properties.
            if eng.exist(var, "var") == 1: # This automatically ensures that the var is a proper variable name, without any code injection which could execute through evalc
                if convert:
                    result[var] = fetch(eng, var)
                else:
                    result[var] = eng.evalc(f"{var}", nargout=1)
            else:
                result[var] = "Variable not found in MATLAB workspace."
        
        except Exception as e:
            raise RuntimeError(f"Error fetching variable '{var}': {e}")
        
    return result
    


def get_workspace_summary() -> str:
    """
    Returns a summary of current MATLAB workspace: variable names, sizes, and types.
    """

    eng = get_state().eng

    try:
        info = eng.workspace_summary(nargout=1)
    except Exception as e:
        raise RuntimeError(f"Failed to get workspace summary: {e}")

    return info



def search_library(query) -> dict:
    """
    Searches for a block name in the Simulink block library and returns all matching source paths.

    Parameters:
        query: Name of the block to search for.

    Returns:
        A list of paths of blocks with similar names.
    """

    simlib = get_state().simlib

    n = 2
    cutoff = 0.5

    try:
        block_names = list(simlib.keys())
        matches = get_close_matches(query, block_names, n=n, cutoff=cutoff)
        return {name: simlib[name]['paths'] for name in matches}
    
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
