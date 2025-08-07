# The functions in this file are used to convert data types between Python and MATLAB.
# They handle various MATLAB data types and convert them to appropriate Python types.
# Some conversion are automatic, while others are done manually and exact values are returned
# This is different from json/string based conversion which returns values as strings. useful for viewing data in a human-readable format, such as by the llm. 
# So we will use that one, and this could be perhaps useful elsewhere.

import math
import numpy as np
from typing import Any, Dict, List 
import matlab.engine
import re


def cmd_to_regex(cmd: str) -> re.Pattern:
    """Converts a MATLAB command to a regex pattern."""
    if cmd == "!": # This command is only used at the beginning of a line
        return re.compile(r"^\s*!.*", re.MULTILINE)
    else:
        escaped = re.escape(cmd)
        return re.compile(rf"\b{escaped}\b")


def reshape_recursive(flat_list: List[Any], shape: List[int]) -> List[Any]:
    """
    Reshape a flat list into a nested list with the given shape (e.g., [2, 3] for 2x3).
    Works for string, char, and cell array conversions.
    """

    def _reshape(data, dims):
        if len(dims) == 1:
            return data
        step = math.prod(dims[1:])
        return [_reshape(data[i * step:(i + 1) * step], dims[1:]) for i in range(dims[0])]

    return _reshape(flat_list, shape)


def convert_supported(data: Any):

    # Automatically converted by MATLAB to native Python types
    if isinstance(data, (int, float, bool, str, dict, type(None))):
        return data
    
    # MATLAB numeric arrays. By default Auto-converted to matlab.double objects, not lists
    elif isinstance(data, matlab.double):
        np_array = np.array(data).squeeze()
        if np_array.ndim == 0: return float(np_array)
        return np_array.tolist() 
    
    # MATLAB logical arrays. By default Auto-converted to matlab.logical objects, not lists
    elif isinstance(data, matlab.logical):
        np_array = np.array(data).squeeze()
        if np_array.ndim == 0: return bool(np_array)
        return np_array.tolist()


def flatten_struct_array(array_name: str, eng):
    "Converts a MATLAB struct array to a flattened list of dictionaries."

    # Even 1D Struct arrays cannot be fetched so we need to save the flattened array to workspace as a temporary variable.
    # eval does not allow = assignment, so we use assignin for above-mentioned purpose.
    eng.eval(f"assignin('base', 'temp', {array_name}(:))")
    length = int(eng.length("temp"))
    converted_array = []

    for i in range(length):
        struct = eng.eval(f"temp({i + 1})")
        converted_array.append(struct)

    return converted_array


def convert_non_supported(array_name: str, eng):
    """
    Converts MATLAB data types such as nD cell, string, char and struct arrays.
    These are not automatically converted by MATLAB to native Python types and so can't even be fetched from the workspace.
    This function flattens the array specified by array_name, gets its shape, and returns it as a reshaped nested list. 
    """

    # Get the shape of the array
    shape = eng.eval(f"size({array_name})")
    shape = np.array(shape).astype(int).tolist()

    # Get the type of the array
    type = eng.eval(f"class({array_name})")

    if type == "struct":
        # 1D Struct arrays cannot be fetched so we convert them manually
        flat_array = flatten_struct_array(array_name, eng)  
    elif type in {"cell", "string", "char"}: 
        # Cell, string, and char arrays can be fetched as flat arrays
        flat_array = eng.eval(f"{array_name}(:)")
    elif type in {"double"}:
        # A double array which is non-convertible must be a sparse array 
        full_array = eng.eval(f"full({array_name})") 
        flat_array = convert_supported(full_array)

    # Rebuild the nested structure based on the shape
    return reshape_recursive(flat_array, shape)


def fetch(eng, var: str):
    """
    Attempts to fetch a variable from MATLAB in decreasing order of compatibility:
    1. Direct fetch + supported conversion
    2. Fallback: convert unsupported types
    3. Fallback: fetch using JSON encoding
    Raises a RuntimeError if all attempts fail.
    """
    try_func = [
        lambda: convert_supported(eng.workspace[var]),
        lambda: convert_non_supported(var, eng),
        lambda: eng.eval(f"jsonencode({var}, 'PrettyPrint', true)")
    ]

    for i, attempt in enumerate(try_func, 1):
        try:
            return attempt()
        except Exception as e:
            last_error = e  

    raise RuntimeError(f"Failed to fetch variable '{var}': {last_error}") from last_error


            
    
        
