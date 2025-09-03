import asyncio
import tempfile
import traceback
import matlab.engine
from pathlib import Path
from difflib import SequenceMatcher

from fastmcp.exceptions import ToolError
from fastmcp.utilities.types import Image

from matlab_simulink_mcp.core.state import get_state
from matlab_simulink_mcp.utils.convert import fetch
from matlab_simulink_mcp.utils.security import check_path, check_code
from matlab_simulink_mcp.utils.logger import logger

# TODO: figure out some how to undo stuff in simulink
# TODO: maybe add system prompt as a server resource


def _get_engine() -> matlab.engine.MatlabEngine:
    eng = get_state().eng
    if eng is None:
        raise ToolError("Could not access MATLAB. Run matlab.engine.shareEngine"
        " in MATLAB, and then use access_matlab tool to reconnect.")
    return eng 

def _raise_error(msg: str, exception: Exception):
    tb = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
    main = str(exception).strip().splitlines()[-1]
    logger.error(tb) 
    raise ToolError(f"{msg} {main}")

def _clean_evalc(s: str) -> str:
    "\n".join(line.strip() for line in s.splitlines() if line.strip())

def _get_image(path) -> Image:
    path = Path(str(path))
    data = path.read_bytes()
    path.unlink(missing_ok=True)
    return Image(data=data, format="png")



async def access_matlab() -> str:
    """Connect to MATLAB."""

    try:
        _get_engine()
        return f"Already connected to MATLAB session: {get_state().session}"
    except ToolError:
        try:
            await asyncio.to_thread(get_state().connect_matlab)
            _get_engine()
            return f"Connected to MATLAB session: {get_state().session}"
        except ToolError as e:
            raise
    except Exception as e:
        _raise_error("Failed to connect to MATLAB.", e)
    

async def read_simulink_system(path: str, detail: bool = False, open: bool = False) -> Image | dict:
    """
    View a Simulink system/subsystem as either a PNG image or a detailed dictionary (if detail=True).
    Optionally open the object in MATLAB desktop in addition.
    Detail only recommended when exact port tags or other details are needed, as it can be verbose.
    """

    eng = _get_engine()
    check_path(path)
    
    parent, _, rest = path.partition("/")
    parent = parent.removesuffix(".slx")
    path = parent if not rest else f"{parent}/{rest}"
          
    try:
        if detail:
            return await asyncio.to_thread(eng.describe_system, path, parent, open, nargout=1)
        else:
            ss_path = await asyncio.to_thread(eng.snapshot_system, path, parent, open, nargout=1)
            return _get_image(ss_path)
    except Exception as e:
        _raise_error("Error reading from Simulink.", e)

  
async def read_matlab_code(path: str, open: bool = False) -> str:
    """
    Read the contents of a MATLAB script (.m) or text file.
    Optionally open the file in MATLAB desktop in addition.
    """

    eng = _get_engine()
    check_path(path)
    
    if open:
        try:
            await asyncio.to_thread(eng.edit, path, nargout=0)
        except Exception as e:
            _raise_error(f"Unexpected error while opening in desktop.", e)

    try:
        content = await asyncio.to_thread(eng.fileread, path, nargout=1)
        return content
    except Exception as e:
        _raise_error(f"Unexpected error when reading file.", e)   


async def save_matlab_code(code: str, path: str, overwrite: bool = False) -> str:
    """
    Validate and save MATLAB code to a .m file.
    Optionally overwrite if the file already exists.
    """

    eng = _get_engine()
    check_path(path)
    check_code(code)

    mode = "w" if overwrite else "x"

    try:
        cwd = await asyncio.to_thread(eng.pwd, nargout=1)
        abs_path = Path(str(cwd)) / path
        abs_path.parent.mkdir(parents=True, exist_ok=True) 
        with abs_path.open(mode) as f:
            f.write(code)
    except Exception as e:
        _raise_error(f"Error saving the code.", e)
    
    try: 
        issues = await asyncio.to_thread(eng.validate_code, path)
        if issues:
            return "Code saved but failed validation with errors:\n" + "\n".join(issues)
        else:
            return "Code saved and validated successfully."
    except Exception as e:
        _raise_error(f"Error validating the code.", e) 


async def run_matlab_code(code: str, get_images: bool = False) -> tuple[str, *tuple[Image, ...]]:
    """
    Execute MATLAB code and return command window output as a string and images (if asked).
    Interact programatically with Simulink if the action is not covered by a tool.
    """

    # TODO: Later implement a canvas based editor
    eng = _get_engine()
    check_code(code)

    imgs: list[Image] = []

    try: 
        if get_images:
            await asyncio.to_thread(eng.close, 'all', nargout=0)
        with tempfile.NamedTemporaryFile("w", suffix=".m", delete=True) as f:
            f.write(code)
            f.flush()
            abs_path = Path(f.name)
            text = _clean_evalc(await asyncio.to_thread(eng.evalc, f"run('{abs_path}')", nargout=1))
        await asyncio.to_thread(eng.format_system, nargout=0)
    except Exception as e:
        _raise_error("Unexpected error while running MATLAB code.", e)
    
    if get_images:
        try:
            img_paths = await asyncio.to_thread(eng.get_images, nargout=1)
            imgs = [_get_image(p) for p in img_paths]
        except Exception as e:
            _raise_error("Error fetching images from MATLAB.", e)
    
    return (text, *imgs) 
            
    

'''
async def get_variables(variables: list[str], convert: bool = False) -> dict:
    """
    Fetch variables from the MATLAB workspace.
    Optionally return converted Python types instead of string representations.
    """

    eng = _get_engine()
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
                    content = await asyncio.to_thread(eng.evalc, f"disp({var})", nargout=1)
                    answer[var] = _clean_evalc(content)
            else:
                answer[var] = "Not in workspace"

        except Exception:
            _raise_error(f"Error getting variable '{var}'.") 

    return answer   
'''


def search_library(query: str) -> list:
    """
    Search the Simulink block library for a block name and return matching source paths.
    """

    try: 
        simlib = get_state().simlib
        candidates = [(name, path) for name, entry in simlib.items() for path in entry["paths"]]
        ranked = sorted(
            candidates,
            key=lambda item: SequenceMatcher(None, query.lower(), item[0].lower()).ratio(),
            reverse=True
        )
        return [path for _, path in ranked[:3]]
    
    except Exception as e:
       _raise_error(f"Error searching Simulink library.")
    
# TODO remember the newline thing for \n 
# ['VehicleWithFourSpeedTransmission/Inertia', newline, 'Impeller']


