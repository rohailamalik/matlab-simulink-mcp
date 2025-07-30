from core.server import start_server
from core.state import get_engine
import math
import numpy as np
from typing import Any, Dict, List 

import matlab.engine
start_server()
eng = get_engine()


def convert_to_int(arr):
    return [int(x) for x in arr[0]]



'''
As per https://se.mathworks.com/help/matlab/matlab_external/pass-data-between-matlab-and-python.html, MATLAB automatically converts simple numbers, strings etc so basically anything of size 1x1, automatically to native python type accordingly.
2. for any numerical array, it converts it to a matlab numeric array object e.g. matlab.double etc.
3. for all other arrays, if they are 1D, they are converted to a python type e.g. 1D Char -> str, 1D string -> list of str, 1D Cell array -> list.
4. a dictionary in matlab is converted to a matlab.dictionary object. 
5. some other stuff is converted to pandas (table) or numpy. 
6. multi dimensional non numeric arrays are not converted, nor are struc arrays or sparse arrays.
'''

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

variable = "cell_array"

#shape = np.array(shape).squeeze().astype(int)

#answer = reshape_recursive(flat_array, shape)

#print(answer)


def matlab_to_python(data: Any) -> Any:

    # Automatically converted by MATLAB to native Python types
    if isinstance(data, (int, float, bool, str, type(None))):
        return data
    
    # MATLAB numeric arrays. Auto-converted to matlab.double objects
    elif isinstance(data, matlab.double):
        np_array = np.array(data).squeeze()
        if np_array.ndim == 0: return float(np_array)
        return np_array.tolist() 
    
    # MATLAB logical arrays. Auto-converted to matlab.logical objects
    elif isinstance(data, matlab.logical):
        np_array = np.array(data).squeeze()
        if np_array.ndim == 0: return bool(np_array)
        return np_array.tolist()
    


def convert_sparse_array(array_name: str) -> List[Any]:
    """
    Converts MATLAB sparse arrays to a list or (list of lists).
    """
    full_array = eng.eval(f"full({array_name})") 

    return matlab_to_python(full_array)



    
def flatten_struct_array(array_name: str):
    "Converts a MATLAB struct array to a flattened list of dictionaries."

    eng.eval(f"temp={array_name}(:)") # Even 1D Struct arrays cannot be fetched so we need to save the flattened array to workspace as a temporary variable.
    length = int(eng.eval("length(temp)"))
    converted_array = []

    for i in range(length):
        struct = eng.eval(f"temp({i + 1})")
        converted_array.append(struct)

    return converted_array


def convert_nD_non_num_arrays(array_name: str) -> List[Any]:
    """
    Converts MATLAB data types such as nD cell, string, char and struct arrays.
    These are not automatically converted by MATLAB to native Python types and so can't even be fetched from the workspace.
    This function flattens the array specified by array_name, gets its shape, and returns it as a reshaped nested list. 
    """

    type = eng.eval(f"class({array_name})")

    shape = eng.eval(f"size({array_name})")
    shape = np.array(shape).astype(int).tolist()

    if type == "struct":
        flat_array = flatten_struct_array(array_name)  
    elif type in {"cell", "string", "char"}:  
        flat_array = eng.eval(f"{array_name}(:)")

    

    return reshape_recursive(flat_array, shape)
        




import IPython; IPython.embed()