import os
import inspect
import sys
import tempfile
from difflib import get_close_matches
from core.state import get_engine, get_sl_lib_data 
from utils.converters import fetch, batch_fetch
from langchain_core.tools import tool, BaseTool



def open_simulink_file(file_name: str, get_content: bool = True, open_in_desktop: bool = False) -> dict | Exception:
    """
    Opens a Simulink file and/or returns its content.

    Parameters:
        file_name: Simulink file name with .slx extension
        get_content: whether to return the content/system in the Simulink file. True by default.
        open_in_desktop: whether to open the Simulink file in MATLAB desktop. False by default.

    Returns:
        If asked, description of the system inside the Simulink file as a dictionary.
    """

    eng = get_engine()

    if eng is None:
        return RuntimeError("MATLAB engine is not available.")

    if not file_name.endswith(".slx"):
        return ValueError("Only .slx files are supported.")

    if eng.exist(file_name, "file") == 0:
        return FileNotFoundError(f"'{file_name}' not found in MATLAB's current working directory.")

    eng.load_system(file_name)

    if open_in_desktop:
        try:
            if eng.usejava("desktop"):
                eng.open_system(file_name, nargout=0)
            else:
                return RuntimeError("Failed to open in desktop. MATLAB desktop is not running")
        except Exception as e:
            return RuntimeError(f"Unexpected error while opening Simulink file in desktop: {e}")

    if get_content:
        try:
            content = eng.describe_system(file_name) 
            return content
        except Exception as e:
            return RuntimeError(f"Unexpected error while reading Simulink file: {e}")

    else:
        return f"{file_name} opened successfully in MATLAB desktop."



def open_matlab_file(file_name: str, get_content: bool = True, open_in_desktop: bool = False) -> str | Exception:
    """
    Opens a MATLAB script and/or returns its content.

    Parameters:
        file_name: script file name with .m extension
        get_content: whether to return the code in the script file. True by default
        open_in_desktop: whether to open the script in MATLAB desktop. False by default

    Returns:
        If asked, code inside the script as a string.
    """

    eng = get_engine()

    if eng is None:
        return RuntimeError("MATLAB engine is not available.")

    if not file_name.endswith(".m"):
        return ValueError("Only .m files can be opened.")
    
    if eng.exist(file_name, "file") == 0:
        return FileNotFoundError(f"'{file_name}' not found in MATLAB's current working directory.")
    
    if open_in_desktop:
        try:
            if eng.usejava("desktop"):
                eng.edit(file_name, nargout=0)
            else:
                return RuntimeError("Failed to open in desktop.")
        except Exception as e:
            return RuntimeError(f"Unexpected error while opening MATLAB file in desktop: {e}")

    if get_content: 
        try:
            content = eng.fileread(file_name, nargout=1)
        except Exception as e:
            return RuntimeError(f"Unexpected error while reading MATLAB file: {e}") 
    else:
        return f"{file_name} opened successfully in MATLAB desktop."


def save_matlab_code(code: str, file_name: str, overwrite: bool = False) -> str | Exception:
    """
    Validates and saves MATLAB code to a .m file in the current MATLAB working directory.

    Parameters:
        code: MATLAB code as a string
        file_name: script name with .m extension
        overwrite: whether to overwrite if the file already exists. False by default

    Returns:
        Confirmation message if saved. Errors if validation fails.
    """

    eng = get_engine()

    if eng is None:
        return RuntimeError("MATLAB engine is not available.")

    if not file_name.endswith(".m"):
        return ValueError("Please save as a .m file.")
    
    if not overwrite and eng.exist(file_name, "file") == 2: 
        return FileNotFoundError(f"'{file_name}' already exists in MATLAB's current working directory.")

    cwd = eng.pwd() 
    file_path = os.path.join(cwd, file_name)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
    except Exception as e:
        return RuntimeError(f"Error saving the code file {file_name} in directory {cwd}: {e}")
    
    try: 
        issues = eng.validate_code(file_path)
    except Exception as e:
            return RuntimeError(f"Error validating the code file {file_name}: {e}") 
    finally:
        if issues:
            os.remove(file_path)
            return ValueError(f"MATLAB syntax issues found in '{file_name}':\n" + "\n".join(issues)
        )

    return f"Code validated and saved successfully as {file_name}."


def run_matlab_code(code: str, variables: list[str] = None, convert= False) -> dict | str | Exception:
    """
    Executes MATLAB code, and retrieves values of specified variables from workspace.

    Parameters:
        code: MATLAB code to run.
        variables: list of variable names to retrieve from current MATLAB workspace after the code is ran. None by default. 
        convert: whether to convert the variables to Python types. When False, the values will be returned as string-wrapped MATLAB types. False by default.

    Returns:
        If asked, a dictionary of asked variables and their values.
    """

    eng = get_engine()

    if eng is None:
        return RuntimeError("MATLAB engine is not available.")

    temp = False

    try:
        # eval does not support multi-line code, so we write it to a temporary file, run it and then delete it.
        # TODO: Later it will be replaced by a canvas-based editor.
        with tempfile.NamedTemporaryFile(mode="w", suffix=".m", delete=False) as f:
            f.write(code)
            temp_path = f.name
            temp = True

        eng.run(temp_path, nargout=0)

    except Exception as e:
        return RuntimeError(f"MATLAB execution failed: {e}")
    
    finally:
        # Whatever happens, delete the temporary file post execution.
        # temp ensures that the file is deleted only if it was created.
        # This prevents deletion of a file with same/ similar name in the current directory.
        if temp and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e: # TODO replace this with debugging logger
                raise RuntimeError(f"Warning: Failed to delete temporary file {temp_path}: {e}")

    if variables:
        return batch_fetch(eng, variables, convert=convert)
    else:
        return "Code executed successfully."


def get_variables(variables: list[str], convert = False) -> dict | Exception:
    """
    Fetches specified variables from MATLAB workspace.

    Parameters:
        variables: list of variable names to retrieve from current MATLAB workspace after the code is ran.
        convert: whether to convert the variables to Python types. When False, the values will be returned as string-wrapped MATLAB types. False by default.

    Returns:
        A dictionary of asked variables and their values.
    """

    eng = get_engine()

    if eng is None:
        return RuntimeError("MATLAB engine is not available.")

    return batch_fetch(eng, variables, convert=convert)


def get_workspace_summary() -> str | Exception:
    """
    Returns a summary of current MATLAB workspace: variable names, sizes, and types.
    """

    eng = get_engine()

    if eng is None:
        return RuntimeError("MATLAB engine is not available.")

    try:
        info = eng.workspace_summary(nargout=1)
    except Exception as e:
        return RuntimeError(f"Failed to get workspace summary: {e}")

    return info


def search_library(query) -> dict:
    """
    Searches for a block name in the Simulink block library and returns all matching source paths.

    Parameters:
        query: Name of the block to search for.

    Returns:
        A list of paths of blocks with similar names.
    """

    sl_lib_data = get_sl_lib_data()
    if sl_lib_data is None:
        return RuntimeError("Simulink library data not found.")

    n = 2
    cutoff = 0.5

    try:
        block_names = list(sl_lib_data.keys())
        matches = get_close_matches(query, block_names, n=n, cutoff=cutoff)
        return {name: sl_lib_data[name]['paths'] for name in matches}
    except Exception as e:
        return RuntimeError(f"Error searching Simulink library: {e}")


# Collect all the tools 
_current_module = sys.modules[__name__]

tools = [
    obj
    for name, obj in inspect.getmembers(_current_module)
    if isinstance(obj, BaseTool)
]

# TODO remember the newline thing for \n bs
# ['VehicleWithFourSpeedTransmission/Inertia', newline, 'Impeller']
